import base64
import mimetypes
import os
import re
import struct
import uuid
from google import genai
from google.genai import types
from config import GOOGLE_API_KEY, TMP_DIR
from logger import get_logger

logger = get_logger(__name__)


def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    """Parses bits per sample and rate from an audio MIME type string.

    Assumes bits per sample is encoded like "L16" and rate as "rate=xxxxx".

    Args:
        mime_type: The audio MIME type string (e.g., "audio/L16;rate=24000").

    Returns:
        A dictionary with "bits_per_sample" and "rate" keys. Values will be
        integers if found, otherwise None.
    """
    bits_per_sample = 16
    rate = 24000

    # Extract rate from parameters
    parts = mime_type.split(";")
    for param in parts:  # Skip the main type part
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate_str = param.split("=", 1)[1]
                rate = int(rate_str)
            except (ValueError, IndexError):
                # Handle cases like "rate=" with no value or non-integer value
                pass  # Keep rate as default
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass  # Keep bits_per_sample as default if conversion fails

    return {"bits_per_sample": bits_per_sample, "rate": rate}


def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    """Generates a WAV file header for the given audio data and parameters.

    Args:
        audio_data: The raw audio data as a bytes object.
        mime_type: Mime type of the audio data.

    Returns:
        A bytes object representing the WAV file header.
    """
    if mime_type and ("wav" in mime_type or "wave" in mime_type):
        return audio_data
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size

    # http://soundfile.sapp.org/doc/WaveFormat/

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",          # ChunkID
        chunk_size,       # ChunkSize (total file size - 8 bytes)
        b"WAVE",          # Format
        b"fmt ",          # Subchunk1ID
        16,               # Subchunk1Size (16 for PCM)
        1,                # AudioFormat (1 for PCM)
        num_channels,     # NumChannels
        sample_rate,      # SampleRate
        byte_rate,        # ByteRate
        block_align,      # BlockAlign
        bits_per_sample,  # BitsPerSample
        b"data",          # Subchunk2ID
        data_size         # Subchunk2Size (size of audio data)
    )
    return header + audio_data


def save_binary_file(file_path, data):
    """Save binary data to file."""
    logger.debug(f"Saving {len(data)} bytes to {file_path}")
    with open(file_path, "wb") as f:
        f.write(data)
    logger.info(f"Saved file: {file_path} ({len(data)} bytes)")


def split_script_into_segments(script, max_lines=15):
    """Split script into smaller segments."""
    logger.info(f"Splitting script (length: {len(script)})")
    lines = [l.strip() for l in script.split('\n') if l.strip()]
    logger.debug(f"Script has {len(lines)} lines")

    segments = []
    current_segment = []
    for line in lines:
        current_segment.append(line)
        if len(current_segment) >= max_lines:
            segments.append('\n'.join(current_segment))
            logger.debug(
                f"Created segment {len(segments)} with {len(current_segment)} lines")
            current_segment = []
    if current_segment:
        segments.append('\n'.join(current_segment))
        logger.debug(
            f"Created final segment {len(segments)} with {len(current_segment)} lines")

    logger.info(f"Split into {len(segments)} segments")
    return segments


def generate_podcast_segment(client, segment, output_prefix, segment_idx):
    """Generate audio for a single script segment."""
    logger.info(f"Generating audio for segment {segment_idx}")
    logger.debug(f"Segment content: {segment[:200]}...")

    model = "gemini-2.5-flash-preview-tts"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=segment),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=[
            "audio",
        ],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 1",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Zephyr"
                            )
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 2",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Puck"
                            )
                        ),
                    ),
                ]
            ),
        ),
    )

    saved_files = []
    file_index = 0

    logger.debug(f"Starting TTS stream for segment {segment_idx}")
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            logger.debug("Received empty chunk, skipping")
            continue
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            logger.debug(
                f"Received audio chunk: {len(data_buffer)} bytes, mime: {inline_data.mime_type}")

            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            if file_extension is None:
                logger.debug("No extension found, converting to WAV")
                file_extension = ".wav"
                data_buffer = convert_to_wav(
                    inline_data.data, inline_data.mime_type)

            file_name = f"{output_prefix}_seg{segment_idx}_{file_index}{file_extension}"
            file_path = file_name  # output_prefix already contains full path
            save_binary_file(file_path, data_buffer)
            saved_files.append(file_path)
            logger.info(
                f"Saved audio file {file_index} for segment {segment_idx}: {file_name}")
            file_index += 1
        else:
            if hasattr(chunk, 'text'):
                logger.debug(f"Received text chunk: {chunk.text}")

    logger.info(
        f"Completed segment {segment_idx}, generated {len(saved_files)} audio files")
    return saved_files


def generate_podcast(script, output_prefix="podcast"):
    """Generate audio by splitting script into segments."""
    logger.info(f"Starting podcast generation with prefix: {output_prefix}")

    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY not found")
        raise RuntimeError("Missing GOOGLE_API_KEY environment variable")

    logger.debug("Initializing Gemini client")
    client = genai.Client(api_key=GOOGLE_API_KEY)

    segments = split_script_into_segments(script)
    logger.info(f"Processing {len(segments)} segments")

    all_files = []
    for idx, segment in enumerate(segments):
        logger.info(f"Processing segment {idx+1}/{len(segments)}")
        try:
            files = generate_podcast_segment(
                client, segment, output_prefix, idx)
            all_files.extend(files)
            logger.info(
                f"Segment {idx} complete: generated {len(files)} files")
        except Exception as e:
            logger.exception(f"Failed to generate segment {idx}: {str(e)}")
            raise

    logger.info(
        f"Podcast generation complete: {len(all_files)} total audio files")
    return all_files

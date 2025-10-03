import os
import wave
import glob
from logger import get_logger

logger = get_logger(__name__)

def concatenate_audio_files(audio_files, output_path):
    """Concatenate multiple WAV files into one."""
    logger.info(f"Concatenating {len(audio_files)} audio files")
    
    if not audio_files:
        raise ValueError("No audio files to concatenate")
    
    # Sort files by segment number
    sorted_files = sorted(audio_files)
    
    # Read first file to get parameters
    with wave.open(sorted_files[0], 'rb') as first_wav:
        params = first_wav.getparams()
    
    # Create output file
    with wave.open(output_path, 'wb') as output_wav:
        output_wav.setparams(params)
        
        # Append each file
        for audio_file in sorted_files:
            with wave.open(audio_file, 'rb') as wav:
                output_wav.writeframes(wav.readframes(wav.getnframes()))
    
    logger.info(f"Created concatenated audio: {output_path}")
    return output_path

def get_audio_duration(audio_file):
    """Get duration of WAV file in seconds."""
    with wave.open(audio_file, 'rb') as wav:
        frames = wav.getnframes()
        rate = wav.getframerate()
        duration = frames / float(rate)
    return duration

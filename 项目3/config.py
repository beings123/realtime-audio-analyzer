import os

# Input audio file settings
INPUT_AUDIO_FILENAME = "Decade_mono_16k.wav"
INPUT_AUDIO_PATH = os.path.join("data", INPUT_AUDIO_FILENAME)

# Output directories
VAD_SEGMENTS_DIR = os.path.join("data", "vad_segments")
FEATURES_DIR = os.path.join("data", "features")

# Audio recording settings (if microphone input were available)
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "recorded_audio.wav"

# VAD settings
VAD_AGGRESSIVENESS = 3 # 0-3, 3 is most aggressive

# Feature extraction settings
MEL_N_MELS = 128



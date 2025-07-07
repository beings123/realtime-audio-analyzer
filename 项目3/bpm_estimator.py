import librosa
import os
from config import INPUT_AUDIO_PATH, FEATURES_DIR
import pyaudio

def estimate_bpm(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    tempo = librosa.beat.tempo(y=y, sr=sr)
    return tempo[0] # Access the scalar value from the array

def estimate_bpm_from_mic(duration=10, segment_duration=2):
    """
    实时录音并每2秒估算一次BPM。
    duration: 总录音时长（秒）
    segment_duration: 每段BPM估算时长（秒）
    """
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print(f"* 正在录音 {duration} 秒，每{segment_duration}秒输出一次BPM...")
    frames = []
    segment_frames = int(RATE * segment_duration)
    total_frames = int(RATE * duration)
    for i in range(0, total_frames, segment_frames):
        segment = b''
        frames_needed = segment_frames // CHUNK
        for _ in range(frames_needed):
            data = stream.read(CHUNK)
            segment += data
        # 转为numpy数组
        import numpy as np
        audio_np = np.frombuffer(segment, dtype=np.int16).astype(float) / 32768.0
        # BPM估算
        import librosa
        bpm = librosa.beat.tempo(y=audio_np, sr=RATE)[0]
        print(f"{i//segment_frames+1}: BPM = {bpm:.2f}")
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("* 录音结束")

if __name__ == "__main__":
    input_audio_path = INPUT_AUDIO_PATH
    bpm = estimate_bpm(input_audio_path)
    print(f"Estimated BPM: {bpm:.2f}")

    # Optionally, save the BPM to a file
    output_dir = FEATURES_DIR
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "estimated_bpm.txt"), "w") as f:
        f.write(f"Estimated BPM: {bpm:.2f}")
    print(f"Estimated BPM saved to {os.path.join(output_dir, 'estimated_bpm.txt')}")



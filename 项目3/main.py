import numpy as np

def realtime_bpm_detection(duration=400, segment_duration=2):
    """
    实时录音并每2秒估算一次BPM。
    duration: 总录音时长（秒）
    segment_duration: 每段BPM估算时长（秒）
    """
    import pyaudio
    import librosa
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
    segment_frames = int(RATE * segment_duration)
    total_frames = int(RATE * duration)
    for i in range(0, total_frames, segment_frames):
        segment = b''
        frames_needed = segment_frames // CHUNK
        for _ in range(frames_needed):
            data = stream.read(CHUNK)
            segment += data
        audio_np = np.frombuffer(segment, dtype=np.int16).astype(float) / 32768.0
        bpm = librosa.beat.tempo(y=audio_np, sr=RATE)[0]
        print(int(round(bpm)))
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("* 录音结束")

if __name__ == "__main__":
    # 默认录音60秒，每2秒输出一次BPM
    realtime_bpm_detection(duration=60, segment_duration=2)



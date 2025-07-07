
import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

def record_audio(filename=WAVE_OUTPUT_FILENAME, record_seconds=RECORD_SECONDS, device_index=None):
    """
    录制音频并保存为WAV文件
    
    参数:
        filename (str): 输出文件名
        record_seconds (int): 录制时长（秒）
        device_index (int, optional): 输入设备索引，None表示使用默认设备
    
    返回:
        bool: 录制是否成功
    """
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=CHUNK)

        print("* recording")
        frames = []

        for i in range(0, int(RATE / CHUNK * record_seconds)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except IOError as e:
                # 处理录音过程中可能出现的IO错误
                print(f"Warning: {e}")
                continue

        print("* done recording")
        
        # 确保流被正确关闭
        stream.stop_stream()
        stream.close()
        
        # 保存录音文件
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            return True
        except Exception as e:
            print(f"Error saving audio file: {e}")
            return False
            
    except Exception as e:
        print(f"Error recording audio: {e}")
        return False
    finally:
        # 确保PyAudio实例被正确终止
        p.terminate()

if __name__ == "__main__":
    record_audio("audio_bpm_detector/data/recorded_audio.wav")



import collections
import webrtcvad
import wave
import os
from config import VAD_AGGRESSIVENESS, VAD_SEGMENTS_DIR, INPUT_AUDIO_PATH

def read_wave(path):
    """Reads a .wav file. Returns (samp_rate, audio_data)."""
    with wave.open(path, 'rb') as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return sample_rate, pcm_data

def write_wave(path, audio, sample_rate):
    """Writes a .wav file. Returns nothing."""
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)

def vad_segment_audio(path, aggressiveness=VAD_AGGRESSIVENESS):
    """Segments audio using WebRTC VAD.

    Args:
        path: Input .wav file path.
        aggressiveness: VAD aggressiveness mode (0-3).

    Returns:
        A list of (start_time, end_time, audio_segment) tuples.
    """
    sample_rate, audio = read_wave(path)
    vad = webrtcvad.Vad(aggressiveness)

    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = vad_collector(sample_rate, 30, 300, vad, frames)

    output_segments = []
    for i, segment in enumerate(segments):
        start_time = segment['start'] / 1000.0
        end_time = (segment['start'] + segment['duration']) / 1000.0
        output_segments.append((start_time, end_time, segment['pcm_data']))
    return output_segments

def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM data.

    Args:
        frame_duration_ms: The duration of a frame in milliseconds.
        audio: The PCM audio data.
        sample_rate: The sample rate of the audio.

    Yields:
        Frames of the audio.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    while offset + n < len(audio):
        yield audio[offset:offset + n]
        offset += n

def vad_collector(sample_rate, frame_duration_ms, 
                  padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.

    Args:
        sample_rate: The sample rate, in Hz.
        frame_duration_ms: The frame duration in milliseconds.
        padding_duration_ms: The amount of non-voiced audio to keep at the start
                              and end of voiced segments.
        vad: An instance of webrtcvad.Vad.
        frames: A generator of audio frames.

    Returns:
        A generator of voiced audio segments.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame, sample_rate)

        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                triggered = False
                yield {'start': (len(voiced_frames) - len(ring_buffer)) * frame_duration_ms,
                       'duration': len(voiced_frames) * frame_duration_ms,
                       'pcm_data': b''.join(voiced_frames)}
                ring_buffer.clear()
                voiced_frames = []

    if voiced_frames:
        yield {'start': (len(voiced_frames) - len(ring_buffer)) * frame_duration_ms,
               'duration': len(voiced_frames) * frame_duration_ms,
               'pcm_data': b''.join(voiced_frames)}

if __name__ == "__main__":
    input_audio_path = INPUT_AUDIO_PATH
    output_dir = VAD_SEGMENTS_DIR
    os.makedirs(output_dir, exist_ok=True)

    segments = vad_segment_audio(input_audio_path)
    for i, (start, end, audio_segment) in enumerate(segments):
        segment_filename = os.path.join(output_dir, f"segment_{i:03d}_{start:.2f}-{end:.2f}.wav")
        write_wave(segment_filename, audio_segment, read_wave(input_audio_path)[0])
        print(f"Saved segment {i} to {segment_filename}")



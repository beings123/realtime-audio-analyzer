
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os
from config import INPUT_AUDIO_PATH, FEATURES_DIR, MEL_N_MELS

def extract_features(audio_path, output_dir):
    y, sr = librosa.load(audio_path, sr=None)

    # STFT
    D = librosa.stft(y)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar()
    plt.title('STFT Spectrogram')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'stft_spectrogram.png'))
    plt.close()
    np.save(os.path.join(output_dir, 'stft_features.npy'), S_db)

    # Mel-spectrogram
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=MEL_N_MELS)
    S_db_mel = librosa.amplitude_to_db(S, ref=np.max)
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(S_db_mel, sr=sr, x_axis='time', y_axis='mel')
    plt.colorbar(format='%2.0f dB')
    plt.title('Mel-frequency Spectrogram')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mel_spectrogram.png'))
    plt.close()
    np.save(os.path.join(output_dir, 'mel_features.npy'), S_db_mel)

    print(f"Features extracted and saved to {output_dir}")

if __name__ == "__main__":
    input_audio_path = INPUT_AUDIO_PATH
    output_dir = FEATURES_DIR
    os.makedirs(output_dir, exist_ok=True)
    extract_features(input_audio_path, output_dir)



import wave
import contextlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import sys
import subprocess
import glob
import hashlib
import threading
import pickle
import time

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# Directory for caching waveform data
CACHE_DIR = ".waveform_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def file_hash(filepath):
    """Generate a hash for the file based on its contents and modification time."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
        # Include modification time in hash to invalidate cache if file changes
        mtime = os.path.getmtime(filepath)
        h.update(str(mtime).encode())
    except Exception as e:
        print(f"Error hashing file: {e}")
        return None
    return h.hexdigest()

def cache_path_for_file(filepath):
    """Return the cache file path for a given audio file."""
    h = file_hash(filepath)
    if h is None:
        return None
    return os.path.join(CACHE_DIR, f"{h}.pkl")

def convert_to_wav_ffmpeg(input_path, output_path):
    """Convert any audio file to WAV format using ffmpeg."""
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, "-acodec", "pcm_s16le", "-ar", "44100", output_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("❌ ffmpeg is not installed or not found in PATH. Please install ffmpeg to use this script.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg failed to convert the file. Error output:")
        print(e.stderr.decode())
        sys.exit(1)

def suggest_audio_files():
    """Suggest audio files in the current directory for user convenience."""
    exts = ["*.mp3", "*.wav", "*.flac", "*.ogg", "*.m4a", "*.aac"]
    files = []
    for ext in exts:
        files.extend(glob.glob(ext))
    return files

def smooth_gradient_colors(n, cmap_name="turbo"):
    """Generate a smooth color gradient for the waveform plot."""
    cmap = plt.get_cmap(cmap_name)
    return [cmap(i / (n-1)) for i in range(n)]

def process_audio_data(wav_path, tqdm_enabled=True):
    """Read and process audio data from a WAV file, returning normalized waveform and metadata."""
    with contextlib.closing(wave.open(wav_path, 'rb')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        channels = f.getnchannels()
        sampwidth = f.getsampwidth()

        chunk_size = 44100 * channels
        audio_data = bytearray()
        if tqdm_enabled and tqdm is not None:
            print("Reading audio data...")
            with tqdm(total=frames, unit="frames", ncols=70, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
                frames_read = 0
                while frames_read < frames:
                    to_read = min(chunk_size, frames - frames_read)
                    chunk = f.readframes(to_read)
                    audio_data.extend(chunk)
                    frames_read += to_read
                    pbar.update(to_read)
        else:
            audio_data = f.readframes(frames)

    # Determine numpy dtype based on sample width
    if sampwidth == 2:
        dtype = np.int16
    elif sampwidth == 4:
        dtype = np.int32
    elif sampwidth == 1:
        dtype = np.uint8
    else:
        print(f"Unsupported sample width: {sampwidth} bytes")
        sys.exit(1)

    audio_array = np.frombuffer(audio_data, dtype=dtype)

    # Handle multi-channel (stereo) audio by averaging channels
    if channels > 1:
        try:
            audio_array = audio_array.reshape(-1, channels)
            if tqdm_enabled and tqdm is not None:
                print("Averaging stereo channels...")
                audio_array = np.array([row.mean() for row in tqdm(audio_array, desc="Averaging", ncols=70)], dtype=np.float32)
            else:
                audio_array = audio_array.mean(axis=1)
        except Exception as e:
            print(f"Error processing stereo audio: {e}")
            sys.exit(1)

    # Normalize audio to [-1, 1]
    audio_array = audio_array.astype(np.float32)
    max_val = np.max(np.abs(audio_array))
    if max_val > 0:
        audio_array /= max_val

    return audio_array, duration, frames

def downsample_audio(audio_array, duration, frames, max_points=100000):
    """Downsample the audio array for efficient SVG rendering."""
    if len(audio_array) > max_points:
        factor = len(audio_array) // max_points
        audio_array = audio_array[:factor*max_points].reshape(-1, factor).mean(axis=1)
        duration = duration * (len(audio_array) / frames)
    time_axis = np.linspace(0, duration, num=len(audio_array))
    return audio_array, time_axis

def plot_waveform(audio_array, time_axis, output_image_path, show_progress=True):
    """
    Plot the waveform as a smooth, colorful SVG image with enhanced depth of field and detail.

    This function creates a visually rich waveform by layering multiple lines with varying
    widths, opacities, and subtle blurring to simulate depth and glow. The main waveform
    is rendered with a vibrant color gradient, while additional layers beneath and above
    the main line add a sense of dimensionality and realism.
    """
    plt.figure(figsize=(20, 6), facecolor='black', dpi=300)
    ax = plt.gca()
    ax.set_facecolor('black')
    plt.axis('off')

    N = len(audio_array) - 1
    colors = smooth_gradient_colors(N, cmap_name="turbo")
    linewidth = 2.8

    # --- Depth of Field and Detail Enhancements ---

    # 1. Subtle shadow layer (simulates depth below the waveform)
    def plot_shadow(start, end):
        shadow_offset = 0.012 * (np.max(audio_array) - np.min(audio_array))
        for i in range(start, end):
            plt.plot(
                time_axis[i:i+2],
                audio_array[i:i+2] - shadow_offset,
                color=(0, 0, 0, 0.18),
                linewidth=linewidth * 4.5,
                solid_capstyle='round',
                zorder=1
            )

    # 2. Soft glow layers (multiple, for a luminous effect)
    def plot_glow_layers(start, end):
        for glow in range(1, 7):
            alpha = 0.06 * (7 - glow)
            lw = linewidth + glow * 3.0
            for i in range(start, end):
                plt.plot(
                    time_axis[i:i+2],
                    audio_array[i:i+2],
                    color=colors[i][:3] + (alpha,),
                    linewidth=lw,
                    solid_capstyle='round',
                    zorder=2
                )

    # 3. Highlight layer (simulates light reflection on the waveform)
    def plot_highlight(start, end):
        highlight_offset = 0.008 * (np.max(audio_array) - np.min(audio_array))
        for i in range(start, end):
            plt.plot(
                time_axis[i:i+2],
                audio_array[i:i+2] + highlight_offset,
                color=(1, 1, 1, 0.10),
                linewidth=linewidth * 1.7,
                solid_capstyle='round',
                zorder=4
            )

    # 4. Main waveform line (sharp, colorful, on top)
    def plot_segments(start, end):
        for i in range(start, end):
            plt.plot(
                time_axis[i:i+2],
                audio_array[i:i+2],
                color=colors[i],
                linewidth=linewidth,
                solid_capstyle='round',
                zorder=5
            )

    # 5. Fine detail: subtle inner edge (adds crispness)
    def plot_inner_edge(start, end):
        for i in range(start, end):
            plt.plot(
                time_axis[i:i+2],
                audio_array[i:i+2],
                color=(1, 1, 1, 0.07),
                linewidth=linewidth * 0.7,
                solid_capstyle='round',
                zorder=6
            )

    # --- Multithreaded plotting for large waveforms (main line only) ---
    num_threads = 4 if N > 4000 else 1
    threads = []
    chunk_size = N // num_threads

    # Plot shadow and glow layers (single-threaded for matplotlib safety)
    plot_shadow(0, N)
    plot_glow_layers(0, N)

    # Plot highlight and inner edge (single-threaded)
    plot_highlight(0, N)
    plot_inner_edge(0, N)

    # Plot main waveform (multi-threaded for speed)
    for t in range(num_threads):
        start = t * chunk_size
        end = N if t == num_threads - 1 else (t + 1) * chunk_size
        threads.append(threading.Thread(target=plot_segments, args=(start, end)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    plt.margins(0.01, 0.18)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    print("Saving beautiful, detailed SVG waveform image with depth of field...")
    plt.savefig(output_image_path, format="svg", bbox_inches='tight', pad_inches=0, facecolor='black')
    plt.close()

def main():
    print("Looking for audio files in the current directory...")
    files = suggest_audio_files()
    if files:
        print("Found the following audio files:")
        for idx, f in enumerate(files, 1):
            print(f"  {idx}. {f}")
        print("You can copy-paste or type the path to one of these files.")
    else:
        print("No audio files found in the current directory. Please enter the path to your audio file.")

    try:
        input_path = input("Enter the path to your audio file (MP3, WAV, etc.): ").strip()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)

    if not os.path.isfile(input_path):
        print(f"File '{input_path}' does not exist.")
        sys.exit(1)

    output_image_path = "waveform.svg"
    wav_path = "temp_waveform.wav"
    cache_file = cache_path_for_file(input_path)
    audio_array = None
    duration = None
    frames = None

    try:
        # Check cache for precomputed waveform data
        cache_hit = False
        if cache_file and os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    cache_data = pickle.load(f)
                audio_array = cache_data["audio_array"]
                duration = cache_data["duration"]
                frames = cache_data["frames"]
                print(f"✅ Loaded waveform data from cache ({cache_file})")
                cache_hit = True
            except Exception as e:
                print(f"⚠️  Failed to load cache: {e}. Will regenerate waveform.")

        if not cache_hit:
            # Convert to WAV if necessary
            if input_path.lower().endswith('.wav'):
                wav_path = input_path
            else:
                print("Converting to WAV...")
                convert_to_wav_ffmpeg(input_path, wav_path)

            # Process audio data (with progress bar if tqdm is available)
            audio_array, duration, frames = process_audio_data(wav_path, tqdm_enabled=True)

            # Save to cache for future runs
            if cache_file:
                try:
                    with open(cache_file, "wb") as f:
                        pickle.dump({
                            "audio_array": audio_array,
                            "duration": duration,
                            "frames": frames
                        }, f)
                    print(f"✅ Cached waveform data to {cache_file}")
                except Exception as e:
                    print(f"⚠️  Failed to write cache: {e}")

        # Downsample for SVG scalability and performance
        audio_array, time_axis = downsample_audio(audio_array, duration, frames, max_points=3000)

        # Plot and save the waveform SVG
        plot_waveform(audio_array, time_axis, output_image_path, show_progress=True)

        print(f"🌈✨ Waveform SVG image saved as '{output_image_path}'")
    finally:
        # Clean up temporary WAV file if it was created
        if wav_path != input_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass

if __name__ == "__main__":
    if tqdm is None:
        print("ℹ️  For a beautiful progress bar, install tqdm: pip install tqdm")
    main()

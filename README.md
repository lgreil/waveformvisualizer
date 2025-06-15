# Music Waveform Visualizer 🎵

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/music-visualizer.svg)](https://badge.fury.io/py/music-visualizer)
[![Built with AI](https://img.shields.io/badge/Built%20with-AI-blueviolet)](https://github.com/features/copilot)

A beautiful and efficient audio waveform visualizer that creates stunning SVG visualizations of your music files. The visualizer supports various audio formats and creates high-quality, colorful waveform images with depth and detail.

![Example Waveform](https://raw.githubusercontent.com/yourusername/musicvisualizer/main/examples/example.png)

## ✨ Features

- 🎨 Creates beautiful SVG visualizations with depth of field and color gradients
- 🎵 Supports multiple audio formats (MP3, WAV, FLAC, OGG, M4A, AAC)
- ⚡ Efficient processing with caching system
- 🔄 Multi-threaded rendering for large files
- 📊 Progress bars for long operations
- 🔄 Automatic format conversion using ffmpeg

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- ffmpeg (for audio format conversion)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/musicvisualizer.git
   cd musicvisualizer
   ```

2. Install ffmpeg:
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg` or equivalent for your distribution

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Place your audio file in the same directory as the script
2. Run the script:
   ```bash
   python generate_waveform.py your_audio_file.mp3
   ```
3. The script will create an SVG file with the same name as your audio file

### Command Line Arguments

- Input file: The audio file to process (required)
- The script will automatically detect audio files in the current directory if no file is specified

## 📦 Building an Executable

To create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Create the executable:
   ```bash
   pyinstaller --onefile generate_waveform.py
   ```

The executable will be created in the `dist` directory.

## 🎯 Output

The script generates an SVG file with the same name as your input file. The visualization features:
- Colorful gradient waveform
- Depth of field effects
- Smooth rendering
- High-quality output suitable for printing or web use

## 📝 Notes

- The script creates a `.waveform_cache` directory to store processed audio data
- Large audio files may take longer to process
- The quality of the visualization is optimized for both detail and performance

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the matplotlib and numpy communities for their excellent libraries
- This project was developed with the assistance of AI tools, demonstrating the power of human-AI collaboration in software development
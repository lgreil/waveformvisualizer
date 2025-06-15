#!/bin/bash

echo "Music Waveform Visualizer"
echo "========================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.6 or higher"
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg is not installed"
    echo "Please install ffmpeg:"
    echo "  - Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Other: Visit https://ffmpeg.org/download.html"
    exit 1
fi

# Check and install requirements
echo "Checking and installing requirements..."
pip3 install -r requirements.txt

# Run the visualizer
echo
echo "Running the visualizer..."
python3 generate_waveform.py "$@" 
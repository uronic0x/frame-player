# Frame Player

[English](README.md) | [中文](README_CN.md)

A simple video player with frame-by-frame navigation, built with PySide6.

## Features

- Play / pause video playback
- Frame-by-frame stepping (previous / next frame)
- Jump to a specific frame number
- Progress slider with time and frame display
- Automatic FPS detection from video metadata

## Requirements

- Python 3.9+
- PySide6

## Installation

```bash
pip install PySide6
```

## Usage

```bash
python src/main.py
```

1. Click **Open Video** to load a video file (MP4, AVI, MKV, MOV, WMV, FLV).
2. Use **Previous Frame** / **Next Frame** to step frame by frame.
3. Enter a frame number and click **Go** to jump to a specific frame.
4. Drag the progress slider to seek.

## Project Structure

```
frame-player/
├── src/
│   └── main.py          # Main application
├── README.md
├── LICENSE
└── requirements.txt
```

## License

MIT License - see [LICENSE](LICENSE) for details.

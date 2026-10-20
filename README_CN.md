# 帧播放器 (Frame Player)

[English](README.md) | [中文](README_CN.md)

一个基于 PySide6 的简单视频播放器，支持逐帧定位功能。

## 功能特点

- 视频播放 / 暂停
- 逐帧步进（上一帧 / 下一帧）
- 跳转到指定帧号
- 进度条拖动，实时显示时间与帧号
- 自动从视频元数据检测帧率 (FPS)

## 环境要求

- Python 3.9 或更高版本
- PySide6

## 安装

```bash
pip install PySide6
```

## 使用方法

```bash
python src/main.py
```

1. 点击 **打开视频** 加载视频文件（支持 MP4、AVI、MKV、MOV、WMV、FLV 格式）。
2. 使用 **上一帧** / **下一帧** 按钮进行逐帧浏览。
3. 在输入框中输入帧号，点击 **跳转** 快速定位。
4. 拖动进度条进行粗略定位。

## 项目结构

```
frame-player/
├── src/
│   └── main.py          # 主程序
├── README.md            # 英文说明
├── README_CN.md         # 中文说明
├── LICENSE
└── requirements.txt
```

## 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件。

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QLineEdit, QFileDialog, QStyle
)
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaMetaData
from PySide6.QtMultimediaWidgets import QVideoWidget


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player - Frame Control")
        self.resize(1000, 700)

        # Default fps; will be updated from video metadata
        self.fps = 30.0
        self.total_frames = 0
        self.duration_ms = 0

        # ---------- Multimedia components ----------
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        self.setCentralWidget(self.video_widget)

        # ---------- Control bar ----------
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        control_widget.setLayout(control_layout)

        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.seek)
        control_layout.addWidget(self.progress_slider)

        # Time and frame info
        info_layout = QHBoxLayout()
        self.time_label = QLabel("00:00 / 00:00")
        self.frame_label = QLabel("Frame: 0 / 0")
        info_layout.addWidget(self.time_label)
        info_layout.addWidget(self.frame_label)
        info_layout.addStretch()
        control_layout.addLayout(info_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_open = QPushButton("Open Video")
        self.btn_open.clicked.connect(self.open_file)
        self.btn_play = QPushButton()
        self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_prev = QPushButton("Previous Frame")
        self.btn_prev.clicked.connect(self.prev_frame)
        self.btn_next = QPushButton("Next Frame")
        self.btn_next.clicked.connect(self.next_frame)

        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_play)
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_next)
        btn_layout.addStretch()

        # Frame jump input
        self.frame_edit = QLineEdit()
        self.frame_edit.setPlaceholderText("Enter frame number")
        self.frame_edit.setFixedWidth(100)
        self.btn_goto = QPushButton("Go")
        self.btn_goto.clicked.connect(self.goto_frame)
        btn_layout.addWidget(self.frame_edit)
        btn_layout.addWidget(self.btn_goto)

        control_layout.addLayout(btn_layout)

        # Main layout: video on top, controls at bottom
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_widget, 1)
        main_layout.addWidget(control_widget)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # ---------- Signal connections ----------
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.player.playbackStateChanged.connect(self.on_playback_state_changed)

    # ========== Slots ==========
    @Slot()
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv *.flv)")
        if file_path:
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    @Slot()
    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    @Slot()
    def prev_frame(self):
        if self.fps <= 0:
            return
        frame_len_ms = 1000.0 / self.fps
        new_pos = max(0, self.player.position() - int(frame_len_ms))
        self.player.setPosition(new_pos)

    @Slot()
    def next_frame(self):
        if self.fps <= 0:
            return
        frame_len_ms = 1000.0 / self.fps
        new_pos = min(self.player.duration(), self.player.position() + int(frame_len_ms))
        self.player.setPosition(new_pos)

    @Slot()
    def goto_frame(self):
        try:
            frame = int(self.frame_edit.text())
            if frame < 1:
                frame = 1
            if self.total_frames > 0:
                frame = min(frame, self.total_frames)
            # Convert frame number to milliseconds (frames start from 1)
            pos_ms = int((frame - 1) / self.fps * 1000)
            self.player.setPosition(pos_ms)
        except ValueError:
            pass

    @Slot(int)
    def seek(self, value):
        """Jump when the slider is moved."""
        self.player.setPosition(value)

    @Slot(int)
    def on_position_changed(self, position):
        """Update slider, time label and frame label."""
        if self.progress_slider.isSliderDown():
            return  # Avoid conflicts while user is dragging
        self.progress_slider.setValue(position)
        self.update_time_label(position)
        self.update_frame_label(position)

    @Slot(int)
    def on_duration_changed(self, duration):
        self.duration_ms = duration
        self.progress_slider.setRange(0, duration)
        self.update_time_label(self.player.position())
        self.update_frame_label(self.player.position())

    @Slot(QMediaPlayer.MediaStatus)
    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.get_video_fps()
            # Calculate total frames
            if self.fps > 0 and self.player.duration() > 0:
                self.total_frames = int(self.player.duration() / 1000 * self.fps)

    @Slot(QMediaPlayer.PlaybackState)
    def on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    # ========== Helper methods ==========
    def get_video_fps(self):
        """Get video frame rate from metadata; fall back to default if unavailable."""
        md = self.player.metaData()
        if md.keys():
            fps_var = md.value(QMediaMetaData.Key.VideoFrameRate)
            if fps_var:
                try:
                    self.fps = float(fps_var)
                except (ValueError, TypeError):
                    self.fps = 30.0
        # Recalculate total frames
        if self.fps > 0 and self.player.duration() > 0:
            self.total_frames = int(self.player.duration() / 1000 * self.fps)

    def update_time_label(self, position_ms):
        current = self.format_time(position_ms)
        total = self.format_time(self.player.duration())
        self.time_label.setText(f"{current} / {total}")

    def update_frame_label(self, position_ms):
        if self.fps <= 0:
            self.frame_label.setText("Frame: 0 / 0")
            return
        current_frame = int(position_ms / 1000 * self.fps) + 1
        total = self.total_frames
        self.frame_label.setText(f"Frame: {current_frame} / {total}")

    @staticmethod
    def format_time(ms):
        s = ms // 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())

import os
import requests
import pygame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider, QLabel

class AudioPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.is_playing = False
        self.is_paused = False
        self.audio_length = 0  # To store the total length of the audio
        self.current_position = 0  # To track current playback position
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_slider)
        
        # Initialize pygame mixer
        pygame.mixer.init()

    def init_ui(self):
        self.setWindowTitle("Audio Player")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # Time label
        self.time_label = QLabel("0:00 / 0:00", self)
        layout.addWidget(self.time_label)

        # Play button
        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.toggle_playback)
        layout.addWidget(self.play_button)

        # Pause button
        self.pause_button = QPushButton("Pause", self)
        self.pause_button.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_button)

        # Rewind button
        self.rewind_button = QPushButton("Rewind", self)
        self.rewind_button.clicked.connect(self.rewind)
        layout.addWidget(self.rewind_button)

        # Forward button
        self.forward_button = QPushButton("Forward", self)
        self.forward_button.clicked.connect(self.forward)
        layout.addWidget(self.forward_button)

        # Slider for playback
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.sliderMoved.connect(self.seek_audio)
        layout.addWidget(self.slider)

        # Set the layout for the window
        self.setLayout(layout)

    def load_audio(self, url):
        self.url = url
        try:
            # Download the audio data to a temporary file
            response = requests.get(self.url)
            if response.status_code == 200:
                # Save audio content to a temporary file
                temp_audio_path = "temp_audio.wav"
                with open(temp_audio_path, "wb") as f:
                    f.write(response.content)

                # Now load the audio into pygame mixer
                pygame.mixer.music.load(temp_audio_path)
                self.audio_length = pygame.mixer.Sound(temp_audio_path).get_length()
                self.slider.setRange(0, int(self.audio_length))
                self.time_label.setText(f"0:00 / {self.format_time(self.audio_length)}")
                print("Audio loaded successfully")

                # Optionally, delete the temporary file after loading
                os.remove(temp_audio_path)
            else:
                print(f"Error downloading audio: {response.status_code}")
        except Exception as e:
            print(f"Error loading audio: {e}")

    def toggle_playback(self):
        if self.is_playing:
            self.pause_audio()
        else:
            if self.is_paused:
                self.resume_audio()
            else:
                self.play_audio()

    def play_audio(self):
        pygame.mixer.music.play()
        self.is_playing = True
        self.is_paused = False
        self.timer.start(100)  # Update slider every 100 ms
        self.play_button.setText("Pause")
        
    def pause_audio(self):
        pygame.mixer.music.pause()
        self.is_playing = False
        self.is_paused = True
        self.timer.stop()
        self.play_button.setText("Play")

    def resume_audio(self):
        pygame.mixer.music.unpause()
        self.is_playing = True
        self.is_paused = False
        self.timer.start(100)
        self.play_button.setText("Pause")

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.timer.stop()
        self.play_button.setText("Play")

    def update_slider(self):
        if self.is_playing:
            current_position = pygame.mixer.music.get_pos() / 1000  # Convert ms to seconds
            self.slider.setValue(int(current_position))
            self.current_position = current_position
            self.time_label.setText(f"{self.format_time(current_position)} / {self.format_time(self.audio_length)}")
        
    def seek_audio(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=self.slider.value())
            self.current_position = self.slider.value()

    def rewind(self):
        new_position = max(self.current_position - 10, 0)  # Rewind 10 seconds
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=new_position)
        self.slider.setValue(int(new_position))
        self.current_position = new_position

    def forward(self):
        new_position = min(self.current_position + 10, self.audio_length)  # Forward 10 seconds
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=new_position)
        self.slider.setValue(int(new_position))
        self.current_position = new_position

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"


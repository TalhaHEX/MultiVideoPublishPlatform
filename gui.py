"""
Social Media Video Automation Tool - PyQt6 Version
Part 1: Main Application Structure and Imports
"""

import json
import logging
import math
import os
import random
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import existing modules
from src.download_audio import (
    download_file,
    get_files_in_folder,
    get_folder_id,
    google_drive_service,
)
from src.extend_video import extend_video_to_60s_with_audio
from src.facebook import Facebook
from src.generate_description_hashtag import GenerateDescriptionHashtag
from src.instagram import Instagram
from src.tiktok import TikTokBot
from src.youtube import Youtube

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from moviepy import (
        AudioFileClip,
        VideoFileClip,
        concatenate_audioclips,
        concatenate_videoclips,
    )
except ImportError as e:
    print(f"Required library missing: {e}")


# Custom QSS Stylesheet for Modern UI
STYLESHEET = """
QMainWindow {
    background-color: #1e1e2e;
}

QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1e1e2e;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 12px 24px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QTabBar::tab:hover {
    background-color: #45475a;
}

QGroupBox {
    background-color: #181825;
    border: 2px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 20px;
    font-weight: bold;
    color: #cdd6f4;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #89b4fa;
    font-size: 14px;
}

QLabel {
    color: #cdd6f4;
    font-size: 13px;
}

QLineEdit, QSpinBox, QTextEdit {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 6px;
    padding: 8px;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
}

QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {
    border: 2px solid #89b4fa;
}

QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #74c7ec;
}

QPushButton:pressed {
    background-color: #89dceb;
}

QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QPushButton#startButton {
    background-color: #a6e3a1;
    color: #1e1e2e;
}

QPushButton#startButton:hover {
    background-color: #94e2d5;
}

QPushButton#stopButton {
    background-color: #f38ba8;
    color: #1e1e2e;
}

QPushButton#stopButton:hover {
    background-color: #eba0ac;
}

QPushButton#saveButton {
    background-color: #cba6f7;
}

QPushButton#saveButton:hover {
    background-color: #b4befe;
}

QCheckBox {
    color: #cdd6f4;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #45475a;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QCheckBox::indicator:hover {
    border-color: #89b4fa;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #181825;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QProgressBar {
    border: 2px solid #313244;
    border-radius: 6px;
    text-align: center;
    background-color: #181825;
    color: #cdd6f4;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 4px;
}

QFrame#statusFrame {
    background-color: #181825;
    border: 2px solid #313244;
    border-radius: 8px;
}

QTextEdit#logText {
    background-color: #11111b;
    border: 2px solid #313244;
    border-radius: 6px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px;
}
"""


class AutomationWorker(QThread):
    """Worker thread for automation tasks"""

    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)  # current, total
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.is_running = True

    def run(self):
        """Main automation loop"""
        while self.is_running:
            try:
                self.log_signal.emit("\n🔥 Downloading audio from Google Drive...")
                audio_file = self.download_audio_from_drive()

                if audio_file:
                    self.log_signal.emit(f"✓ Downloaded: {audio_file}")

                    self.log_signal.emit("🎬 Creating video with audio...")
                    output_video, original_video = self.create_video_with_audio(
                        audio_file
                    )

                    if output_video and original_video:
                        self.log_signal.emit(f"✓ Video created: {output_video}")

                        audio_name = os.path.basename(audio_file)
                        uploaded_platforms = self.upload_to_platforms(
                            output_video, audio_name
                        )

                        # Log the upload
                        if (
                            self.config.get("avoid_duplicates", True)
                            and uploaded_platforms
                        ):
                            self.log_upload(
                                audio_file, original_video, uploaded_platforms
                            )

                        # Delete used audio file
                        try:
                            os.remove(audio_file)
                            self.log_signal.emit(f"🗑 Deleted audio file: {audio_file}")
                        except:
                            pass

                # Wait for next interval
                if self.is_running:
                    self.countdown_timer()

            except Exception as e:
                self.error_signal.emit(f"❌ Error: {str(e)}")
                import traceback

                self.log_signal.emit(f"Traceback: {traceback.format_exc()}")

        self.finished_signal.emit()

    def stop(self):
        """Stop the automation"""
        self.is_running = False

    def countdown_timer(self):
        """Countdown timer between posts"""
        interval_seconds = self.config.get("interval", 60) * 60

        for remaining in range(interval_seconds, 0, -1):
            if not self.is_running:
                break

            mins, secs = divmod(remaining, 60)
            self.progress_signal.emit(remaining, interval_seconds)
            time.sleep(1)

    # Continue in next part...

    def download_audio_from_drive(self):
        """Download random audio file from Google Drive"""
        try:
            SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
            creds = None

            if os.path.exists("token.json"):
                creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client.json", SCOPES)
                creds = flow.run_local_server(port=0)
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

            service = build("drive", "v3", credentials=creds)

            # Get folder ID
            query = f"name='{self.config['drive_folder']}' and mimeType='application/vnd.google-apps.folder'"
            results = service.files().list(q=query, fields="files(id, name)").execute()
            folders = results.get("files", [])

            if not folders:
                self.log_signal.emit(
                    f"❌ Folder '{self.config['drive_folder']}' not found on Drive"
                )
                return None

            folder_id = folders[0]["id"]

            # Get audio files
            query = f"'{folder_id}' in parents and mimeType contains 'audio'"
            results = service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get("files", [])

            if not files:
                self.log_signal.emit("❌ No audio files found in folder")
                return None

            # Pick random file
            random_file = random.choice(files)

            # Download
            request = service.files().get_media(fileId=random_file["id"])
            audio_folder = self.config["audio_folder"]
            os.makedirs(audio_folder, exist_ok=True)
            file_path = os.path.join(audio_folder, random_file["name"])

            with open(file_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

            return file_path

        except Exception as e:
            self.log_signal.emit(f"❌ Drive download error: {str(e)}")
            return None

    def check_duplicate(self, audio_file, video_file):
        """Check if audio/video combination was already uploaded"""
        log_file = "upload_log.json"

        if not os.path.exists(log_file):
            return False

        try:
            with open(log_file, "r") as f:
                logs = json.load(f)

            audio_name = os.path.basename(audio_file)
            video_name = os.path.basename(video_file)

            for entry in logs:
                if (
                    entry["audio_file"] == audio_name
                    and entry["video_file"] == video_name
                ):
                    return True

            return False
        except Exception as e:
            self.log_signal.emit(f"⚠ Error checking duplicates: {str(e)}")
            return False

    def log_upload(self, audio_file, video_file, platforms):
        """Log the uploaded audio/video combination"""
        log_file = "upload_log.json"

        try:
            # Load existing logs
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    logs = json.load(f)
            else:
                logs = []

            # Add new entry
            entry = {
                "audio_file": os.path.basename(audio_file),
                "video_file": os.path.basename(video_file),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "platforms": platforms,
            }
            logs.append(entry)

            # Save logs
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=4)

            self.log_signal.emit("✓ Upload logged successfully")
        except Exception as e:
            self.log_signal.emit(f"⚠ Error logging upload: {str(e)}")

    def create_video_with_audio(self, audio_file):
        """Create 60s video with audio"""
        try:
            video_folder = self.config["video_folder"]
            output_folder = self.config["output_folder"]
            os.makedirs(output_folder, exist_ok=True)

            # Pick random video
            video_files = [
                f
                for f in os.listdir(video_folder)
                if f.endswith((".mp4", ".avi", ".mov"))
            ]
            if not video_files:
                self.log_signal.emit("❌ No video files found")
                return None, None

            # Check for duplicates if enabled
            if self.config.get("avoid_duplicates", True):
                max_attempts = len(video_files)
                attempts = 0
                video_file = None

                while attempts < max_attempts:
                    temp_video = random.choice(video_files)
                    temp_video_path = os.path.join(video_folder, temp_video)

                    if not self.check_duplicate(audio_file, temp_video_path):
                        video_file = temp_video
                        break
                    else:
                        self.log_signal.emit(
                            "⚠ Duplicate combination detected, trying another video..."
                        )
                        video_files.remove(temp_video)
                        attempts += 1

                if video_file is None:
                    self.log_signal.emit(
                        "❌ All video combinations already used with this audio"
                    )
                    return None, None
            else:
                video_file = random.choice(video_files)

            video_path = os.path.join(video_folder, video_file)

            # Load video and remove audio
            clip = VideoFileClip(video_path).without_audio()

            # Extend to 60 seconds
            repeat_times = math.ceil(60 / clip.duration)
            final_clip = concatenate_videoclips([clip] * repeat_times)
            final_clip = final_clip.with_duration(60)

            # Add audio
            audio_clip = AudioFileClip(audio_file)
            if audio_clip.duration < 60:
                audio_clip = concatenate_audioclips(
                    [audio_clip] * math.ceil(60 / audio_clip.duration)
                )
            audio_clip = audio_clip.subclipped(0, 60)
            final_clip = final_clip.with_audio(audio_clip)

            # Export
            output_path = os.path.join(output_folder, f"output_{int(time.time())}.mp4")
            final_clip.write_videofile(
                output_path, codec="libx264", audio_codec="aac", logger=None
            )

            # Clean up clips
            final_clip.close()
            clip.close()
            audio_clip.close()

            return output_path, video_path

        except Exception as e:
            self.log_signal.emit(f"❌ Video creation error: {str(e)}")
            return None, None

    def upload_to_platforms(self, video_path, audio_name):
        """Upload video to selected platforms"""
        # Generate AI content if enabled
        if self.config.get("use_ai", True):
            self.log_signal.emit("🤖 Generating AI descriptions and hashtags...")
            try:
                gen = GenerateDescriptionHashtag()
                generated = gen.generate_description_and_hashtags(
                    self.config.get("lang1", "English"),
                    self.config.get("lang2", "Spanish"),
                    self.config.get("lang3", "French"),
                    self.config.get("topic", "AI Automation"),
                )

                if generated:
                    full_description = f"{generated['lang1_desc']}\n\n{generated['lang2_desc']}\n\n{generated['lang3_desc']}"
                    full_caption = f"{full_description}\n\n{generated['hashtags']}"
                    self.log_signal.emit("✓ AI content generated successfully")
                else:
                    description = self.config.get("description", "")
                    hashtags = self.config.get("hashtags", "")
                    full_caption = f"{description}\n\n{hashtags}"
                    self.log_signal.emit(
                        "⚠ Using manual description (AI generation failed)"
                    )
            except Exception as e:
                self.log_signal.emit(
                    f"⚠ AI generation error: {str(e)}, using manual input"
                )
                description = self.config.get("description", "")
                hashtags = self.config.get("hashtags", "")
                full_caption = f"{description}\n\n{hashtags}"
        else:
            description = self.config.get("description", "")
            hashtags = self.config.get("hashtags", "")
            full_caption = f"{description}\n\n{hashtags}"

        uploaded_platforms = []
        platforms = self.config.get("platforms", {})

        for platform, enabled in platforms.items():
            if not enabled:
                continue

            self.log_signal.emit(f"\n📤 Uploading to {platform}...")

            try:
                if platform == "TikTok":
                    bot = TikTokBot()
                    bot.upload_video(
                        video_path, self.config.get("tiktok_artist", ""), full_caption
                    )
                elif platform == "Instagram":
                    ig = Instagram()
                    ig.upload_video(video_path, full_caption)
                    ig.close()
                elif platform == "Facebook":
                    fb = Facebook()
                    fb.upload_video(video_path, full_caption, "next_button.png")
                    fb.close()
                elif platform == "YouTube":
                    title = os.path.splitext(audio_name)[0]
                    title = title.replace("_", " ").replace("-", " ").title()
                    yt = Youtube()
                    yt.upload_video(video_path, title, full_caption)
                    yt.close()

                self.log_signal.emit(f"✓ {platform} upload completed")
                uploaded_platforms.append(platform)
            except Exception as e:
                self.log_signal.emit(f"❌ {platform} upload failed: {str(e)}")

        return uploaded_platforms


"""
Part 3: Main Window Class - Configuration Tab
"""


class SocialMediaAutomationGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Social Media Video Automation Tool")
        self.setGeometry(100, 100, 1000, 750)

        # Apply stylesheet
        self.setStyleSheet(STYLESHEET)

        # Variables
        self.worker = None
        self.config_file = "automation_config.json"

        # Setup UI
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Title
        title_label = QLabel("🎬 Social Media Video Automation")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #89b4fa; padding: 10px;")
        main_layout.addWidget(title_label)

        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Create tabs
        self.config_tab = self.create_config_tab()
        self.platform_tab = self.create_platform_tab()
        self.control_tab = self.create_control_tab()

        self.tabs.addTab(self.config_tab, "⚙️ Configuration")
        self.tabs.addTab(self.platform_tab, "🌐 Platform Settings")
        self.tabs.addTab(self.control_tab, "🎮 Control & Logs")

    def create_config_tab(self):
        """Create configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # Google Drive Settings
        drive_group = QGroupBox("☁️ Google Drive Settings")
        drive_layout = QGridLayout()
        drive_layout.setSpacing(10)

        drive_layout.addWidget(QLabel("Audio Folder Name on Drive:"), 0, 0)
        self.drive_folder_input = QLineEdit("Audio")
        drive_layout.addWidget(self.drive_folder_input, 0, 1)

        drive_group.setLayout(drive_layout)
        scroll_layout.addWidget(drive_group)

        # Local Paths
        paths_group = QGroupBox("📁 Local Folder Paths")
        paths_layout = QGridLayout()
        paths_layout.setSpacing(10)

        paths_layout.addWidget(QLabel("Local Audio Folder:"), 0, 0)
        self.audio_folder_input = QLineEdit("Audio")
        paths_layout.addWidget(self.audio_folder_input, 0, 1)
        audio_browse_btn = QPushButton("Browse")
        audio_browse_btn.clicked.connect(
            lambda: self.browse_folder(self.audio_folder_input)
        )
        paths_layout.addWidget(audio_browse_btn, 0, 2)

        paths_layout.addWidget(QLabel("Local Video Folder:"), 1, 0)
        self.video_folder_input = QLineEdit("Video")
        paths_layout.addWidget(self.video_folder_input, 1, 1)
        video_browse_btn = QPushButton("Browse")
        video_browse_btn.clicked.connect(
            lambda: self.browse_folder(self.video_folder_input)
        )
        paths_layout.addWidget(video_browse_btn, 1, 2)

        paths_layout.addWidget(QLabel("Output Folder:"), 2, 0)
        self.output_folder_input = QLineEdit("Output")
        paths_layout.addWidget(self.output_folder_input, 2, 1)
        output_browse_btn = QPushButton("Browse")
        output_browse_btn.clicked.connect(
            lambda: self.browse_folder(self.output_folder_input)
        )
        paths_layout.addWidget(output_browse_btn, 2, 2)

        paths_group.setLayout(paths_layout)
        scroll_layout.addWidget(paths_group)

        # Timing Settings
        timing_group = QGroupBox("⏰ Automation Timing")
        timing_layout = QGridLayout()
        timing_layout.setSpacing(10)

        timing_layout.addWidget(QLabel("Interval Between Posts (minutes):"), 0, 0)
        self.interval_input = QSpinBox()
        self.interval_input.setMinimum(1)
        self.interval_input.setMaximum(1440)
        self.interval_input.setValue(60)
        self.interval_input.setMinimumWidth(100)
        timing_layout.addWidget(self.interval_input, 0, 1)

        timing_group.setLayout(timing_layout)
        scroll_layout.addWidget(timing_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        return tab

    def browse_folder(self, line_edit):
        """Browse for folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            line_edit.setText(folder)
            """
Part 4: Platform Settings Tab
Add this method to the SocialMediaAutomationGUI class
"""

    def create_platform_tab(self):
        """Create platform settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # Platform Selection
        platform_group = QGroupBox("🎯 Select Platforms")
        platform_layout = QGridLayout()
        platform_layout.setSpacing(15)

        self.platform_checkboxes = {}
        platforms = [
            ("TikTok", "🎵"),
            ("Instagram", "📸"),
            ("Facebook", "👥"),
            ("YouTube", "▶️"),
        ]

        for idx, (platform, emoji) in enumerate(platforms):
            checkbox = QCheckBox(f"{emoji} {platform}")
            checkbox.setChecked(True)
            self.platform_checkboxes[platform] = checkbox
            platform_layout.addWidget(checkbox, idx // 2, idx % 2)

        platform_group.setLayout(platform_layout)
        scroll_layout.addWidget(platform_group)

        # TikTok Settings
        tiktok_group = QGroupBox("🎵 TikTok Settings")
        tiktok_layout = QGridLayout()
        tiktok_layout.setSpacing(10)

        tiktok_layout.addWidget(QLabel("Artist Name:"), 0, 0)
        self.tiktok_artist_input = QLineEdit()
        self.tiktok_artist_input.setPlaceholderText("Enter artist name for TikTok")
        tiktok_layout.addWidget(self.tiktok_artist_input, 0, 1)

        tiktok_group.setLayout(tiktok_layout)
        scroll_layout.addWidget(tiktok_group)

        # YouTube Settings
        youtube_group = QGroupBox("▶️ YouTube Settings")
        youtube_layout = QGridLayout()
        youtube_layout.setSpacing(10)

        youtube_layout.addWidget(QLabel("Video Title:"), 0, 0)
        self.youtube_title_input = QLineEdit("Awesome Video")
        youtube_layout.addWidget(self.youtube_title_input, 0, 1)

        youtube_group.setLayout(youtube_layout)
        scroll_layout.addWidget(youtube_group)

        # Common Settings
        common_group = QGroupBox("✍️ Common Settings (All Platforms)")
        common_layout = QVBoxLayout()
        common_layout.setSpacing(10)

        common_layout.addWidget(QLabel("Description/Caption:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter your video description...")
        self.description_input.setMaximumHeight(100)
        self.description_input.setText("Check out this amazing video! 🎥✨")
        common_layout.addWidget(self.description_input)

        common_layout.addWidget(QLabel("Hashtags (comma-separated):"))
        self.hashtags_input = QTextEdit()
        self.hashtags_input.setPlaceholderText("Enter hashtags separated by commas...")
        self.hashtags_input.setMaximumHeight(80)
        self.hashtags_input.setText("#viral #trending #amazing #fyp #foryou")
        common_layout.addWidget(self.hashtags_input)

        self.avoid_duplicates_checkbox = QCheckBox(
            "🚫 Avoid uploading duplicate audio/video combinations"
        )
        self.avoid_duplicates_checkbox.setChecked(True)
        common_layout.addWidget(self.avoid_duplicates_checkbox)

        common_group.setLayout(common_layout)
        scroll_layout.addWidget(common_group)

        # AI Content Generation Settings
        ai_group = QGroupBox("🤖 AI Content Generation")
        ai_layout = QGridLayout()
        ai_layout.setSpacing(10)

        ai_layout.addWidget(QLabel("Language 1:"), 0, 0)
        self.lang1_input = QLineEdit("English")
        ai_layout.addWidget(self.lang1_input, 0, 1)

        ai_layout.addWidget(QLabel("Language 2:"), 0, 2)
        self.lang2_input = QLineEdit("Spanish")
        ai_layout.addWidget(self.lang2_input, 0, 3)

        ai_layout.addWidget(QLabel("Language 3:"), 1, 0)
        self.lang3_input = QLineEdit("French")
        ai_layout.addWidget(self.lang3_input, 1, 1)

        ai_layout.addWidget(QLabel("Topic:"), 1, 2)
        self.topic_input = QLineEdit("AI Automation")
        ai_layout.addWidget(self.topic_input, 1, 3)

        self.use_ai_checkbox = QCheckBox(
            "✨ Use AI-generated descriptions and hashtags"
        )
        self.use_ai_checkbox.setChecked(True)
        ai_layout.addWidget(self.use_ai_checkbox, 2, 0, 1, 4)

        ai_group.setLayout(ai_layout)
        scroll_layout.addWidget(ai_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        return tab

    """
Part 5: Control & Logs Tab
Add this method to the SocialMediaAutomationGUI class
"""

    def create_control_tab(self):
        """Create control and logs tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Control buttons
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        control_layout.setSpacing(10)

        self.start_button = QPushButton("▶ Start Automation")
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self.start_automation)
        self.start_button.setMinimumHeight(40)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("⏹ Stop Automation")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.clicked.connect(self.stop_automation)
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(40)
        control_layout.addWidget(self.stop_button)

        save_button = QPushButton("💾 Save Config")
        save_button.setObjectName("saveButton")
        save_button.clicked.connect(self.save_config)
        save_button.setMinimumHeight(40)
        control_layout.addWidget(save_button)

        load_button = QPushButton("📂 Load Config")
        load_button.clicked.connect(self.load_config)
        load_button.setMinimumHeight(40)
        control_layout.addWidget(load_button)

        control_layout.addStretch()
        layout.addWidget(control_frame)

        # Status frame
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_frame.setMinimumHeight(120)
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(10)

        status_title = QLabel("📊 Status")
        status_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_title.setStyleSheet("color: #89b4fa;")
        status_layout.addWidget(status_title)

        self.status_label = QLabel("⚪ Idle - Ready to start")
        self.status_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #a6e3a1; padding: 5px;")
        status_layout.addWidget(self.status_label)

        self.progress_label = QLabel("Next post in: --")
        self.progress_label.setStyleSheet("color: #cdd6f4; padding: 5px;")
        status_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        status_layout.addWidget(self.progress_bar)

        layout.addWidget(status_frame)

        # Logs section
        logs_label = QLabel("📝 Activity Logs")
        logs_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        logs_label.setStyleSheet("color: #89b4fa;")
        layout.addWidget(logs_label)

        self.log_text = QTextEdit()
        self.log_text.setObjectName("logText")
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Clear logs button
        clear_button = QPushButton("🗑️ Clear Logs")
        clear_button.clicked.connect(self.clear_logs)
        layout.addWidget(clear_button)

        return tab

    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)

        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        """Clear log text"""
        self.log_text.clear()
        self.log_message("Logs cleared")
        """
Part 6: Configuration Management and Validation
Add these methods to the SocialMediaAutomationGUI class
"""

    def save_config(self):
        """Save configuration to file"""
        config = {
            "avoid_duplicates": self.avoid_duplicates_checkbox.isChecked(),
            "drive_folder": self.drive_folder_input.text(),
            "audio_folder": self.audio_folder_input.text(),
            "video_folder": self.video_folder_input.text(),
            "output_folder": self.output_folder_input.text(),
            "interval": self.interval_input.value(),
            "tiktok_artist": self.tiktok_artist_input.text(),
            "youtube_title": self.youtube_title_input.text(),
            "description": self.description_input.toPlainText(),
            "hashtags": self.hashtags_input.toPlainText(),
            "platforms": {
                platform: checkbox.isChecked()
                for platform, checkbox in self.platform_checkboxes.items()
            },
            "lang1": self.lang1_input.text(),
            "lang2": self.lang2_input.text(),
            "lang3": self.lang3_input.text(),
            "topic": self.topic_input.text(),
            "use_ai": self.use_ai_checkbox.isChecked(),
        }

        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)

            QMessageBox.information(
                self,
                "Success",
                "Configuration saved successfully!",
                QMessageBox.StandardButton.Ok,
            )
            self.log_message("✓ Configuration saved")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save config: {str(e)}",
                QMessageBox.StandardButton.Ok,
            )

    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            self.log_message("⚠ No saved configuration found")
            return

        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)

            self.avoid_duplicates_checkbox.setChecked(
                config.get("avoid_duplicates", True)
            )
            self.drive_folder_input.setText(config.get("drive_folder", "Audio"))
            self.audio_folder_input.setText(config.get("audio_folder", "Audio"))
            self.video_folder_input.setText(config.get("video_folder", "Video"))
            self.output_folder_input.setText(config.get("output_folder", "Output"))
            self.interval_input.setValue(config.get("interval", 60))
            self.tiktok_artist_input.setText(config.get("tiktok_artist", ""))
            self.youtube_title_input.setText(
                config.get("youtube_title", "Awesome Video")
            )
            self.description_input.setText(config.get("description", ""))
            self.hashtags_input.setText(config.get("hashtags", ""))
            self.lang1_input.setText(config.get("lang1", "English"))
            self.lang2_input.setText(config.get("lang2", "Spanish"))
            self.lang3_input.setText(config.get("lang3", "French"))
            self.topic_input.setText(config.get("topic", "AI Automation"))
            self.use_ai_checkbox.setChecked(config.get("use_ai", True))

            platforms = config.get("platforms", {})
            for platform, checkbox in self.platform_checkboxes.items():
                checkbox.setChecked(platforms.get(platform, True))

            self.log_message("✓ Configuration loaded successfully")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load config: {str(e)}",
                QMessageBox.StandardButton.Ok,
            )

    def validate_config(self):
        """Validate configuration before starting"""
        errors = []

        if not os.path.exists(self.audio_folder_input.text()):
            errors.append(
                f"Audio folder does not exist: {self.audio_folder_input.text()}"
            )

        if not os.path.exists(self.video_folder_input.text()):
            errors.append(
                f"Video folder does not exist: {self.video_folder_input.text()}"
            )

        if not any(cb.isChecked() for cb in self.platform_checkboxes.values()):
            errors.append("Please select at least one platform")

        if (
            self.platform_checkboxes["TikTok"].isChecked()
            and not self.tiktok_artist_input.text()
        ):
            errors.append("TikTok artist name is required when TikTok is enabled")

        return errors

    def get_config(self):
        """Get current configuration as dictionary"""
        return {
            "avoid_duplicates": self.avoid_duplicates_checkbox.isChecked(),
            "drive_folder": self.drive_folder_input.text(),
            "audio_folder": self.audio_folder_input.text(),
            "video_folder": self.video_folder_input.text(),
            "output_folder": self.output_folder_input.text(),
            "interval": self.interval_input.value(),
            "tiktok_artist": self.tiktok_artist_input.text(),
            "youtube_title": self.youtube_title_input.text(),
            "description": self.description_input.toPlainText(),
            "hashtags": self.hashtags_input.toPlainText(),
            "platforms": {
                platform: checkbox.isChecked()
                for platform, checkbox in self.platform_checkboxes.items()
            },
            "lang1": self.lang1_input.text(),
            "lang2": self.lang2_input.text(),
            "lang3": self.lang3_input.text(),
            "topic": self.topic_input.text(),
            "use_ai": self.use_ai_checkbox.isChecked(),
        }

    """
Part 7: Automation Control and Main Entry Point (Final Part)
Add these methods to the SocialMediaAutomationGUI class
"""

    def start_automation(self):
        """Start the automation process"""
        errors = self.validate_config()
        if errors:
            QMessageBox.critical(
                self,
                "Validation Error",
                "\n".join(errors),
                QMessageBox.StandardButton.Ok,
            )
            return

        # Disable start button, enable stop button
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("🟢 Running - Automation Active")
        self.status_label.setStyleSheet("color: #a6e3a1; padding: 5px;")

        self.log_message("=" * 50)
        self.log_message("🚀 Starting automation...")
        self.log_message(f"Interval: {self.interval_input.value()} minutes")
        self.log_message("=" * 50)

        # Create and start worker thread
        config = self.get_config()
        self.worker = AutomationWorker(config)

        # Connect signals
        self.worker.log_signal.connect(self.log_message)
        self.worker.status_signal.connect(self.update_status)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.on_automation_finished)
        self.worker.error_signal.connect(self.on_automation_error)

        # Start worker
        self.worker.start()

    def stop_automation(self):
        """Stop the automation process"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("🔴 Stopped - Automation Inactive")
        self.status_label.setStyleSheet("color: #f38ba8; padding: 5px;")
        self.progress_label.setText("Next post in: --")
        self.progress_bar.setValue(0)
        self.log_message("⏹ Automation stopped by user")

    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)

    def update_progress(self, current, total):
        """Update progress bar and label"""
        mins, secs = divmod(current, 60)
        self.progress_label.setText(f"Next post in: {mins:02d}:{secs:02d}")

        # Update progress bar (inverse - starts at 100%, goes to 0%)
        percentage = int((current / total) * 100)
        self.progress_bar.setValue(100 - percentage)

    def on_automation_finished(self):
        """Handle automation finish"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("⚪ Idle - Automation Completed")
        self.status_label.setStyleSheet("color: #cdd6f4; padding: 5px;")
        self.log_message("✓ Automation completed")

    def on_automation_error(self, error):
        """Handle automation error"""
        self.log_message(error)
        QMessageBox.warning(
            self, "Automation Error", error, QMessageBox.StandardButton.Ok
        )

    def closeEvent(self, event):
        """Handle window close event"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Automation is still running. Do you want to stop it and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.worker.stop()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main entry point"""
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for better consistency

    # Set application info
    app.setApplicationName("Social Media Automation")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("AutomationTools")

    # Create and show main window
    window = SocialMediaAutomationGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

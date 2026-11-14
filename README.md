# Multi-Platform Social Media Video Automation & Publishing Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6-green.svg?logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![Automation](https://img.shields.io/badge/Automation-Selenium%20Firefox-orange.svg?logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![Video Processing](https://img.shields.io/badge/Video-MoviePy-red.svg)](https://zulko.github.io/moviepy/)
[![AI Powered](https://img.shields.io/badge/AI-xAI%20Grok-black.svg)](https://x.ai/)

An all-in-one automation desktop application and workflow designed to streamline social media content production and publishing. It automatically downloads background audio from Google Drive, loops/extends video footage to standard 60-second short-form dimensions, generates AI-powered multilingual captions and hashtags using the **xAI Grok API**, and automatically uploads to **YouTube Shorts**, **Facebook Reels/Videos**, **Instagram**, and **TikTok** using browser automation.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
  - [1. Grok API Key (.env)](#1-grok-api-key-env)
  - [2. Google Drive OAuth Credentials](#2-google-drive-oauth-credentials)
  - [3. Browser Profile & Platform Logins](#3-browser-profile--platform-logins)
- [Usage](#-usage)
  - [Option A: Graphical User Interface (GUI)](#option-a-graphical-user-interface-gui)
  - [Option B: CLI Automation Workflow](#option-b-cli-automation-workflow)
- [How It Works](#-how-it-works)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer & License](#-disclaimer--license)

---

## 🚀 Key Features

- **Modern PyQt6 Desktop GUI**: Feature-rich, dark-mode user interface with live logs, status badges, progress bars, and tabbed configuration.
- **AI-Powered Captions & Hashtags**: Integrates with **xAI Grok (`grok-2-1212`)** to generate high-engagement video descriptions across 3 selectable languages simultaneously, plus trending English hashtags.
- **Smart Video Extension & Audio Sync**: Automatically takes source video footage, strips audio, loops/concatenates it to 60 seconds (Shorts/Reels length), and attaches synced background music using `moviepy`.
- **Multi-Platform Automated Publishing**:
  - **YouTube**: Automates YouTube Studio upload with customized title and description.
  - **Facebook**: Uploads reels/videos with computer vision UI detection (`OpenCV` + `pyautogui` + `Selenium`).
  - **Instagram**: Automates media upload and caption pasting.
  - **TikTok**: Automates video uploading and background artist sound search.
- **Persistent Firefox Browser Profile**: Reuses your default Firefox browser profile so you log in once manually and bypass two-factor authentication or CAPTCHA on subsequent runs.
- **Cloud Audio Integration**: Automatically connects to Google Drive via OAuth2 to pull random background audio tracks.

---

## 🏗 System Architecture

```
┌────────────────────────────────────────────────────────┐
│                   PyQt6 GUI / CLI                      │
└───────┬───────────────────┬────────────────────┬───────┘
        │                   │                    │
        ▼                   ▼                    ▼
┌──────────────┐    ┌──────────────┐     ┌──────────────┐
│ Google Drive │    │   MoviePy    │     │   xAI Grok   │
│ Audio Sync   │    │ Video Editor │     │  AI Engine   │
└───────┬──────┘    └───────┬──────┘     └───────┬──────┘
        │                   │                    │
        └─────────► Output/output_60sec.mp4 ◄────┘
                            │
                            ▼
              ┌───────────────────────────┐
              │ Selenium (Firefox Profile)│
              └─────────────┬─────────────┘
                            │
       ┌───────────┬────────┴────────┬───────────┐
       ▼           ▼                 ▼           ▼
   YouTube     Facebook          Instagram     TikTok
```

---

## 📁 Project Structure

```plaintext
MultiVideoPublishedPlatform/
├── gui.py                             # Main PyQt6 graphical user interface application
├── generate_toke.py                   # Google Drive OAuth2 token generation script
├── requirements.txt                   # Python package dependencies
├── .env.example                       # Example environment variable file
├── .gitignore                         # Git exclusion rules
├── README.md                          # Project documentation
├── Audio/                             # Directory for downloaded audio tracks
├── Video/                             # Directory for raw video clips
├── Output/                            # Directory for finalized 60-second rendered videos
└── src/
    ├── __init__.py                    # Python package initializer
    ├── main.py                        # Headless CLI automation pipeline
    ├── driver_instance.py             # Firefox WebDriver configuration & profile loader
    ├── generate_description_hashtag.py# xAI Grok API client (reads GROK_API_KEY from environment)
    ├── extend_video.py                # Video processing and audio concatenation
    ├── download_audio.py              # Google Drive API downloader
    ├── youtube.py                     # YouTube Studio automation module
    ├── facebook.py                    # Facebook posting module (Selenium + OpenCV)
    ├── instagram.py                   # Instagram posting module
    └── tiktok.py                      # TikTok upload & sound search module
```

---

## ⚙ Prerequisites

1. **Python 3.10 or higher**: [Download Python](https://www.python.org/downloads/)
2. **Mozilla Firefox**: [Download Firefox](https://www.mozilla.org/firefox/)
3. **GeckoDriver**: [Download GeckoDriver](https://github.com/mozilla/geckodriver/releases) matching your operating system and place it in your system `PATH` or in the project root directory.
4. **Google Cloud Account** *(optional, only if using Google Drive audio fetch)*: Enabled Google Drive API with OAuth client credentials.
5. **xAI Grok API Key** *(optional, only if generating captions via AI)*: Available from the [xAI Console](https://console.x.ai/).

---

## 📥 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
   ```

2. **Create and activate a virtual environment**:
   - **Windows**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔧 Configuration

### 1. Grok API Key (`.env`)

Copy the example file and add your xAI API key:

```bash
cp .env.example .env
```

Open `.env` in any editor and set:
```env
GROK_API_KEY=xai-your-api-key-here
```
> The application uses `python-dotenv` and `os.getenv("GROK_API_KEY")` to securely retrieve this key without hardcoding it in source code.

---

### 2. Google Drive OAuth Credentials

If downloading background tracks automatically from Google Drive:
1. Place your Google Cloud OAuth 2.0 Client credentials JSON file named **`client.json`** in the project root.
2. Generate the access token:
   ```bash
   python generate_toke.py
   ```
3. A browser window will open asking you to authorize access. After approval, `token.json` will be saved locally.

---

### 3. Browser Profile & Platform Logins

The Selenium driver (`src/driver_instance.py`) automatically attempts to load your existing Firefox profile (`%APPDATA%\Mozilla\Firefox\Profiles\*.default-release` on Windows).

**Recommended first-time setup:**
1. Open Firefox manually on your system.
2. Log into your accounts on:
   - [YouTube Studio](https://studio.youtube.com)
   - [Facebook](https://www.facebook.com)
   - [Instagram](https://www.instagram.com)
   - [TikTok](https://www.tiktok.com)
3. Ensure "Remember Me" is checked so sessions remain active.
4. Close Firefox before running the automation so the profile directory is unlocked.

---

## 🖥 Usage

### Option A: Graphical User Interface (GUI)

Launch the PyQt6 desktop app:

```bash
python gui.py
```

From the GUI you can:
- Select languages and topics for AI content generation.
- Choose whether to download fresh audio from Google Drive or use existing files.
- Toggle target publishing platforms (YouTube, Facebook, Instagram, TikTok).
- Trigger single uploads or schedule recurring batches.
- Monitor real-time logs and progress bars.

### Option B: CLI Automation Workflow

Run the full end-to-end headless pipeline:

```bash
python src/main.py
```

The CLI pipeline executes the following sequence:
1. Downloads a random audio track from Google Drive into `Audio/`.
2. Extends a random video from `Video/` to 60 seconds with the audio into `Output/output_60sec.mp4`.
3. Uploads sequentially to YouTube, Facebook, Instagram, and TikTok.
4. Logs results to `upload_log.txt`.

---

## 🔍 How It Works

| Module | Core Technology | Description |
|---|---|---|
| **AI Content** | xAI API (`requests`) | Sends structured prompt to `grok-2-1212` returning formatted multi-language text and English tags. |
| **Video Editing** | `moviepy` | Loops short clips (`concatenate_videoclips`), replaces audio, clips to 60.0s, and exports using `libx264`/`aac`. |
| **Web Automation** | `selenium`, `WebDriverWait` | Interacts with modern single-page web applications (SPA) using CSS selectors, file drop inputs, and keyboard events. |
| **Visual Button Detection** | `OpenCV` + `pyautogui` | Employs template matching (`cv2.matchTemplate`) for stubborn web UI elements that resist standard DOM events. |

---

## 🛠 Troubleshooting

- **GeckoDriver not found**:
  Ensure `geckodriver.exe` is in your project directory or in your system PATH (`C:\Windows\System32` or similar).
- **Firefox profile lock**:
  Close all active Firefox browser windows before starting the automation, as Firefox locks profile databases during active sessions.
- **AI Generation returns None**:
  Ensure your `GROK_API_KEY` is correctly defined in `.env` and that your xAI account has active API credits.
- **MoviePy write error**:
  Ensure FFmpeg is installed or accessible through `imageio-ffmpeg` (installed via `requirements.txt`).

---

## ⚖ Disclaimer & License

This project is intended for educational, research, and authorized personal content management purposes. Automated interactions with third-party platforms must comply with their respective Terms of Service:
- [YouTube Terms of Service](https://www.youtube.com/t/terms)
- [Meta Terms of Service](https://www.facebook.com/terms.php)
- [TikTok Terms of Service](https://www.tiktok.com/legal/page/row/terms-of-service/en)

Licensed under the [MIT License](LICENSE).

import math
import os
import random

from moviepy import (
    AudioFileClip,
    VideoFileClip,
    concatenate_audioclips,
    concatenate_videoclips,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path to src/

VIDEO_FOLDER = os.path.join(BASE_DIR, "Video")
AUDIO_FOLDER = os.path.join(BASE_DIR, "Audio")
OUTPUT_PATH = os.path.join(BASE_DIR, "Output", "output_60sec.mp4")


def extend_video_to_60s_with_audio():
    # Pick a random video
    video_file = random.choice(os.listdir(VIDEO_FOLDER))
    video_path = os.path.join(VIDEO_FOLDER, video_file)

    # Pick a random audio
    audio_file = random.choice(os.listdir(AUDIO_FOLDER))
    audio_path = os.path.join(AUDIO_FOLDER, audio_file)

    # Load video and remove existing audio
    clip = VideoFileClip(video_path).without_audio()

    # Calculate how many repeats needed to reach 60 seconds
    repeat_times = math.ceil(60 / clip.duration)

    # Create extended video clip
    final_clip = concatenate_videoclips([clip] * repeat_times)
    final_clip = final_clip.with_duration(60)

    # Load audio and set duration to 60s
    audio_clip = AudioFileClip(audio_path)
    if audio_clip.duration < 60:
        audio_clip = concatenate_audioclips(
            [audio_clip] * math.ceil(60 / audio_clip.duration)
        )
    audio_clip = audio_clip.subclipped(0, 60)
    final_clip = final_clip.with_audio(audio_clip)

    # Export final video
    final_clip.write_videofile(OUTPUT_PATH, codec="libx264", audio_codec="aac")

    print(f"Video extended with audio '{audio_file}' and saved successfully!")

    # Delete the used audio file
    # os.remove(audio_path)
    print(f"Deleted audio file: {audio_file}")


# Only run if this script is executed directly, not imported
if __name__ == "__main__":
    extend_video_to_60s_with_audio()

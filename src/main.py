import logging
import os
import time
from datetime import datetime

# Import modules
from download_audio import main as download_audio
from extend_video import extend_video_to_60s_with_audio
from facebook import Facebook
from instagram import Instagram
from src.tiktok import TikTokBot
from youtube import Youtube

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("upload_log.txt"), logging.StreamHandler()],
)


def ensure_folders_exist():
    """Ensure all required folders exist"""
    folders = ["Video", "Audio", "Output"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            logging.info(f"Created folder: {folder}")


def main():
    """Main automation workflow"""
    try:
        logging.info("=" * 60)
        logging.info("Starting Video Upload Automation")
        logging.info("=" * 60)

        # Ensure folders exist
        ensure_folders_exist()

        # Step 1: Download random audio from Google Drive
        logging.info("\n[STEP 1] Downloading random audio from Google Drive...")
        try:
            download_audio()
            logging.info("✓ Audio downloaded successfully")
        except Exception as e:
            logging.error(f"✗ Failed to download audio: {str(e)}")
            raise

        time.sleep(2)

        # Step 2: Create video with audio
        logging.info("\n[STEP 2] Creating 60-second video with audio...")
        try:
            extend_video_to_60s_with_audio()
            logging.info("✓ Video created successfully")
        except Exception as e:
            logging.error(f"✗ Failed to create video: {str(e)}")
            raise

        # Check if output video exists
        output_video = "Output/output_60sec.mp4"
        if not os.path.exists(output_video):
            raise FileNotFoundError(f"Output video not found: {output_video}")

        time.sleep(3)

        # Video metadata
        video_title = f"Amazing Video {datetime.now().strftime('%Y-%m-%d')}"
        video_caption = "Check out this amazing content! 🔥 #viral #trending"
        video_description = (
            "Don't forget to like, comment, and subscribe for more content!"
        )

        # Step 3: Upload to YouTube
        logging.info("\n[STEP 3] Uploading to YouTube...")
        youtube = None
        try:
            youtube = Youtube()
            youtube.upload_video(output_video, video_title, video_description)
            logging.info("✓ YouTube upload completed")
        except Exception as e:
            logging.error(f"✗ YouTube upload failed: {str(e)}")
        finally:
            if youtube:
                youtube.close()

        time.sleep(5)

        # Step 4: Upload to Facebook
        logging.info("\n[STEP 4] Uploading to Facebook...")
        facebook = None
        try:
            facebook = Facebook()
            facebook.upload_video(output_video, video_caption)
            logging.info("✓ Facebook upload completed")
        except Exception as e:
            logging.error(f"✗ Facebook upload failed: {str(e)}")
        finally:
            if facebook:
                facebook.close()

        time.sleep(5)

        # Step 5: Upload to Instagram
        logging.info("\n[STEP 5] Uploading to Instagram...")
        instagram = None
        try:
            instagram = Instagram()
            instagram.upload_video(output_video, video_caption)
            logging.info("✓ Instagram upload completed")
        except Exception as e:
            logging.error(f"✗ Instagram upload failed: {str(e)}")
        finally:
            if instagram:
                instagram.close()

        time.sleep(5)

        # Step 6: Upload to TikTok
        logging.info("\n[STEP 6] Uploading to TikTok...")
        tiktok = None
        try:
            tiktok = TikTokBot()
            tiktok.upload_video(output_video, artist_name="Oxlade")
            logging.info("✓ TikTok upload completed")
        except Exception as e:
            logging.error(f"✗ TikTok upload failed: {str(e)}")

        # Final summary
        logging.info("\n" + "=" * 60)
        logging.info("AUTOMATION COMPLETED!")
        logging.info("=" * 60)
        logging.info("All uploads have been processed.")
        logging.info(f"Check 'upload_log.txt' for detailed logs.")

    except Exception as e:
        logging.error(f"\n❌ CRITICAL ERROR: {str(e)}")
        logging.error("Automation stopped due to error.")
        raise


if __name__ == "__main__":
    main()

import logging
import os
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.driver_instance import DriverSetup


class Youtube:

    def __init__(self):
        self.driver = DriverSetup().driver
        self.wait = WebDriverWait(self.driver, 15)
        self.description = None  # Fixed typo: descritoption -> description

    def upload_video(self, video_path, title, description):
        """Upload video to YouTube"""
        try:
            if not self.driver:
                raise Exception("Driver not initialized properly")

            self.driver.get("https://studio.youtube.com/channel/UC/videos/upload")
            create_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[aria-label="Create"]')
                )
            )
            create_button.click()

            upload_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'tp-yt-paper-item[test-id="upload"]')
                )
            )
            upload_button.click()

            wait = WebDriverWait(self.driver, 10)
            file_path = os.path.abspath(video_path)
            file_input = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "input[type='file']",
                    )
                )
            )
            file_input.send_keys(file_path)
            print(f"Uploading video: {file_path}")

            print("File upload initiated successfully!")
            time.sleep(120)

            # Add title
            title_field = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        'div[aria-label*="Add a title that describes your video"]',
                    )
                )
            )
            title_field.clear()
            title_field.send_keys(title)

            # Add description
            description_field = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        'div[aria-label*="Tell viewers about your video"]',
                    )
                )
            )
            description_field.clear()
            description_field.send_keys(description)

            # Set as not made for kids
            kids_radio_btn = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        'tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_MFK"]',
                    )
                )
            )
            kids_radio_btn.click()

            # Click Next button (multiple times)
            for i in range(3):
                next_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, 'button[aria-label="Next"]')
                    )
                )
                next_button.click()
                time.sleep(1)

            # Set to public
            public_radio = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'tp-yt-paper-radio-button[name="PUBLIC"]')
                )
            )
            public_radio.click()

            # Publish
            publish_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[aria-label="Publish"]')
                )
            )
            publish_button.click()
            time.sleep(40)

            logging.info("Video uploaded successfully")
            self.driver.quit()

        except Exception as e:
            logging.error(f"Error uploading video: {str(e)}")
            raise

    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    youtube = Youtube()
    try:
        youtube.upload_video("video.mp4", "Video Title", "Video Description")
    finally:
        youtube.close()

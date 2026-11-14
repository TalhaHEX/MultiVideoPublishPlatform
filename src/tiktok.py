import os
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.driver_instance import DriverSetup


class TikTokBot:
    def __init__(self):
        self.driver = DriverSetup().driver
        self.wait = WebDriverWait(self.driver, 15)

    def close_content_check_modal(self):
        try:
            # Wait briefly for modal
            time.sleep(10)

            cancel_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button//*[text()='Cancel']/parent::button",
                    )
                )
            )
            cancel_btn.click()
            print("Popup detected → Cancel clicked.")
        except NoSuchElementException:
            print("No popup detected.")

    def upload_video(self, video_path, artist_name, description):
        self.driver.get("https://www.tiktok.com")
        url = "https://www.tiktok.com/tiktokstudio/upload"
        self.driver.get(url)
        time.sleep(5)
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
        time.sleep(30)
        print(f"Uploading video: {file_path}")
        editor = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.public-DraftEditor-content[contenteditable='true']",
                )
            )
        )
        self.driver.execute_script(
            "arguments[0].innerText = arguments[1];", editor, description
        )
        try:
            self.close_content_check_modal()
        except Exception as e:
            print(f"Error closing modal: {e}")

        # STEP 1 → Click "Edit video" button
        edit_btn = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(@class, 'TUXButton-label') and text()='Edit video']",
                )
            )
        )
        edit_btn.click()
        time.sleep(2)

        # STEP 2 → Type artist name in search bar
        search_bar = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']"))
        )
        search_bar.send_keys(f"{artist_name}")
        search_bar.send_keys(Keys.ENTER)
        time.sleep(3)  # wait for results to load

        # STEP 3 → Click first music card
        first_card = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "(//div[contains(@class, 'music-card-container')])[1]")
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView();", first_card)
        first_card.click()
        time.sleep(2)

        # STEP 4 → Click "Use" button on right side
        use_button = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(@class, 'TUXButton-label') and text()='Use']",
                )
            )
        )
        use_button.click()
        save_button = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(@class,'TUXButton-label') and text()='Save edit']/ancestor::button",
                )
            )
        )
        save_button.click()
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        post_button = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(@class,'Button__content') and text()='Post']/ancestor::button",
                )
            )
        )
        post_button.click()

        print("✔ Song selected successfully")
        time.sleep(10)  # wait for upload to complete
        self.driver.quit()


# if __name__ == "__main__":
#     bot = TikTokBot()
#     bot.upload_video("video.mp4")

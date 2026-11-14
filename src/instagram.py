import logging
import os
import time

import pyperclip
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.driver_instance import DriverSetup


class Instagram:
    def __init__(self):
        self.driver = DriverSetup().driver
        self.wait = WebDriverWait(self.driver, 15)

    def upload_video(self, video_path, caption):
        self.driver.get("https://www.instagram.com/")
        create_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Create')]"))
        )
        create_btn.click()
        time.sleep(5)
        post_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='Post']"))
        )
        post_btn.click()

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
        next_btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='button' and text()='Next']")
            )
        )
        next_btn.click()
        next_2_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='button' and normalize-space()='Next']")
            )
        )
        next_2_btn.click()
        time.sleep(2)
        caption_box = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
            )
        )
        caption_box.click()
        pyperclip.copy(caption)
        caption_box.send_keys(Keys.CONTROL, "v")
        time.sleep(20)
        share_btn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='button' and text()='Share']")
            )
        )
        share_btn.click()
        time.sleep(30)
        self.driver.quit()

    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    instagram = Instagram()
    try:
        instagram.upload_video("video.mp4", caption=None)
    finally:
        instagram.close()

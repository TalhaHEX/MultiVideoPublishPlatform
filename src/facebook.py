import logging
import os
import time

import cv2
import numpy as np
import pyautogui
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


class Facebook:
    def __init__(self):
        self.driver = DriverSetup().driver
        self.wait = WebDriverWait(self.driver, 15)

    def click_image(self, image_path, threshold=0.8, move_duration=0.2):
        """
        Searches the given image on the screen and clicks its center.

        Parameters:
            image_path (str): Path to the button/image you want to click.
            threshold (float): Template matching threshold.
            move_duration (float): Mouse movement speed.

        Returns:
            bool: True if clicked, False if not found.
        """

        # Load template/button image
        template = cv2.imread(image_path, 0)
        if template is None:
            print("Error: Image not found ->", image_path)
            return False

        w, h = template.shape[::-1]

        # Screenshot
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

        # Match template
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)

        # If found
        if len(loc[0]) > 0:
            # Click only first match
            pt = list(zip(*loc[::-1]))[0]
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2

            pyautogui.moveTo(center_x, center_y, duration=move_duration)
            pyautogui.click()

            print("Clicked:", image_path)
            return True

        print("Not found:", image_path)
        return False

    def upload_video(self, video_path, description, image_path):
        self.driver.get("https://www.facebook.com/")
        time.sleep(5)
        reel_btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[aria-label="Reel"][role="button"]')
            )
        )
        reel_btn.click()
        file_path = os.path.abspath(video_path)
        time.sleep(5)
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
        editor = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "div[contenteditable='true'][data-lexical-editor='true']",
                )
            )
        )
        text = f"{description}"
        pyperclip.copy(text)
        editor.click()
        editor.send_keys(Keys.CONTROL, "v")
        print(f"Uploading video: {file_path}")

        print("File upload initiated successfully!")

        self.click_image(f"{image_path}")
        time.sleep(5)
        # next_button_2 = self.wait.until(
        #     EC.element_to_be_clickable(
        #         (By.CSS_SELECTOR, 'div[aria-label="Next"][role="button"]')
        #     )
        # )

        # click the Next button
        # next_button_2.click()
        post_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[aria-label="Post"][role="button"]')
            )
        )

        # click the Post button
        post_button.click()
        time.sleep(30)
        self.driver.quit()

    def close(self):
        """Close the browser driver"""
        self.driver.quit()


if __name__ == "__main__":
    facebook = Facebook()
    try:
        facebook.upload_video("video.mp4")
    finally:
        facebook.close()

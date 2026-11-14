import os
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait


class DriverSetup:
    def __init__(self) -> None:
        """Setup Firefox driver with robust configuration"""
        self.driver = None
        self.wait = None
        self._setup_driver()

    def _setup_driver(self):
        """Internal method to configure and start the driver"""
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            options.set_preference("browser.tabs.remote.autostart", False)
            options.set_preference("browser.tabs.remote.autostart.2", False)
            options.set_preference("media.autoplay.default", 0)
            options.set_preference("media.autoplay.enabled", True)

            # Use existing profile if found
            try:
                profile_root = os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")
                default_profile = None
                if os.path.exists(profile_root):
                    for folder in os.listdir(profile_root):
                        if folder.endswith(".default-release"):
                            default_profile = os.path.join(profile_root, folder)
                            break
                if default_profile and os.path.exists(default_profile):
                    options.add_argument(f"-profile")
                    options.add_argument(default_profile)
                    print(f"Using Firefox profile: {default_profile}")
                else:
                    print("Using new Firefox profile")
            except Exception as profile_error:
                print(f"Could not load existing profile: {profile_error}")

            # Set binary location
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                "firefox",
            ]
            for path in firefox_paths:
                if os.path.exists(path) or path == "firefox":
                    try:
                        options.binary_location = path
                        print(f"Using Firefox binary: {path}")
                        break
                    except:
                        continue

            # Setup geckodriver
            service = None
            geckodriver_paths = [
                "geckodriver.exe",
                "geckodriver",
                r"C:\geckodriver.exe",
                os.path.join(os.getcwd(), "geckodriver.exe"),
            ]
            for driver_path in geckodriver_paths:
                if os.path.exists(driver_path) or driver_path in [
                    "geckodriver.exe",
                    "geckodriver",
                ]:
                    service = Service(executable_path=driver_path)
                    print(f"Using geckodriver: {driver_path}")
                    break
            if not service:
                service = Service()
                print("Using default geckodriver location")

            # Launch Firefox with retry
            for attempt in range(3):
                try:
                    print(f"Starting Firefox (attempt {attempt + 1}/3)...")
                    self.driver = webdriver.Firefox(service=service, options=options)
                    self.wait = WebDriverWait(self.driver, 20)
                    self.driver.get("https://www.google.com")
                    time.sleep(2)
                    print("Firefox driver setup successfully ✅")
                    return  # Successfully initialized
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = None
                    if attempt < 2:
                        time.sleep(5)
                    else:
                        raise e

        except Exception as e:
            print(f"Browser setup error: {e}")
            print("Troubleshooting tips:")
            print("1. Ensure Firefox is installed")
            print("2. Ensure geckodriver is in the same folder or PATH")
            print("3. Close all Firefox windows and retry")
            print("4. Disable antivirus temporarily if blocking")
            raise

    def close(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

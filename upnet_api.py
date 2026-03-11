import time
import re
from selenium import webdriver
import platform
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

class UpnetScraper:
    def __init__(self):
        self.options = Options()
        self.os_name = platform.system()
        self.driver = None

    def start_browser(self):
        print(f"Launching Browser for {self.os_name}...")

        if self.os_name == "Windows":
            # --- WINDOWS SETUP ---
            # Windows uses standard Google Chrome. No special sandbox or binary flags needed.
            driver_manager = ChromeDriverManager().install()
            self.driver = webdriver.Chrome(
                service=Service(driver_manager),
                options=self.options
            )

        else:
            print("Launching Chromium...")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shm-usage")

            # Explicitly tell Selenium to use Chromium, not Google Chrome
            self.options.binary_location = "/usr/bin/chromium-browser"
            # This automatically finds the correct driver for Chromium
            driver_manager = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
            self.driver = webdriver.Chrome(
                service=Service(driver_manager),
                options=self.options
            )

        self.driver.get("https://progress.upatras.gr")

    def _recursive_frame_search(self, depth=0):
        try:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            # Look for keywords that appear on the grades page
            if "Εξάμηνο" in body_text and ("CEID" in body_text or "Βαθμός" in body_text):
                print(f" Data found in Layer {depth}!")
                return body_text
        except:
            pass

        frames = self.driver.find_elements(By.TAG_NAME, "iframe") + \
                 self.driver.find_elements(By.TAG_NAME, "frame")
        
        for frame in frames:
            try:
                self.driver.switch_to.frame(frame)
                result = self._recursive_frame_search(depth + 1)
                if result: return result
                self.driver.switch_to.parent_frame()
            except:
                self.driver.switch_to.default_content()
        return None

    def parse_grades(self, raw_text):
        print("\nParsing Grades...")
        lines = raw_text.split('\n')
        student_data = []
        regex = r"(CEID_\w+)\s+(.+?)\s+(\d{1,2}[.,]\d{2}|\d{1,2})"

        for line in lines:
            if "CEID" in line:
                match = re.search(regex, line)
                if match:
                    grade_clean = match.group(3).replace(',', '.')
                    name_clean = re.sub(r'\d{4}-\d{2}.*', '', match.group(2)).strip()
                    try:
                        if float(grade_clean) <= 10.0:
                            student_data.append({
                                "code": match.group(1),
                                "name": name_clean[:40],
                                "grade": grade_clean
                            })
                    except: continue
        return student_data

    def fetch_grades_manual(self):
        if not self.driver: self.start_browser()

        print("\nACTION REQUIRED: Log in & Solve CAPTCHA in the Progress: Φοιτητής -> Ακαδημαϊκό Έργο window!")
        input("Once you see the grades table, click back here and press [ENTER]...")
        
        print("Scanning...")
        found_text = self._recursive_frame_search()
        
        if not found_text:
            print("No grades found. Are you on the right page?")
            return []

        data = self.parse_grades(found_text)
        print(f"Extracted {len(data)} courses.")
        return data

    def close(self):
        if self.driver: self.driver.quit()

if __name__ == "__main__":
    scraper = UpnetScraper()
    try:
        data = scraper.fetch_grades_manual()
        for d in data:
            print(d)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # scraper.close() # Keep browser open to debug if needed
        pass
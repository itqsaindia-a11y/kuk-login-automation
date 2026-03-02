from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

driver.get("https://ol.kukonline.in/login")

time.sleep(3)

driver.find_element(By.ID,"username").send_keys("11949271")
driver.find_element(By.ID,"password").send_keys("11949271_1")

driver.find_element(By.ID,"user-sign-in").click()

time.sleep(5)

driver.quit()

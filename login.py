import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

driver = webdriver.Chrome()

driver.get("https://ol.kukonline.in/login")

time.sleep(3)

driver.find_element(By.ID,"username").send_keys(username)
driver.find_element(By.ID,"password").send_keys(password)

driver.find_element(By.ID,"user-sign-in").click()

time.sleep(5)

driver.quit()

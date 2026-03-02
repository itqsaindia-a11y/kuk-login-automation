import os
import smtplib
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def send_mail(subject, message):

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)

        msg = f"Subject: {subject}\n\n{message}"

        server.sendmail(
            EMAIL_USER,
            "aashishhr05@gmail.com",
            msg
        )

        server.quit()

    except Exception as e:
        print("Mail error:", e)


try:

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    driver.get("https://ol.kukonline.in/login")

    time.sleep(3)

    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)

    driver.find_element(By.ID, "user-sign-in").click()

    time.sleep(5)

    send_mail(
        "KUK Auto Login SUCCESS",
        "Login completed successfully."
    )

    driver.quit()

except Exception as e:

    send_mail(
        "KUK Auto Login FAILED",
        str(e)
    )

import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def send_email(status, script_status, message, screenshot_path=None):
    """Send email with complete status information"""
    
    sender_email = os.getenv("EMAIL_USERNAME")
    sender_password = os.getenv("EMAIL_PASSWORD")
    receiver_email = sender_email
    
    # Current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    
    # Determine emoji and color based on ACTUAL login status
    if status == "success":
        main_status = "✅ LOGIN SUCCESSFUL"
        main_color = "green"
    else:
        main_status = "❌ LOGIN FAILED"
        main_color = "red"
    
    # Script execution status
    script_icon = "✅" if script_status == "success" else "❌"
    
    # Create HTML email
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>Auto Login Report</h2>
        <p><strong>Time:</strong> {current_time}</p>
        
        <div style="padding: 15px; border-radius: 5px; background-color: #f5f5f5;">
          <p><strong>Script Execution:</strong> {script_icon} {script_status.upper()}</p>
          <p><strong style="color: {main_color};">Actual Login Status: {main_status}</strong></p>
          <p><strong>Message:</strong> {message}</p>
        </div>
        
        <hr>
        <p><small>GitHub Run: <a href="${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}">View Logs</a></small></p>
      </body>
    </html>
    """
    
    # Setup email
    msg = MIMEMultipart()
    msg['Subject'] = f"{'✅' if status == 'success' else '❌'} Auto Login - {current_time}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.attach(MIMEText(body, 'html'))
    
    # Attach screenshot if login failed
    if screenshot_path and os.path.exists(screenshot_path) and status == "failed":
        with open(screenshot_path, 'rb') as f:
            img_data = f.read()
            image = MIMEImage(img_data, name=os.path.basename(screenshot_path))
            msg.attach(image)
    
    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("📧 Email sent!")
        return True
    except Exception as e:
        print(f"❌ Email failed: {str(e)}")
        return False

def check_actual_login(driver):
    """Check if ACTUALLY logged into website"""
    try:
        # Wait for page to change/load after login
        time.sleep(5)
        
        # Check 1: URL change (not on login page anymore)
        current_url = driver.current_url
        if "login" not in current_url.lower():
            return True, "Redirected away from login page"
        
        # Check 2: Look for logout button
        logout_elements = driver.find_elements(By.XPATH, "//*[contains(text(),'Logout')]")
        logout_elements += driver.find_elements(By.XPATH, "//*[contains(text(),'Sign Out')]")
        if logout_elements:
            return True, "Found Logout button"
        
        # Check 3: Look for user dashboard elements
        dashboard_elements = driver.find_elements(By.CLASS_NAME, "dashboard")
        dashboard_elements += driver.find_elements(By.ID, "welcome")
        if dashboard_elements:
            return True, "Found dashboard elements"
        
        # Check 4: Look for error messages (login failed)
        error_elements = driver.find_elements(By.CLASS_NAME, "error")
        error_elements += driver.find_elements(By.CLASS_NAME, "alert-danger")
        error_elements += driver.find_elements(By.XPATH, "//*[contains(text(),'Invalid')]")
        
        if error_elements:
            error_text = error_elements[0].text[:100]  # First 100 chars
            return False, f"Error shown: {error_text}"
        
        # If still on login page with no errors
        if "login" in current_url.lower():
            return False, "Still on login page - might be stuck"
        
        return False, "Unknown - couldn't verify login status"
        
    except Exception as e:
        return False, f"Check failed: {str(e)}"

def main():
    # Credentials
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    
    if not username or not password:
        print("❌ No credentials!")
        return
    
    script_status = "success"  # Assume success unless error occurs
    driver = None
    screenshot_path = None
    
    try:
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        
        print("🚀 Starting browser...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Go to login page
        print("📱 Opening website...")
        driver.get("https://ol.kukonline.in/login")
        time.sleep(3)
        
        # Fill login form
        print("👤 Entering username...")
        driver.find_element(By.ID, "username").send_keys(username)
        
        print("🔑 Entering password...")
        driver.find_element(By.ID, "password").send_keys(password)
        
        # Click login
        print("🖱 Clicking login button...")
        driver.find_element(By.ID, "user-sign-in").click()
        
        # Wait for login to process
        time.sleep(8)
        
        # Take screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"login_{timestamp}.png"
        driver.save_screenshot(screenshot_path)
        print("📸 Screenshot saved")
        
        # Check ACTUAL login status
        login_success, message = check_actual_login(driver)
        
        if login_success:
            print(f"✅ ACTUAL LOGIN SUCCESSFUL! {message}")
            # Only email for failures, so no email for success
            # But you can still log it
            with open("login_history.txt", "a") as f:
                f.write(f"{datetime.now()}: SUCCESS - {message}\n")
        else:
            print(f"❌ ACTUAL LOGIN FAILED! {message}")
            # Send email ONLY for failures
            send_email(
                status="failed",
                script_status=script_status,
                message=f"Login failed: {message}",
                screenshot_path=screenshot_path
            )
        
    except Exception as e:
        script_status = "failed"
        error_msg = f"Script error: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Save error screenshot
        if driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"error_{timestamp}.png"
            driver.save_screenshot(screenshot_path)
        
        # Send email for script errors too
        send_email(
            status="failed",
            script_status="failed",
            message=error_msg,
            screenshot_path=screenshot_path
        )
        
    finally:
        if driver:
            driver.quit()
            print("👋 Browser closed")

if __name__ == "__main__":
    main()

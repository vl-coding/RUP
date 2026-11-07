from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def clock(in_or_out):
    # Define credentials and URLs
    login_url = "https://hrms.example.com/psp/HRMS1/EMPLOYEE/HRMS/c/ROLE_EMPLOYEE.TL_SS_JOB_SRCH_CLK.GBL?NAVSTACK=Clear&PORTALPARAM_PTCNAV=HC_TL_SS_JOB_SRCH_CLK_GBL&EOPP.SCNode=HRMS&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=PT_PTPP_PORTAL_ROOT&EOPP.SCLabel=Time%2520Reporting&EOPP.SCFName=HC_TIME_REPORTING&EOPP.SCSecondary=true&EOPP.SCPTfname=HC_TIME_REPORTING&FolderPath=PORTAL_ROOT_OBJECT.CO_EMPLOYEE_SELF_SERVICE.HC_TIME_REPORTING.HC_RECORD_TIME.HC_TL_SS_JOB_SRCH_CLK_GBL&IsFolder=false"
    clock_url = "https://hrms.example.com/psp/HRMS1/EMPLOYEE/HRMS/c/ROLE_EMPLOYEE.TL_SS_JOB_SRCH_CLK.GBL?NAVSTACK=Clear&PORTALPARAM_PTCNAV=HC_TL_SS_JOB_SRCH_CLK_GBL&EOPP.SCNode=HRMS&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=PT_PTPP_PORTAL_ROOT&EOPP.SCLabel=Time%2520Reporting&EOPP.SCFName=HC_TIME_REPORTING&EOPP.SCSecondary=true&EOPP.SCPTfname=HC_TIME_REPORTING&FolderPath=PORTAL_ROOT_OBJECT.CO_EMPLOYEE_SELF_SERVICE.HC_TIME_REPORTING.HC_RECORD_TIME.HC_TL_SS_JOB_SRCH_CLK_GBL&IsFolder=false"
    credentials = {
        "username": os.getenv("RUTGERS_NETID"),
        "password": os.getenv("RUTGERS_PASSWORD")
    }
    # hide browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (recommended for headless mode)
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size for consistent behavior
    chrome_options.add_argument("--no-sandbox")  # Add for better compatibility on some systems
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    # Set up WebDriver
    service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Step 1: Log in
        driver.get(login_url)
        time.sleep(1)

        
        try:
            # Enter username and password
            driver.find_element(By.NAME, "username").send_keys(credentials["username"])
            driver.find_element(By.NAME, "password").send_keys(credentials["password"])
            driver.find_element(By.NAME, "submit").click()

            # driver.find_element(By.ID, "trust-browser-button").click()
            trust = WebDriverWait(driver, 300).until(
                EC.visibility_of_element_located((By.ID, "trust-browser-button"))
            )
            trust.click()
            time.sleep(10)

            # switch to iframe
            driver.switch_to.frame(driver.find_element(By.ID, "ptifrmtgtframe"))
            time.sleep(1)

            # select desired way to clock - in / out
            dropdown = driver.find_element(By.NAME, "TL_RPTD_TIME_PUNCH_TYPE$0")
            select = Select(dropdown)
            if(in_or_out == 1):
                select.select_by_index(1)
            elif(in_or_out == 0):
                select.select_by_index(3)
            time.sleep(1)
            
            # submit clocking
            driver.find_element(By.ID, "TL_LINK_WRK_TL_SAVE_PB$0").click()
            time.sleep(5)

            # close out of it
            driver.find_element(By.ID, "DERIVED_ETEO_SAVE_PB").click()
            time.sleep(2)

            # send email to confirm
            message = MIMEMultipart()
            message["From"] = os.getenv("GMAIL_ADDRESS")
            message["To"] = os.getenv("GMAIL_ADDRESS")

            if(in_or_out == 1):
                body = "This to confirm you have clocked in for today."
            elif(in_or_out == 0):
                body = "This to confirm you have clocked out for today"

            message.attach(MIMEText(body, "plain"))
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # Upgrade the connection to secure
                server.login(os.getenv("GMAIL_ADDRESS"), os.getenv("GMAIL_APP_PASSWORD"))
                server.sendmail(os.getenv("GMAIL_ADDRESS"), os.getenv("GMAIL_ADDRESS"), message.as_string())
        except Exception as e:
            print("Error during interaction or clocking in or out:", str(e))
    finally:
        driver.quit()

# Schedule the job
# Monday
schedule.every().monday.at("10:00").do(clock, 1)  # Monday - clockin at 10 AM
schedule.every().monday.at("14:00").do(clock, 0) # Monday - clockout at 2 PM

#Tuesday
schedule.every().tuesday.at("18:00").do(clock, 1) # Tuesday - clockin at 6 PM
schedule.every().tuesday.at("20:00").do(clock, 0) # Tuesday - clockout at 8 PM

# # Wednesday
# schedule.every().wednesday.at("").do(clock, 1) 
# schedule.every().wednesday.at("").do(clock, 0) 

# Thursday
schedule.every().thursday.at("10:00").do(clock, 1) # Thursday - clockin at 10 AM
schedule.every().thursday.at("14:00").do(clock, 0) # Thursday - clockout at 2 PM

# # Friday
# schedule.every().friday.at("").do(clock, 1)
# schedule.every().friday.at("").do(clock, 0)

# # Keep the script running
# while True:
#     schedule.run_pending()  # Check if any scheduled task is due to run
#     time.sleep(1)  # Sleep for a second to avoid high CPU usage

filename = "clocking.text"

# Try to read the current state from the file
try:
    with open(filename, 'r') as file:
        current_value = int(file.read().strip())
except FileNotFoundError:
    pass

# Flip the value
new_value = 1 if current_value == 0 else 0

# Save the new value back to the file
with open(filename, 'w') as file:
    file.write(str(new_value))

# Print the new value to confirm
if(new_value == 0):
    print("Now clocking out...")
elif(new_value == 1):
    print("Now clocking in...")
clock(new_value)
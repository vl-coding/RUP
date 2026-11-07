from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time
from webdriver_manager.chrome import ChromeDriverManager

def generate_link(isbn, title):     
    # Define credentials and URLs
    login_url = "https://ebook-vault.example.com/BV.login.epl?bv.mybooks.epl"
    data_url = f"https://ebook-vault.example.com/bv.mybooks.epl?pc=all&mybooks=certainbooks&findtype=ISBN&certainvalue={isbn}&aretoggle=1&availability=job_ccpy_20_32&metadataitem=10&metadatavalue=2024&fileformat=all&filestatus=&filetype="
    data_url_2 = f"https://ebook-vault.example.com/bv.mybooks.epl?pc=all&mybooks=certainbooks&findtype=title&certainvalue={title.replace(" ", "+") }&aretoggle=1&availability=job_ccpy_20_32&metadataitem=10&metadatavalue=2024&fileformat=all&filestatus=&filetype=" 
    credentials = {
        "username": os.getenv("BIBLIOVAULT_USERNAME"),
        "password": os.getenv("BIBLIOVAULT_PASSWORD")
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

        # Enter username and password
        driver.find_element(By.NAME, "username").send_keys(credentials["username"])
        driver.find_element(By.NAME, "password").send_keys(credentials["password"])
        driver.find_element(By.NAME, "login").click()
        time.sleep(1)

        # Step 2: Navigate to the ISBN search result
        try:
            driver.get(data_url)
        except Exception:
            driver.get(data_url_2)
        time.sleep(1)

        # Step 3: Interact with the page to generate the desired link
        # Adjust selectors to match the website's structure and elements
        try:
            # Navigate to overview
            overview = driver.find_element(By.PARTIAL_LINK_TEXT, f"{title[0:int(len(title)*0.75)]}")
            overview.click()
            time.sleep(1)

            # navigate to link generation
            try:
                link_element = driver.find_element(By.LINK_TEXT, "Make Comp Copy Link")
                if(link_element.is_displayed):
                    driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
                    time.sleep(1)
                    link_element.click()
                    time.sleep(1)

                    # customize link generation
                    try:
                        if(driver.find_element(By.ID, "ePubDE").is_displayed()):
                            settings = driver.find_element(By.ID, "ePubDE")
                            settings.click()
                    except Exception:
                        pass
                    settings = driver.find_element(By.ID, "noprint")
                    settings.click()
                    settings = driver.find_element(By.ID, "nocopy")
                    settings.click()
                    settings = driver.find_element(By.ID, "extraRights_lrt")
                    settings.send_keys("180")
                    settings = driver.find_element(By.NAME, "GenHere")
                    driver.execute_script("arguments[0].scrollIntoView(true);", settings)
                    time.sleep(1)
                    settings.click()
                    time.sleep(1)
                    
                    # # Copy the link to clipboard
                    generated_link = driver.find_element(By.PARTIAL_LINK_TEXT, "https://ebook-vault.example.com/cgi-bin/DeliverADE.epl?transid=")
                    return generated_link.text
            except Exception:
                print("link not available")
                return None

        except Exception as e:
            print(f"Error during interaction or link generation of {title} ({isbn}):", str(e))
            return None
    finally:
        # Step 4: Close the browser
        driver.quit()
# link = generate_link(9780813551562, "The New Anthology of American Poetry")
# print( link )
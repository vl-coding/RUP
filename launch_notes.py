from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

# def launch_notes():
# notes = input("What are the launch notes?\n")

login_url = "https://tme.firebrandtech.com/RUP/TmmWeb/User/Login"
launch_notes_url = "https://tme.firebrandtech.com/RUP/TmmWeb/Home"
credentials = {
    "username": os.getenv("FIREBRAND_USERNAME"),
    "password": os.getenv("FIREBRAND_PASSWORD")
}
# hide browser
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (recommended for headless mode)
chrome_options.add_argument("--window-size=1920,1080")  # Set window size for consistent behavior
chrome_options.add_argument("--no-sandbox")  # Add for better compatibility on some systems
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

# Set up WebDriver
service = Service('RUP/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service)
# driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Step 0: Gather info
    try:
        with open('RUP/launch_notes.text', 'r') as file:
            launch_notes = file.readlines()
            info = []
            for row in launch_notes:
                info.append(row.strip())       
    except FileNotFoundError:
        pass
    inform = {}
    author = info[0].split(", ")[0].split(" ")
    inform["author"] = author[len(author) - 1]
    inform["title"] = info[0].split(", ")[1].split(": ")[0].strip()
    inform["publisher"] = "Rutgers University Press"
    inform["pb_price"] = (info[4].split(": ")[1].split(" / ")[0].removeprefix("$").removesuffix("pb").strip()) 
    inform["hc_price"] = (info[4].split(": ")[1].split(" / ")[1].removeprefix("$").removesuffix("hc").strip()) 
    inform["inst_price"] = (info[5].split(": ")[1].removeprefix("$").strip()) # institutional price
    inform["pb_disc"] = (info[6].split(": ")[1].split(" / ")[0].strip()) # paperback discount
    inform["hc_disc"] = (info[6].split(": ")[1].split(" / ")[1].strip()) # hardcover discount
    inform["jackets"] = (info[9].strip()) # jacket subjects
    inform["collections"] = (info[14].split(": ")[1].strip()) # collections

    length = info[17].split(": ")[1].split(" x ")[0].split("-")
    if(len(length) > 1):
        length = (int(length[0]) + float(length[1].split("/")[0]) / float(length[1].split("/")[1])) # trim - length
    else:
        length = (int(length[0]))
    inform["length"] = length
    
    width = info[17].split(": ")[1].split(" x ")[1].split("-")
    if(len(width) > 1):
        width = (int(width[0]) + (float(width[1].split("/")[0]) / float(width[1].split("/")[1]))) # trim - width
    else:
        width = (int(width[0]))
    inform["width"] = width

    inform["pages"] = (int(info[18].split(": ")[1].strip())) # page count
    inform["images"] = (info[19].split(": ")[1].strip()) # images

    inform["pub_month"] = (info[21].split(": ")[1].split(", ")[0].split(" ")[0].strip().lower().title()) # pub date - month
    inform["pub_year"] = (info[21].split(": ")[1].split(", ")[1].strip()) # pub date - year

    # for i in inform.keys():
    #     print(i, inform[i])

    # Step 1: Log in
    driver.get(login_url)
    time.sleep(1)

    # Enter username and password
    driver.find_element(By.NAME, "username").send_keys(credentials["username"])
    driver.find_element(By.NAME, "password").send_keys(credentials["password"])
    driver.find_element(By.XPATH, "//input[@type='submit' and @value='Sign in']").click()
    time.sleep(1)

    # Step 2: open FireBrand
    driver.get(launch_notes_url)
    time.sleep(1)

    # Step 3: Interact with the page to update publishings' information
    try:
        # navigate to primary version of publishing
        driver.get("https://tme.firebrandtech.com/RUP/TmmWeb/Search/1/6")
        driver.find_element(By.ID, "Search_CriteriaDetailItems_0__StringValue").send_keys(inform["title"])
        driver.find_element(By.ID, "Search_CriteriaDetailItems_1__StringValue").send_keys(inform["author"])
        # editor = driver.find_element(By.ID, "Search_OrgLevels_0__OrgEntryKey")
        # select = Select(editor)
        # select.select_by_value("18")
        # time.sleep(1)
        driver.find_element(By.XPATH, "//*[@id='search-criteria-find-area']/button").click()
        time.sleep(3)

        driver.find_element(By.LINK_TEXT, f"{inform["title"]}").click()
        time.sleep(4)

        # set publisher date
        driver.find_element(By.ID, "shTitleInfobtnSectionEdit").click()
        time.sleep(1)
    
        month = driver.find_element(By.ID, "Product_PubMonthCode")
        if(month.get_attribute("title").__contains__(inform["pub_month"]) == False):
            select = Select(month)
            select.select_by_visible_text(inform["pub_month"])

        year = driver.find_element(By.ID, "Product_PubYear")
        if(year.get_attribute("value").__contains__(inform["pub_year"]) == False):
            year.send_keys(inform["pub_year"])

        driver.find_element(By.ID, "shTitleInfobtnSectionView").click()
        time.sleep(1)

        # set price
        driver.find_element(By.ID, "shPricesbtnSectionEdit").click()
        driver.find_element(By.ID, "shPricesbtnSectionAdd").click()
        # price_input = driver.find_elements(By.CLASS_NAME, "price-type-selector refresh-section-trigger")
        # print(price_input)
        
        
        # driver.find_element(By.ID, "").send_keys()

        time.sleep(300)

    except Exception as e:
        print("Error during interaction or launch notes updating:", str(e))
finally:
    # Step 4: Close the browser
    driver.quit()
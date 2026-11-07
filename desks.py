from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import os
import time
from AIAdressFinder import address_with_gpt
from webdriver_manager.chrome import ChromeDriverManager

def us_state_conversion(input):
    us_states = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DC": "District of Columbia",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming"
    }
    for i in us_states:
        if(input.upper() == i):
            return us_states[i]
        if(input.upper() == us_states[i].upper()):
            return input
    return "Foreign or Canadian?"

def print_desk(info):
    isbn = info["isbn"]
    last_name = info["last name"]
    street_address = info["street address"]
    street_address2 = info["street address 2"]
    city = info["city"]
    state = info["state"]
    zipcode = info["zipcode"]
    country = info["country"]
    publisher = info["publisher"]
    purchase_no = f"Bh Desk {last_name}"
    address_type = ""
    email = ""
    phone_no = ""

    for i in str(zipcode):
        # letter = False
        states = ( (us_state_conversion(state)) == "Foreign or Canadian?" ) # true --> Foreign / Canadian
        if((i not in str([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "-"])) or states):
            # letter = True
            if(street_address2 is not None):
                full_address = f"{street_address}, {street_address2}, {city}, { state } {zipcode}"
            else:
                full_address = f"{street_address}, {city}, { state } {zipcode}"
            address_type, extra = address_with_gpt(full_address)
            # address_type, extra = ('Foreign', 'Australia')
            if(address_type == "Foreign"):
                country = extra
            elif(address_type == "Canadian"):
                state = extra
            break
        else:
            address_type = "Domestic"

    # Define credentials and URLs
    login_url = "https://distribution-center.example.com/cdcreporting/"
    order_url = "https://distribution-center.example.com/cdcreporting/cdcrptComps.aspx"
    credentials = {
        "username": os.getenv("CDC_USERNAME"),
        "password": os.getenv("CDC_PASSWORD")
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
    # driver = webdriver.Chrome(service=service) # use instead when testing
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Step 1: Log in
        driver.get(login_url)
        time.sleep(1)

        # Enter username and password
        driver.find_element(By.ID, "ContentPlaceHolder1_txtUserID").send_keys(credentials["username"])
        driver.find_element(By.ID, "ContentPlaceHolder1_txtPassword").send_keys(credentials["password"])
        driver.find_element(By.ID, "ContentPlaceHolder1_btnLogin").click()
        time.sleep(1)

        # Step 2: Navigate to the Comp Copy Order Entry
        driver.get(order_url)
        time.sleep(1)

        # Step 3: Interact with the page to send the order
        try:
            # input publisher
            publisher_element = driver.find_element(By.ID, "ContentPlaceHolder1_ddlPublisher")
            publisher_element.send_keys(publisher)
            time.sleep(1)

            # start an order
            order_element = driver.find_element(By.ID, "ContentPlaceHolder1_lbtnAddNew")
            order_element.click()
            time.sleep(1)
            # inputs
            order_element = driver.find_element(By.ID, "ContentPlaceHolder1_ddlAccounts")
            select = Select(order_element)
            select.select_by_index(1)
            order_element = driver.find_element(By.ID, "ContentPlaceHolder1_ddlTracking")
            select = Select(order_element)
            select.select_by_index(1)
            order_element = driver.find_element(By.ID, "ContentPlaceHolder1_txtPurchaseOrder")
            order_element.send_keys(purchase_no)
            order_element = driver.find_element(By.ID, "ContentPlaceHolder1_btnNext")
            order_element.click()
            time.sleep(1)

            # input address information
            if(address_type == "Domestic"):
                address_element = driver.find_element(By.ID, "ContentPlaceHolder1_rblAddressType_0") 
            elif(address_type == "Canadian"):
                address_element = driver.find_element(By.ID, "ContentPlaceHolder1_rblAddressType_1")
            elif(address_type == "Foreign"):
                address_element = driver.find_element(By.ID, "ContentPlaceHolder1_rblAddressType_2")
            address_element.click()
            time.sleep(1)
            address_element = driver.find_element(By.ID, "ContentPlaceHolder1_lbtnContinueShip")
            address_element.click()
            address_element = driver.find_element(By.ID, "ContentPlaceHolder1_txtLastName")
            address_element.send_keys(last_name)
            address_element = driver.find_element(By.ID, "ContentPlaceHolder1_txtAddress1")
            address_element.send_keys(street_address)
            address_element = driver.find_element(By.ID, "ContentPlaceHolder1_txtAddress2")
            address_element.send_keys(street_address2)
            address_element = driver.find_element(By.ID, "ContentPlaceHolder1_txtCity")
            address_element.send_keys(city)
            address_element = driver.find_element(By.ID, "ContentPlaceHolder1_ddlStates")
            select = Select(address_element)
            if(address_type == "Domestic"):
                select.select_by_visible_text( us_state_conversion(state) )
            elif(address_type == "Foreign"):
                address_element = driver.find_element(By.ID, "ContentPlaceHolder1_ddlCountry")
                select = Select(address_element)
                select.select_by_visible_text( country.upper() )
            elif(address_type == "Canadian"):
                select.select_by_visible_text( state )
            time.sleep(1)
            address_element = driver.find_element(By.ID, "ContentPlaceHolder1_txtZipCode")
            address_element.send_keys(zipcode)
            address_element = driver.find_element(By.ID, "ContentPlaceHolder1_btnNext2")
            address_element.click()
            time.sleep(1)

            # confirm address
            try:
                if(driver.find_element(By.ID, "ContentPlaceHolder1_hbtnOk").is_displayed()):
                    driver.find_element(By.ID, "ContentPlaceHolder1_hbtnOk").click()
                    time.sleep(1)
                    driver.find_element(By.ID, "ContentPlaceHolder1_btnAcceptChanges").click()
                    time.sleep(1)
            except Exception:
                driver.quit()
                print("Print Desk Copy Order NOT COMPLETED...  Address not valid")
                return False
            time.sleep(1)

            # input isbn
            isbn_element = driver.find_element(By.NAME, "ctl00$ContentPlaceHolder1$txtISBN")
            isbn_element.send_keys(isbn)
            isbn_element = driver.find_element(By.ID, "ContentPlaceHolder1_btnISubmit")
            isbn_element.click()
            time.sleep(1)
            isbn_element = driver.find_element(By.ID, "ContentPlaceHolder1_txtQty")
            isbn_element.send_keys(1)
            if driver.find_element(By.ID, "ContentPlaceHolder1_hbtnOk").is_displayed():
                driver.find_element(By.ID, "ContentPlaceHolder1_hbtnOk").click()
                time.sleep(1)
            else:
                isbn_element = driver.find_element(By.ID, "ContentPlaceHolder1_btnIRecord")
                isbn_element.click()
                time.sleep(1)
            
            # if backordering
            if(driver.find_element(By.ID, "ContentPlaceHolder1_hbtnOk").is_displayed()):
                driver.find_element(By.ID, "ContentPlaceHolder1_hbtnOk").click()
                time.sleep(1)
            # finalize order
            finalize_element = driver.find_element(By.ID, "ContentPlaceHolder1_btnReview")
            finalize_element.click()
            time.sleep(1)

            # shipping selections order
            shipping_element = driver.find_element(By.ID, "ContentPlaceHolder1_ddlPBShipping")
            select = Select(shipping_element)
            select.select_by_index(1)
            time.sleep(1)
            if(address_type != "Domestic"):
                email_element = driver.find_element(By.ID, "ContentPlaceHolder1_txtContactPhone")
                email_element.send_keys(email)
                phone_no_element = driver.find_element(By.ID, "ContentPlaceHolder1_txtRecipientPhone")
                phone_no_element.send_keys(phone_no)

            # accept order
            confirmation_element = driver.find_element(By.ID, "ContentPlaceHolder1_chkAccept")
            confirmation_element.click() 
            time.sleep(1)

            # close out of it
            close_element = driver.find_element(By.ID, "ContentPlaceHolder1_btnConfirm")
            close_element.click() ## when testing, comment out
            time.sleep(1)

            print("Print Desk Order Completed...")
            return True

        except Exception as e:
            print("Error during interaction or print desk copy ordering:", str(e))
            return False

    finally:
        # Step 4: Close the browser
        driver.quit()
# print( print_desk( {'email': 'professor@example.edu', 'first name': 'Jane', 'title': 'Sample Book Title', 'publisher': 'Rutgers University Press', 'phone_no': '(555) 555-0100', 'format': 'Print and Electronic Desk', 'last name': 'Doe', 'street address': '123 Example St', 'street address 2': '', 'city': 'Exampleton', 'state': 'NJ', 'zipcode': '08901', 'country': '', 'link': None, 'isbn': 9780813541969, 'notes': 'Cannot Make Comp Copy Link', 'status': ''} ) )
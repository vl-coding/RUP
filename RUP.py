import streamlit as st
import pandas as pd
import os
from threading import Lock
from datetime import datetime
from RUP import make_email_content, gather_info, print_desk

# Initialize lock for thread-safe file writing
file_lock = Lock()

# Define column order from csv file
excel_columns = [
    "Submission Date", 
    "Is this a desk copy request or an exam copy request?", "Do you want a print copy or an electronic copy or both?", 
    "Book Title", "Book Author/Editor", "Paperback ISBN", "Publication Date", 
    "First Name", "Last Name",
    "Title", "Department", "University", "Course Title", 
    "Email", "Phone Number",
    "Street Address", "Street Address Line 2", "City", "State / Province", "Postal / Zip Code", "Country",
    "How likely are you to adopt this book for your classroom?", "How did you hear about the book?", 
    "Your Note", "Course Title and Number", "Date When the Course is Offered",
    "If you selected \"other\", please elaborate. If you heard about this book at a conference, which conference(s)?",
    "Submission ID", "entered into email program", ""
]

# Streamlit GUI
st.set_page_config(page_title="RUP Desk and Exam Copy Request Form", layout="wide")
st.title("Rutgers University Press - Desk and Exam Copy Request Form")
st.markdown("Please provide the following information to request a desk or exam copy. *Required fields")

# Initialize session state
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

with st.form(key="exam_desk_form"):
    # Book Information
    st.subheader("Book Information")
    book_title = st.text_input("Book Title*", placeholder="e.g., My Race Is My Gender", key="book_title")
    book_author = st.text_input("Book Author/Editor*", placeholder="e.g., Stephanie Hsu", key="book_author")
    isbn = st.text_input("Paperback ISBN*", placeholder="e.g., 9781978823945", key="isbn")
    publication_date = st.text_input("Publication Date", placeholder="e.g., 08-16-2024", key="publication_date")

    # Customer Information
    st.subheader("Customer Information")
    first_name = st.text_input("First Name*", key="first_name")
    last_name = st.text_input("Last Name*", key="last_name")
    email = st.text_input("Email*", key="email")
    institution = st.text_input("Institution", key="institution")
    department = st.text_input("Department", key="department")
    street = st.text_input("Street Address*", key="street")
    street2 = st.text_input("Street Address 2", key="street2")
    city = st.text_input("City*", key="city")
    state = st.text_input("State/Province*", key="state")
    zip_code = st.text_input("Zip/Postal Code*", key="zip_code")
    country = st.text_input("Country*", key="country")
    phone = st.text_input("Phone Number*", key="phone")

    # Course Information
    st.subheader("Course Information")
    course_name = st.text_input("Course Name", key="course_name")
    course_number = st.text_input("Course Number", key="course_number")
    expected_enrollment = st.number_input("Expected Enrollment", min_value=0, step=1, key="expected_enrollment")
    semester = st.text_input("Semester/Term", placeholder="e.g., Fall 2025", key="semester")
    course_start_date = st.text_input("Course Start Date", placeholder="e.g., 09-01-2025", key="course_start_date")

    # Request Type and Format
    st.subheader("Request Type and Format")
    copy_type = st.selectbox("Copy Type*", ["Print", "Electronic", "Both"], key="copy_type")
    request_type = st.selectbox("Request Type*", ["Desk Copy", "Exam Copy"], key="request_type")
    st.markdown("*Note*: Desk Copies are typically provided as print only. Selecting 'Electronic' or 'Both' for Desk Copy will provide a print copy unless an electronic version is available.")

    # Additional
    notes = st.text_area("Notes/Comments", placeholder="Any additional information", key="notes")
    rush_order = st.checkbox("Rush my order", key="rush_order")

    submit_button = st.form_submit_button("Submit Request")

    if submit_button:
        required_fields = {
            "Book Title": book_title,
            "Book Author/Editor": book_author,
            "Paperback ISBN": isbn,
            "First Name": first_name,
            "Last Name": last_name,
            "Email": email,
            "Street Address": street,
            "City": city,
            "State/Province": state,
            "Zip/Postal Code": zip_code,
            "Country": country
        }
        additional_fields = {
            "Institution:": institution,
            "Department": department,
            "Course Name": course_name,
            "Course Number": course_number,
            "Expected Enrollment": str(expected_enrollment),
            "Semester/Term": semester,
            "Course Start Date": course_start_date
        }
        # check for empty additional fields and make the empty ones into ""
        for field, value in additional_fields.items():
            if not value.strip():
                value = ""
        # Check for missing required fields
        missing_fields = [field for field, value in required_fields.items() if not value.strip()]
        
        if missing_fields:
            st.error(f"Missing required fields: {', '.join(missing_fields)}")
        else:
            # Prepare form data
            form_data = {
                "Book Title": book_title,
                "Book Author/Editor": book_author,
                "Paperback ISBN": isbn,
                "Publication Date": publication_date,
                "First Name": first_name,
                "Last Name": last_name,
                "Email": email,
                "Institution": institution,
                "Department": department,
                "Street Address": street,
                "Street Address Line 2": street2,
                "City": city,
                "State / Province": state,
                "Postal / Zip Code": zip_code,
                "Country": country,
                "Phone Number": phone,
                "Course Name": course_name,
                "Course Number": course_number,
                "Expected Enrollment": expected_enrollment,
                "Semester/Term": semester,
                "Course Start Date": course_start_date,
                "Request Type": request_type,
                "Copy Type": copy_type,
                "Notes/Comments": notes,
                "Rush Order": rush_order
            }

            # Create DataFrame with excel_columns
            data_dict = {
                "Submission Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Is this a desk copy request or an exam copy request?": form_data["Request Type"],
                "Do you want a print copy or an electronic copy or both?": form_data["Copy Type"],
                "Book Title": form_data["Book Title"],
                "Book Author/Editor": form_data["Book Author/Editor"],
                "Paperback ISBN": form_data["Paperback ISBN"],
                "Publication Date": form_data["Publication Date"],
                "First Name": form_data["First Name"],
                "Last Name": form_data["Last Name"],
                "Title": "",  # Not collected
                "Department": form_data["Department"],
                "University": form_data["Institution"],
                "Course Title": form_data["Course Name"],
                "Email": form_data["Email"],
                "Phone Number": form_data["Phone Number"],
                "Street Address": form_data["Street Address"],
                "Street Address Line 2": form_data["Street Address Line 2"],
                "City": form_data["City"],
                "State / Province": form_data["State / Province"],
                "Postal / Zip Code": form_data["Postal / Zip Code"],
                "Country": form_data["Country"],
                "How likely are you to adopt this book for your classroom?": "",  # Not collected
                "How did you hear about the book?": "",  # Not collected
                "Your Note": f"{form_data['Notes/Comments']}\nExpected Enrollment: {form_data['Expected Enrollment']}\nRush Order: {form_data['Rush Order']}",
                "Course Title and Number": f"{form_data['Course Name']} {form_data['Course Number']}",
                "Date When the Course is Offered": form_data["Course Start Date"],
                "If you selected \"other\", please elaborate. If you heard about this book at a conference, which conference(s)?": "",  # Not collected
                "Notes": "",  # Not collected
                "entered into email program": "",  # Not collected
                "": ""  # Placeholder column
            }
            
            df = pd.DataFrame([data_dict], columns=excel_columns)
            # Append to CSV
            try:
                with file_lock:
                    file_exists = os.path.isfile("exam_desk_requests.csv")
                    df.to_csv("exam_desk_requests.csv", mode="a", index=False, header=not file_exists)
                st.session_state.form_data = form_data
                st.session_state.confirmation_message = "Request submitted successfully!"
                st.session_state.form_submitted = True
            except Exception as e:
                st.session_state.confirmation_message = f"Error saving to CSV: {str(e)}"
                st.session_state.form_submitted = True
# Display submitted data message
if st.session_state.form_submitted and st.session_state.form_data:
    st.success("Request submitted successfully!")

# Note about required fields
st.markdown("*Required fields")

data = pd.read_csv("exam_desk_requests.csv").iloc[-1].to_list()  # Ensure the file exists and is readable
# finish it off
for row in range(len(data)):
    data[row][14] = "" # clear "sumbission_id" to make room for "notes"
    order = True
    info = gather_info( data[row] )
    if( ("Print" in info["format"]) and ("Desk" in info["format"]) ):
        order = print_desk(info)
        if(order == False):
            print(f"ORDER FAILED for {info["title"]} for {info["first name"]}.")
    if(order != False):
        message = make_email_content(info)
    # mark as completed
    if(info["status"] != ""):
        data[row][16] = info["status"]
        data[row][14] = info["notes"]
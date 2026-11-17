# use venv conda virtual environment
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.styles import Border, Side
from openpyxl.styles import Font
from helpers import is_row_highlighted, is_row_bordered, publisher, discount_code, generate_link, print_desk
from rich.console import Console
from rich.text import Text

### connect to data
file_path = "Requests.xlsx"

def read_excel(file_path):
    # Load the workbook and select the active sheet
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    # Process each subsequent row 
    info = []
    updata = []
    status = []
    # (status)
    for row in sheet.iter_rows(min_row=2, values_only=False):
        if(is_row_highlighted(row)):
            status.append("x")
        elif(is_row_bordered(row)):
            status.append("x/2")
        else:
            status.append("")

    rows = list(sheet.iter_rows(min_row = 2, values_only=True))
    for row in rows: 
        row_list = list(row)
        updata.append(row_list)
        
        # Process specific columns:
        draft = row_list[1:4] # 1-3 (Desk/Exam, Print/Elec/Both, Book Title)
        draft.append(row_list[5]) # 5 (ISBN)
        draft.extend(row_list[7:9]) # 7-8 (First name, Last name)
        draft.extend(row_list[13:21]) # 13-20 (email, phone_no, street_address_1, street_address_2, city, state, zipcode, country)
        draft.append(row_list[27]) # 27 (notes)
        draft.append("") # 28 (conferences)    
        
        info.append(draft) 

    for row in range(len(info)):
        info[row].append(status[row])

    return info, updata

data, updata = read_excel(file_path)
# print(data[0][:])

### make decision
def decide_format(row):
    format = ""
    exam_desk = str(row[0])
    prin_elec_both = str(row[1])
    # decide which format between Print (0), Electronic (1), or both (2)
    if(prin_elec_both.startswith("Print")):
        format = format + str(0)
    elif(prin_elec_both.startswith("Electronic")):
        format = format + str(1)
    elif(prin_elec_both.startswith("Both")):
        format = format + str(2)
    # decide which format between Desk (0) or Exam (1)
    if(exam_desk.startswith("Desk")):
        format = format + str(0)
    elif(exam_desk.startswith("Exam")):
        format = format + str(1)
    return format
# print(decide_format( data[1][:] ))

### action execution
def gather_info(row):
    info = {}
    info["email"] = row[6]
    info["first name"] = row[4]
    info["title"] = row[2]
    isbn, title = row[3], row[2]
    info["publisher"] = publisher(isbn)
    format = decide_format(row)
    if(format == "00"): # print desk
        info["phone_no"] = row[7]
        info["format"] = "Print Desk"
        info["last name"] = row[5]
        info["street address"] = row[8]
        info["street address 2"] = row[9]
        if(info["street address 2"] == None):
            info["street address 2"] = ""
        info["city"] = row[10]
        info["state"] = row[11]
        info["zipcode"] = row[12]
        info["country"] = row[13]
        if(info["country"] == None):
            info["country"] = ""
    elif(format == "01"): # print exam
        info["format"] = "Print Exam"
        info["discount"] = discount_code(info["publisher"])
    elif(format == "10"): # electronic desk
        info["format"] = "Electronic Desk"
        info["link"] = generate_link(isbn, title)
    elif(format == "11"): # electronic exam
        info["format"] = "Electronic Exam"
        info["link"] = generate_link(isbn, title)
    elif(format == "20"): # both desk
        info["phone_no"] = row[7]
        info["format"] = "Print and Electronic Desk"
        info["last name"] = row[5]
        info["street address"] = row[8]
        info["street address 2"] = row[9]
        if(info["street address 2"] == None):
            info["street address 2"] = ""
        info["city"] = row[10]
        info["state"] = row[11]
        info["zipcode"] = row[12]
        info["country"] = row[13]
        if(info["country"] == None):
            info["country"] = ""
        info["link"] = generate_link(isbn, title)
    elif(format == "21"): # both exam
        info["format"] = "Print and Electronic Exam"
        info["discount"] = discount_code(info["publisher"])
        info["link"] = generate_link(isbn, title)
    info["isbn"] = isbn
    if("link" in info.keys()):
            if(info["link"] is None):
                info["notes"] = "Cannot Make Comp Copy Link"
            else:
                info["notes"] = ""
    else:
        info["notes"] = ""
    info["status"] = ""
    return info
# print( gather_info( data[0][:] ) )

def make_email_content(info):
    email = {}
    email["to"] = info["email"]
    email["cc"] = "desk-exam@rutgersuniversitypress.org"
    email["subject line"] = f"{info["title"]} {info["format"]} Copy Request"
    email["content"] = ""
    if info["format"] == "Print Desk":
        email["content"] = f"Hi {info["first name"]},\n\nThank you so much for your desk copy request. Your order has been placed and should arrive within the next week or two.\n"
        info["status"] = "x"
    elif info["format"] == "Print Exam":
        email["content"] = f"Dear {info["first name"]},\n\nThank you for your exam copy request for this title.  Below is a discount code that you can use in our shopping cart to buy the exam copy at $15.00 (free shipping).\n\n{info["discount"]}\n"
        info["status"] = "x"
    elif info["format"] == "Electronic Desk":
        if(info["link"] != None):
            email["content"] = f"Hi {info["first name"]},\n\nBelow is a link to an electronic desk copy for your use.\n\n{info["link"]}\n"
            info["status"] = "x"
        else:
            email["content"] = f"Hi {info["first name"]},\n\nThank for your request. However, at the moment we do not have an electronic copy available."
            info["status"] = "x/2"
            info["notes"] = "cannot Make Comp Copy Link"
    elif info["format"] == "Electronic Exam":
        if(info["link"] != None):
            email["content"] = f"Hi {info["first name"]},\n\nBelow is a link to an electronic exam copy for your use.\n\n{info["link"]}\n"
            info["status"] = "x"
        else:
            email["content"] = f"Hi {info["first name"]},\n\nThank for your request. However, at the moment we do not have an electronic copy available."
            info["status"] = "x/2"
            info["notes"] = "cannot Make Comp Copy Link"
    elif info["format"] == "Print and Electronic Desk":
        if(info["link"] != None):
            email["content"] = f"Hi {info["first name"]},\n\nThank you so much for your desk copy request. Your order has been placed and should arrive within the next week or two. Below is a link to an electronic desk copy for your use.\n\n{info["link"]}\n"
            info["status"] = "x"
        else:
            email["content"] = f"Hi {info["first name"]},\n\nThank you so much for your desk copy request. Your order has been placed and should arrive within the next week or two. However, we do not have an electronic copy available at the moment."
            info["status"] = "x/2"
            info["notes"] = "cannot Make Comp Copy Link\nsent Print Desk Copy order"
    elif info["format"] == "Print and Electronic Exam":
        if(info["link"] != None):
            email["content"] = f"Dear {info["first name"]},\n\nThank you for your exam copy request for this title.  Below is a discount code that you can use in our shopping cart to buy the exam copy at $15.00 (free shipping) and a link to an electronic exam copy for your use.\n\n{info["discount"]}\n\n{info["link"]}\n"
            info["status"] = "x"
        else:
            email["content"] = f"Dear {info["first name"]},\n\nThank you for your exam copy request for this title.  Below is a discount code that you can use in our shopping cart to buy the exam copy at $15.00 (free shipping). However, we do not have an electronic copy available at the moment.\n\n{info["discount"]}"
            info["status"] = "x/2"
            info["notes"] = "cannot Make Comp Copy Link\nsent discount code"
    return email
# print( make_email_content( gather_info( data[0][:] ) ) )

# Write updata into excel
def write_excel(file_path, new_data, row_no):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    sheet.delete_rows(2)
    sheet.append(new_data[row_no])
    if(data[row_no][16] == "x"): # highlight if completely done
        highlight_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        for cell in sheet[sheet.max_row]:
            cell.fill = highlight_fill
    elif(data[row_no][16] == "x/2"): # border if half done
        side = Side(style="thin")
        row_cells = list(sheet[sheet.max_row])
        row_cells[0].border = Border(left=side, top=side, bottom=side)
        for cell in row_cells[1:-1]:
            cell.border = Border(top=side, bottom=side)
        if len(row_cells) > 1:
            row_cells[-1].border = Border(right=side, top=side, bottom=side)
    for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row, min_col=1, max_col=sheet.max_column):
        for cell in row:
            cell.font = Font(name="Arial", size=10)
    workbook.save(file_path)

# finish it off
for row in range(len(data)):
    data[row][14] = "" # clear "sumbission_id" to make room for "notes"
    if(data[row][16] == ""):
        order = True
        info = gather_info( data[row] )
        if( ("Print" in info["format"]) and ("Desk" in info["format"]) ):
            order = print_desk(info)
            if(order == False):
                print(f"ORDER FAILED for {info["title"]} for {info["first name"]}. Try again")
        if(order != False):
            content = make_email_content(info)
            print(data[row], "\n")
            print(content["to"], "\n")
            print(content["subject line"], "\n")
            # print out email content
            console = Console()
            italic_text = Text(content["content"], style="italic") # Create a text object with italic style
            console.print(italic_text) # Print the text
            print()
        print()
        # mark as completed
        if(info["status"] != ""):
            data[row][16] = info["status"]
            data[row][14] = info["notes"]
        # def send_email( content ):
        # mark it as completed in updata
        updata[row][27] = data[row][14] # update notes
        updata[row][5] = str(data[row][3]) # make ISBNs strings instead of integers
        # handle empty cells
        for cell in updata[row]:
            if cell is None:
                cell = " "
        write_excel(file_path, updata, row)
    else:
        print("Completed already\n")
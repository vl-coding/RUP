import requests
from datetime import datetime
from links import generate_link
from desks import print_desk
# from outlook import (function)

def publisher(isbn):
    response = requests.get(f"https://www.rutgersuniversitypress.org/search-results-grid/?keyword={isbn}")
    index = response.text.find("Publisher: ") + 11
    response = response.text[index:(index+28)]
    if("Rutgers" in response):
        return "Rutgers University Press"
    elif("Bucknell" in response):
        return "Bucknell University Press"
    elif("Delaware" in response):
        return "University of Delaware Press"
    elif("Templeton" in response):
        return "Templeton University Press"
    else:
        ""

def find_quart(month):
    quart = month/3
    if(month % 3 != 0):
        quart += 1
    return int(quart)

def discount_code(publisher):
    discount_code = "CODE"  # real prefix removed for public showcase
    if(publisher == "Rutgers University Press"):
        discount_code = f"{discount_code}AAA"
    elif(publisher == "Bucknell University Press"):
        discount_code = f"{discount_code}BBB"
    elif(publisher == "Universtiy of Delaware Press"):
        discount_code = f"{discount_code}CCC"
    elif(publisher == "Templeton University Press"):
        discount_code = f"{discount_code}DDD"
    discount_code = f"{discount_code}{find_quart(datetime.now().month) + 1}Q{datetime.now().year % 100}"
    return discount_code

def is_cell_highlighted(cell):
    # cell.fill.fill_type is None if no fill is applied
    return cell.fill and cell.fill.fill_type is not None

def is_row_highlighted(row):
    return any(is_cell_highlighted(cell) for cell in row)

def is_row_bordered(row):
    # Check that every cell has top and bottom borders
    for cell in row:
        if not cell.border.top or cell.border.top.style is None:
            return False
        if not cell.border.bottom or cell.border.bottom.style is None:
            return False

    # Check left border on the first cell
    first_cell = row[0]
    if not first_cell.border.left or first_cell.border.left.style is None:
        return False

    # Check right border on the last cell
    last_cell = row[-1]
    if not last_cell.border.right or last_cell.border.right.style is None:
        return False

    return True
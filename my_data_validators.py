import calendar
import random
import time

import requests, datetime
from datetime import datetime
import os
import string
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from better_profanity import profanity
from wtforms import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import re

# Loading My Keys

load_dotenv()
ADMIN = generate_password_hash(os.environ.get('ADMIN'), method='pbkdf2:sha256', salt_length=8)
WAREHOUSE_USER_API_KEY = os.environ.get('WAREHOUSE_USER')
profanity.load_censor_words()
ALLOWED_EXTENSIONS = {'csv', 'ods', 'xlsx'}


def check_date(birth_date):
    """If false it has a validation message with it"""

    if birth_date != None:
        birth_date = birth_date.strip()
        if birth_date == '':
            return (False, "Please Enter Your Birth Date")
        try:
            time.strptime(birth_date, '%m/%d/%Y')
            birth_date_year = int((str(birth_date)).split("/")[2])
            print(birth_date_year)
            current_year = datetime.now().year
            print(current_year)
            if current_year - birth_date_year < 10:
                return (False, "Sorry , You have to be at least 10 Years old or above ")
        except:
            return (False, "Please Enter Your Birth Date in the Correct Format")
        return (True, "")


def get_date() -> str:
    """it prints the date in nice format ex: september 12,2001"""
    month = calendar.month_name[datetime.now().month]
    day = datetime.now().day
    year = datetime.now().year
    date = f"{month} {day},{year}"
    return date


def check_url(url: str):
    """Returns True if the url returns a valid response code ,
       otherwise return False.
    """
    try:
        response = requests.get(url)
        return True
    except requests.ConnectionError as exception:
        return False


def is_url(url: str):
    if url != None and check_url(url):
        return url
    raise ValidationError('Invalid Product link')


def check_available(para: str) -> bool:
    para=str(para)

    if para == None:
        raise ValidationError('available and delivery  : must be either true or false')
    if para == "1" or para == 1 or para.lower() == "true":
        return True
    elif para == "0" or para == 0 or para.lower() == "false":
        return False
    raise ValidationError('availabe and delivery : must be true or false')


def missing_param(param, param_name: str):
    """It checks if the Parameter is missing"""
    if param == None:
        raise ValidationError(f"💡Missing {param_name} Parameter !")
    return param


def check_price(price: float):
    """It checks Price Value"""
    try:
        if price == None or float(price) <= 0:
            raise ValidationError("💡Price can't be Less than or Equal Zero")
        return round(float(price), 2)
    except ValueError:  # If it cant be typed cast to float
        raise ValidationError("💡Please write the price in float format ex: 12.1")


def allowed_file(filename):
    """Check if the file that is uploaded ends with the correct extension when using upload_file"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_url_image(image_url: str):
    """checks if the url is image format """
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    if image_url == None or len(image_url) == 0:
        raise ValidationError('💡Product Image link is needed')

    r = requests.head(image_url)
    if r.headers["content-type"] in image_formats and check_url(image_url):
        return image_url
    raise ValidationError('💡Invalid Image link')


def is_abusive(text: str):
    """Check if the content is abusive used  """
    if text == None:
        raise ValidationError("💡Product Description is needed")
    censored_text = profanity.censor(text)
    if "****" in censored_text:
        raise ValidationError("💡Abusive content")
    return text


def is_company(company_name: str) -> bool:
    """It checks is the name is a Company name in a correct format and ending"""
    company_name = company_name.title()
    regex = r"\b[A-Z]\w+(?:\.com?)?(?:[ -]+(?:&[ -]+)?[A-Z]\w+(?:\.com?)?){0,2}[,\s]+(?i:ltd|llc|inc|plc|co(?:rp)?|group|holding|gmbh)\b"
    if len(re.findall(regex, company_name)) == 1:
        return True
    return False


def is_admin(admin: str) -> bool:
    """So the user wont be able to update or delete  default Products returns boolean only"""
    if admin == None:
        return False
    return check_password_hash(ADMIN, admin)


def check_email(email_address: str) -> bool:
    """Email Validator that checks if it was real email or No"""
    if email_address == None:
        raise ValidationError("Enter Your Email")
    response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params={'email': str(email_address).lower()})
    status = response.json()['status']
    if status != "valid":
        raise ValidationError("Email doesn't Exist , please Enter Your real Email")


def password_generator():
    "Generates a random Password"
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

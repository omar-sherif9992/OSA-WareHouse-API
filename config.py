import json
import requests
import pathlib
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import os
from sqlalchemy import exc
from models import User, Products
from database import db
from dotenv import load_dotenv
from my_data_validators import *
from flask_bootstrap import Bootstrap
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

# Loading My Keys
load_dotenv()
APP_SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASE_URL= os.environ.get("DATABASE_URL","sqlite:///Warehouse.db")

WAREHOUSE_USER_API_KEY = os.environ.get('WAREHOUSE_USER')
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
MY_SUPPORT_EMAIL = os.environ.get("MY_SUPPORT_EMAIL")
MY_PHONE = os.environ.get("MY_PHONE")
MY_COUNTRY = os.environ.get("MY_COUNTRY")
MY_BIRTH_DATE = os.environ.get("MY_BIRTH_DATE")

# Warehouse Demo
MY_DEMO_BIRTH_DATE=os.environ.get("MY_DEMO_BIRTH_DATE")
MY_DEMO_PHONE=os.environ.get("MY_DEMO_PHONE")
MY_DEMO_EMAIL=os.environ.get("MY_DEMO_EMAIL")
MY_DEMO_COUNTRY=os.environ.get("MY_DEMO_COUNTRY")
MY_DEMO_API_KEY=os.environ.get("MY_DEMO_API_KEY")

WAREHOUSE_BASE_URL = os.environ.get("WAREHOUSE_BASE_URL") # Todo after you upload the website make sure to update it
MAIL_ME_ERROR_LINK = os.environ.get('MAIL_ME_ERROR_LINK') #For the user to email me mailto link


COMPANY_END=os.environ.get('COMPANY_END')    # Only for Contributors


client_secret_file=json.loads(os.environ.get("CLIENT_SECRET_JSON_FILE"))




client_secrets_file_path = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")


def create_client_secret_file():
        jsonString = json.dumps(client_secret_file)
        jsonFile = open(client_secrets_file_path, "w")
        jsonFile.write(jsonString)
        jsonFile.close()

# Excel or csv File uploads for inventory upload
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv','ods',"xlsx"}

# Google sign up button setup
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = os.environ.get('CLIENT_ID')

create_client_secret_file()
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file_path,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri=f"{WAREHOUSE_BASE_URL}/callback"
)


def init_db(app):
    """Database tables configuration setup"""
    # Creates the logs tables if the db doesnt already exist
    with app.app_context():

        db.create_all()
        new_user = User(
            email=MY_SUPPORT_EMAIL.lower()
            ,
            name="Omar Sherif",
            api_key=ADMIN,
            number_of_products=0,
            gender="Male",
            status="User",
            service=None,
            birth_date=MY_BIRTH_DATE,
            phone=str(MY_PHONE),
            country=MY_COUNTRY.title(),
            since_date=get_date()
        )

        demo = User(  # TODO

            email=MY_DEMO_EMAIL,
            name="Omar Sherif Demo",
            number_of_products=0,
            api_key=generate_password_hash(MY_DEMO_API_KEY, method='pbkdf2:sha256', salt_length=8),
            gender="Male",
            status="User",
            service=None,
            birth_date=MY_DEMO_BIRTH_DATE,
            phone=MY_DEMO_PHONE,
            country=MY_DEMO_COUNTRY,
            since_date = get_date()

        )
        db.session.add(new_user)
        db.session.add(demo)

        try:
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
        except:
            pass


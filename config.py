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
WAREHOUSE_USER_API_KEY = os.environ.get('WAREHOUSE_USER')
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
MY_SUPPORT_EMAIL = os.environ.get("MY_SUPPORT_EMAIL")
MY_PHONE = os.environ.get("MY_PHONE")
MY_COUNTRY = os.environ.get("MY_COUNTRY")
MY_BIRTH_DATE = os.environ.get("MY_BIRTH_DATE")
WAREHOUSE_BASE_URL = os.environ.get("WAREHOUSE_BASE_URL") # Todo after you upload the website make sure to update it
MAIL_ME_ERROR_LINK = os.environ.get('MAIL_ME_ERROR_LINK') #For the user to email me mailto link
COMPANY_END=os.environ.get('COMPANY_END')    # Only for Contributors



# Excel or csv File uploads for inventory upload
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv','ods',"xlsx"}

# Google sign up button setup
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = os.environ.get('CLIENT_ID')
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
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
            email="demo@gmail.com",
            name="Omar Sherif",
            number_of_products=0,
            api_key=generate_password_hash("+021008757777_demo", method='pbkdf2:sha256', salt_length=8),
            gender="Male",
            status="User",
            service=None,
            birth_date=MY_BIRTH_DATE,
            phone=str("+021008757777"),
            country=MY_COUNTRY.title(),
            since_date = get_date()

        )
        db.session.add(new_user)
        db.session.add(demo)

        try:
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()


# APP Configuration
def create_app():
    """App confiquration setup """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = APP_SECRET_KEY
    app.config["RECAPTCHA_PUBLIC_KEY"] = RECAPTCHA_PUBLIC_KEY
    app.config["RECAPTCHA_PRIVATE_KEY"] = RECAPTCHA_PRIVATE_KEY
    Bootstrap(app)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    ##Connect to Database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Warehouse.db'
    # app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    db.app = app
    db.init_app(app)
    init_db(app)
    ADMIN_USER = User.query.filter_by(id=1).first()
    return (ADMIN_USER, app)

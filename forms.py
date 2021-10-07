import datetime

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, SelectField, RadioField, DateField
from wtforms.validators import DataRequired, Length, Email, ValidationError, URL
from my_data_validators import *
from select_fields_data import *
from models import User
from dotenv import load_dotenv
load_dotenv()

COMPANY_END=os.environ.get('COMPANY_END')


class GoogleForm(FlaskForm):
    """It's the form if the user selected google sign up"""
    phone = StringField(label="", validators=[DataRequired()],
                        render_kw={"placeholder": "Phone Number ex: +209996752223"})
    country = SelectField(label="", validators=[DataRequired()], choices=countries())
    status = RadioField(label="", choices=[("User", "User"), ("Company", "Company")], render_kw={"Status"},
                        validators=[DataRequired()])
    gender = SelectField(label="", choices=genders())
    service = SelectField(label="", choices=all_services_list)
    company_url = StringField(label="",
                              render_kw={"placeholder": "Company Page Link"})
    birth_date = StringField(label="", render_kw={"placeholder": "Birth Date mm/dd/yyyy"})
    submit = SubmitField(label="Register")

    def validate_birth_date(self, birth_date):
        """it validates the user's birth date"""
        flag, message = check_date(birth_date=birth_date.data)
        if self.status.data == "User" and not flag:
            raise ValidationError(message)

    def validate_gender(self, gender):
        """it validates the user's gender"""
        if self.status.data == "User" and gender.data == "Choose Your Gender":
            raise ValidationError("Please Choose Your Gender")

    def validate_service(self, service):
        """it validates the company's service"""
        if self.status.data == "Company" and service.data == "Choose Your Company's Service":
            raise ValidationError("Please Choose Your Company's Service")

    def validate_company_url(self, company_url):
        """It checks if the company url is valid and the company's first name is in the url"""
        if self.status.data == "Company":
            try:
                is_url(url=company_url.data)
            except:
                raise ValidationError("Invalid Company Url")
            first_name = self.name.data
            first_name = first_name.split(" ")[0]
            if str(first_name).lower() not in str(company_url.data).lower():
                raise ValidationError("This Company Url is not related to Your Company")




    def validate_status(self, status):
        """it validates that the user selected  status"""
        if status.data != "User" and status.data != "Company":
            raise ValidationError("Please Select Your Status")

    def validate_country(self, country):
        """Make sure that the user have chosen a country"""
        try:
            country = country.data
            if country == None or str(country) == "Country" or country == 'None' or country == "":
                raise ValueError
        except ValueError:
            raise ValidationError('Choose Your Country')

    def validate_phone(self, phone):
        """International Phone number Validator"""
        user = User.query.filter_by(phone=phone.data).first()
        if user != None:
            raise ValidationError("Phone Number is used before")

        try:
            if len(str(phone.data)) >= 5 and self.status.data == "Company":
                return
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                # Because Company's phone consist of 5 numbers like jumia
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid Phone Number')


class ForgotForm(FlaskForm):
    """It's the form if the user selected google sign up"""
    email = StringField(label="", validators=[Email("This field requires a valid Email Address"), DataRequired(),
                                              Length(min=6, max=35)], render_kw={"placeholder": "Email"})
    phone = StringField(label="", validators=[DataRequired()],
                        render_kw={"placeholder": "Phone Number ex: +209996752223"})
    submit = SubmitField(label="Find api_key")

    # recaptcha = RecaptchaField()  # todo enable recaptcha after uploading to disable bots
    def validate_email(self, email):
        """Email Validator for forgot form"""
        check_email(email.data)
    # no phone validator here cause status radio is not available


class RegisterForm(FlaskForm):
    """User Register his or her Data"""
    name = StringField(label="", validators=[DataRequired()], render_kw={"placeholder": "Name"})
    email = StringField(label="", validators=[Email("This field requires a valid Email Address"), DataRequired(),
                                              Length(min=6, max=35)], render_kw={"placeholder": "Email"})
    phone = StringField(label="", validators=[DataRequired()],
                        render_kw={"placeholder": "Phone Number ex: +209996752223"})
    country = SelectField(label="", validators=[DataRequired()], choices=countries())
    status = RadioField(label="", choices=[("User", "User"), ("Company", "Company")], render_kw={"Status"},
                        validators=[DataRequired()])
    gender = SelectField(label="", choices=genders())
    service = SelectField(label="", choices=all_services_list)
    company_url = StringField(label="", render_kw={"placeholder": "Company Page Link"})
    birth_date = StringField(label="", render_kw={"placeholder": "Birth Date mm/dd/yyyy"})

    # recaptcha = RecaptchaField()  # todo enable recaptcha after uploading to disable bots
    submit = SubmitField(label="Register")

    def validate_birth_date(self, birth_date):
        """it validates the user's birth date"""
        flag, message = check_date(birth_date=birth_date.data)
        if self.status.data == "User" and not flag:
            raise ValidationError(message)

    def validate_gender(self, gender):
        """it validates the user's gender"""
        if self.status.data == "User" and gender.data == "Choose Your Gender":
            raise ValidationError("Please Choose Your Gender")

    def validate_service(self, service):
        """it validates the company's service"""
        if self.status.data == "Company" and service.data == "Choose Your Company's Service":
            raise ValidationError("Please Choose Your Company's Service")

    def validate_company_url(self, company_url):
        """It checks if the company url is valid and the company's first name is in the url"""
        if self.status.data == "Company":
            try:
                is_url(url=company_url.data)
            except:
                raise ValidationError("Invalid Company Url")
            first_name = self.name.data
            first_name = first_name.split(" ")[0]
            if str(first_name).lower() not in str(company_url.data).lower():
                raise ValidationError("This Company Url is not related to Your Company")

    def validate_status(self, status):
        """it validates that the user selected  status"""
        if status.data != "User" and status.data != "Company":
            raise ValidationError("Please Select Your Status")

    def validate_email(self, email):
        """Email Validator"""
        user = User.query.filter_by(email=email.data).first()
        if user != None:
            raise ValidationError("Email Address is used before")

        check_email(email.data)

    def validate_name(self, name):
        """Name Validator"""
        word = str(name.data).strip()
        if self.status.data == "User":
            for letter in word:
                if letter.isdigit():
                    raise ValidationError('Please write your Real Name without Digits!')
                elif not letter.isascii():
                    raise ValidationError('Please write your Real Name only letters!')
        if self.status.data == "Company":
            if not is_company(company_name=str(name.data)):
                raise ValidationError('Please Enter Your company name in the correct format and ending')
            if COMPANY_END not in name.data.lower():
                raise ValidationError("ask permission from osa.helpme@gmail.com")

    def validate_country(self, country):
        """Make sure that the user have chosen a country"""
        try:
            country = country.data
            if country == None or country == 'None' or str(country) == "Country":
                raise ValueError
        except ValueError:
            raise ValidationError('Please Choose Your Country')

    def validate_phone(self, phone):
        """International Phone number Validator"""
        user = User.query.filter_by(phone=phone.data).first()
        if user != None:
            raise ValidationError("Phone Number is used before")

        try:
            if len(str(phone.data)) >= 5 and self.status.data == "Company":
                return
            p = phonenumbers.parse(phone.data)
            if (not phonenumbers.is_valid_number(p)) and self.status.data == "User":
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid Phone Number')

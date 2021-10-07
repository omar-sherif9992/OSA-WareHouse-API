from sqlalchemy import exc
from flask_login import UserMixin
from database import db
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import ValidationError


# owner TABLE Configuration
class User(db.Model):
    """users Table """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    phone = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    api_key = db.Column(db.String(100), nullable=False)  # hashed
    gender = db.Column(db.String(7), nullable=True)  # because either a gender or service depending on status
    status = db.Column(db.String(7), nullable=False)  # either Company or User
    service = db.Column(db.String(100), nullable=True)  # because either a gender or service depending on status
    country = db.Column(db.String(100), nullable=False)  # hashed
    birth_date = db.Column(db.String(100), nullable=True)  # birth date
    company_url = db.Column(db.String(100), nullable=True)  # company url
    number_of_products = db.Column(db.Integer, nullable=False)  # number of products the user owns
    since_date = db.Column(db.String(100), nullable=False)  # The date when the User signed up since
    products = db.relationship("Products", backref="user")

    def to_dict_save(self):
        """Converts SQl object into dictionary """
        user_info = {}  # for product info
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            if column.name != "id" and column.name != "user_id" and getattr(self, column.name) != None:
                user_info[column.name] = getattr(self, column.name)

        return user_info

    def to_dict(self):
        """Converts SQl object into dictionary """
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            if column.name != "api_key" and getattr(self, column.name) != None and column.name != "id":
                dictionary[column.name] = getattr(self, column.name)
        return dictionary

    def __repr__(self):
        return '<User %r>' % self.name


# Warehouse TABLE Configuration
class Products(db.Model):
    """products Table"""
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(250), nullable=False)  # product's name
    category = db.Column(db.String(250), nullable=False)  # category of the product
    sub_category = db.Column(db.String(250), nullable=True)  # Some companies doesn't have sub-categories option
    brand = db.Column(db.String(250), nullable=False)  # Product brand
    price = db.Column(db.Float, nullable=False)  # price of the product
    img_url = db.Column(db.String(500), nullable=False)  # image url of the product
    product_description = db.Column(db.String(250), nullable=False)  # product description
    product_url = db.Column(db.String(250), unique=True, nullable=False)  # product page url
    available = db.Column(db.Boolean, nullable=False)  # if the product is available
    delivery = db.Column(db.Boolean, nullable=False)  # if delivery option is available
    currency = db.Column(db.String(10), nullable=False)  # price currency
    source_name = db.Column(db.String(250), nullable=False)  # ex: amazon ,alibaba
    rating = db.Column(db.String(250), nullable=False)
    release_date = db.Column(db.String(250), nullable=False)  # it is the added date for the product
    secure = db.Column(db.Boolean, nullable=False)  # secure the product means hash the product_id and not show it in the inventory for extra layer of security
    product_id = db.Column(db.String(250), unique=True,
                           nullable=False)  # hashed unique for every product for the owner can share to user who doesnt own it.

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # class Saved_Product(db.Model):
    #     """User Saved Products"""
    #     __tablename__ ='saved_products'
    #     user_id = db.Column(db.Integer, db.ForeignKey("users.id"),nullable=False)
    #

    def __repr__(self):
        return '<Product %r>' % self.product_name

    def to_dict_save(self):
        """Converts SQl object into dictionary without owner info for preparing it in csv format for download only "only for my products" ex:
        dictionary=
        {
        "Product_Counter":{"product_info"}
        }
        """
        product = {}  # for product info
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            if column.name != "id" and column.name != "user_id" and getattr(self, column.name) != None:
                product[column.name] = getattr(self, column.name)

        return product

    def to_dict(self, counter: int) -> {}:
        """Converts SQl object into dictionary without owner info "only for my products cause it contains product_id" ex:
        dictionary=
        {
        "Product_Counter":{"product_info"}
        }
        """
        dictionary = {}
        product = {}  # for product info
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            if column.name != "id" and column.name != "user_id" and getattr(self,column.name) != None and column.name != "secure" and column.name != "product_id":
                product[column.name] = getattr(self, column.name)
            if column.name == "id":
                product_counter = f"product_{counter}"
                dictionary[product_counter] = {}

            if column.name == "secure":
                product[column.name] = getattr(self, column.name)
                if getattr(self, column.name) == True or getattr(self, column.name) =="true":
                    pass

                else:
                    product["product_id"] = getattr(self, "product_id")

        dictionary[product_counter] = product
        return dictionary

    # todo
    def to_dict_with_owner(self, user, counter: int) -> {}:
        """Converts SQl object into dictionary with owner info "only for search,filter,all" ex:
         dictionary={
         "product_1":{
            "owner":{
                owner's data
            },
            "product":{
                product's data
            }
        }
        }"""
        dictionary = {}
        product = {}  # for product info
        owner = {'name': user.name,
                 'email': user.email,
                 'phone': user.phone,
                 "country":user.country,
                 "status": user.status,

                 "number_of_products": user.number_of_products,
                 "since": user.since_date,

                 }
        if user.status == "User":
            owner["gender"] = user.gender
        else:
            owner["service"] = user.service
            owner["company_url"] = user.company_url

        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            if column.name != "product_id" and column.name != "id" and column.name != "user_id" and getattr(self, column.name) != None and column.name!="secure":  # avoid sub-category if it was None not necessary
                product[column.name] = getattr(self, column.name)

            if column.name == "id":
                product_counter = f"product_{counter}"
                dictionary[product_counter] = {}
        dictionary[product_counter]["owner"] = owner
        dictionary[product_counter]["product"] = product

        return dictionary

import csv
import os

import pandas as pd
import requests
from Scraped_Data.jumia_data.jumia import Jumia
from user import User
from company import Company
from sign_up_auto import sign_up_user, sign_up_company
import sys
from dotenv import load_dotenv
load_dotenv()

# Only for Contributors
COMPANY_END=os.environ.get('COMPANY_END')

class Uploader:
    """It uploads all the Products data that is scraped"""
    BASE_URL = "http://127.0.0.1:5000/"
    ADMIN = os.environ.get('ADMIN')
    user = None
    company = None
    products_params = None
    api_key = None

    def __init__(self, user, user_products):
        self.all_products = user_products
        if user.service == None:
            self.user = User(user)
        else:
            self.company = Company(user)
        self.products = {}

        # Registering the user
        self.sign_up()

        # restructring the products and uploading it
        self.create_and_upload_products()

    def check_api_key(self, api_key):
        """It checks if the api_key exist or no"""
        if api_key == None:
            return None
        api_key_param = {
            "api_key": api_key
        }
        response = requests.get(url=f"{self.BASE_URL}my/profile", params=api_key_param)
        content = response.json()
        if content.get('status') != "success":
            self.delete_row_csv(api_key=api_key)
            return None
        return api_key

    def delete_row_csv(self, api_key):
        """deletes an old not functional api_key"""
        if self.check_path(name="api_key_saver.csv"):
            df = pd.read_csv(f'{os.getcwd()}/api_key_saver.csv')
            df.drop(df.loc[df['api_key'] == api_key].index, inplace=True)
            df.to_csv(f'{os.getcwd()}/api_key_saver.csv', index=False)

    def sign_up(self):
        """Registers the user or the company"""
        if self.user != None:

            # it tries to read the api_key that was saved and checks then if the api_key is valid if not valid it register again and

            self.api_key = self.check_api_key(api_key=self.read_api_key(user_name=self.user.name))
            if self.api_key != None:
                print(f"{self.user.name} was registered before")

            elif self.api_key == None and sign_up_user(user=self.user):
                print(f"{self.user.name} Successfully registered")
                self.api_key = str(input(f"Please enter the api_key of {self.user.name} check your email osa :"))
                while self.check_api_key(api_key=self.api_key) == None:
                    self.api_key = str(input(f"Please re-enter the api_key of {self.user.name} check your email osa :"))
                self.save_api_key(data_rows=[[self.user.name, "User", self.api_key]],
                                  titles=["Name", "Status", "api_key"])
            else:
                print(f"{self.user.name} failed to register ! ")

        else:
            self.api_key = self.check_api_key(self.read_api_key(user_name=self.company.name))  # todo
            if self.api_key != None:
                print(f"{self.company.name} was registered before")

            elif self.api_key == None and sign_up_company(company=self.company):
                self.company.name=(self.company.name).replace(COMPANY_END,"")
                print(f"{self.company.name} Successfully registered")
                self.api_key = str(input(f"Please enter the api_key of {self.company.name} check your email osa :"))
                while self.check_api_key(api_key=self.api_key) == None:
                    self.api_key = str(
                        input(f"Please re-enter the api_key of {self.company.name} check your email osa :"))
                self.save_api_key(data_rows=[[self.company.name, "Company", self.api_key]],
                                  titles=["Name", "Status", "api_key"])

            else:
                print(f"{self.company.name} failed to register")

    def save_api_key(self, data_rows, titles):
        """Save api key if user or company was already registered and entered previously their api-key"""
        if self.check_path(name="api_key_saver.csv"):
            with open(f'{os.getcwd()}/api_key_saver.csv', 'a') as file:
                write = csv.writer(file)
                write.writerow(data_rows)
        else:
            with open(f'{os.getcwd()}/api_key_saver.csv', 'w') as file:
                write = csv.writer(file)
                write.writerow(titles)
                write.writerows(data_rows)

    def read_api_key(self, user_name: str):
        """Reading api_key from the api_key_saver file"""
        if self.check_path(name="api_key_saver.csv"):
            with open(f'{os.getcwd()}/api_key_saver.csv', newline='') as file:
                reader = csv.reader(file)
                i = 0
                for row in reader:
                    if i == 0:  # so i wont read the titles too
                        i += 1
                        continue
                    if row[0] == user_name:
                        return row[2]
        return None

    def check_path(self, name: str):
        """it checks if the path already exists or no"""
        """check if the that csv file was previously created"""
        return os.path.exists(f'{os.getcwd()}/{name}')

    def create_and_upload_products(self):
        """It Structres the data to be uploaded in the correct format ex:
        self.product_params={
        product_1:{
        product info
        },
        product_2:{
                product info

        }
        }
        """
        counter = 0
        for product in self.all_products:
            counter += 1
            product_name = product[0]  # index 0 for
            product_currency = product[1]  # index 1 for
            product_price = product[2]  # index 2 for
            product_brand = product[3]  # index 3 for
            product_description = product[4]  # index 4 for
            product_page_url = product[5]  # index 5 for page link (essential)
            product_image_url = product[6]  # index 6 for image link (essential)
            product_category = product[7]  # index 7 for category name (essential)
            product_sub_category = product[8]  # index 8 for sub_category can be None ,except: Jumia
            product_rating = product[9]  # index 9 for rating can be None , except: Jumia
            product_source_name = product[10]  # index 10 for source name (essential)
            product_available = product[11]  # index 11 for product available (essential)
            product_delivery = product[12]  # index 12 for deleivery status (esseential)
            product_release_date = product[13]  # index 13 for release date (essential)

            # reseting ===> saving ==> uploading ==> repeat
            product_counter = f"product_{counter}"
            self.products_params = {}  # first product is product_1
            self.products_params[product_counter] = {'api_key': self.api_key}
            self.products_params[product_counter]["product_name"] = product_name
            self.products_params[product_counter]["brand"] = product_brand
            self.products_params[product_counter]["category"] = product_category
            self.products_params[product_counter]["sub_category"] = product_sub_category
            self.products_params[product_counter]["price"] = product_price
            self.products_params[product_counter]["img_url"] = product_image_url
            self.products_params[product_counter]["available"] = product_available
            self.products_params[product_counter]["delivery"] = product_delivery
            self.products_params[product_counter]["rating"] = product_rating
            self.products_params[product_counter]["release_date"] = product_release_date

            self.products_params[product_counter]["description"] = product_description
            self.products_params[product_counter]["currency"] = product_currency
            self.products_params[product_counter]["product_url"] = product_page_url
            self.products_params[product_counter]["source_name"] = product_source_name

            response = requests.post(url=f"{self.BASE_URL}add/product", params=self.products_params[product_counter])

            content = (response.json())
            status = content.get('status')
            fail_response = content.get('response').get('fail_message')
            if fail_response != None and (
                    "Invalid Api Key please apply for an API Key" in fail_response or "Api Key is needed for access" in fail_response):
                print(content.get('response').get('fail_message'))
                break

            if status != None and status == 'error':
                print(content.get('response').get('error_message'))
                break

            if status != None and status == 'fail':
                print("Product is not added due to " + fail_response + "❌")
                counter -= 1
                continue

            print(f"✔ Uploaded Product {counter} ")
        if counter - 1 == 0:
            print(f"No Products are Added")
        else:
            print(f"All {counter - 1} Products is created !")

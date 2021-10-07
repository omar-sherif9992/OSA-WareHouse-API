import requests
from bs4 import BeautifulSoup
import os
import csv
from datetime import datetime
from time import sleep
import calendar
from dotenv import load_dotenv

load_dotenv()

# Only for Contributors
COMPANY_END=os.environ.get('COMPANY_END')

# brand name decreases the number of products  because some products doesnt have a brand
class Jumia:
    company_url = "https://www.jumia.com.eg"
    name = "jumia inc"+COMPANY_END
    country="Egypt"
    email='newsletter@info.jumia.com'
    phone='15204'
    status='Company'
    service="Ecommerce Services"


    def __init__(self):
        # Finding Categories phase 1
        try:
            if (not self.check_path(name="categories")):
                self.categories = self.find_categories()
        except:
            self.categories = self.read_page_data(name='categories')
        else:
            self.categories = self.read_page_data(name="categories")
        # Finding Sub categories phase 2
        try:
            if (not self.check_path(name="sub_categories")):
                self.sub_categories = self.see_all_buttons()

        except:
            self.sub_categories = self.read_page_data(name="sub_categories")
        else:
            self.sub_categories = self.read_page_data(name="sub_categories")

        # Finding Product Profiles  plus
        # extracting image_link ,product_page_link,currency,price phase3
        try:
            if not self.check_path(name="product_profile"):
                self.product_profile = self.enter_products_page()
        except:
            self.product_profile = self.read_page_data(name="product_profile")
        else:
            self.product_profile = self.read_page_data(name="product_profile")

        # Finding Jumia products info -last phase 4 all data saved here
        try:
            if not self.check_path(name="Jumia_products_info"):
                self.all_products_info = self.produce_product()
        except:
            self.all_products_info = self.read_page_data(name="Jumia_products_info")
        else:
            self.all_products_info = self.read_page_data(name="Jumia_products_info")

    def produce_product(self):
        """it produces each branded product with its essential data  phase 4"""
        name = "Jumia_products_info"
        products = []
        skipped = 0
        c = 0
        for product in self.product_profile:
            produced_product = []
            try:
                product_page_link = product[2]
                response = requests.get(url=product_page_link)
                soup = BeautifulSoup(response.content, 'lxml')
                product_currency = product[0]
                product_price = product[1]
                product_image_link = product[3]
                category_name = product[4]
                sub_category = product[5]
                name_tag = soup.find(name='h1')
                product_name = name_tag.text
                rating = soup.select_one(
                    "#jm > main > div:nth-child(1) > section > div > div.col10 > div.-phs > div.-df.-i-ctr.-pvxs > div")
                brand_tag = soup.select_one(
                    selector='#jm > main > div:nth-child(1) > section > div > div.col10 > div.-phs > div:nth-child(1) > a:nth-child(1)')
                if brand_tag == None:
                    skipped += 1
                    print("skipped")
                    continue
                descritption_tag = soup.select_one("ul")
                descritption_tag = descritption_tag.find_all(name='li')
                product_description = ""
                for description in descritption_tag:
                    if (description.text).strip() != "":
                        product_description += f"-{(description.text).strip()} \n"
                if product_description=="":
                    product_description+="N/A"

                # Product info produced
                # print("brand : " + brand_tag.text)
                # print((product_name.strip()).title())
                # print(product_description)
                # print(rating.text)
                produced_product.append(product_name)
                produced_product.append(product_currency)
                produced_product.append(product_price)
                produced_product.append(brand_tag.text)
                produced_product.append(product_description)
                produced_product.append(product_page_link)
                produced_product.append(product_image_link)
                produced_product.append(category_name)
                produced_product.append(sub_category)
                produced_product.append(rating.text)
                produced_product.append("Jumia")  # Source
                produced_product.append(True)  # Available
                produced_product.append(True)  # Delievery Available
                produced_product.append(self.get_date())
                print("_________________________")
                if len(produced_product) != 0:
                    products.append(produced_product)
                    c += 1
                    print(c)
            except KeyError as e:
                print(e)
                continue
            except AttributeError as e:
                print(e)

                continue
            except requests.exceptions.ConnectionError as e:
                sleep(6)
                print(e)

        if not self.check_path(name=name):
            self.save_page_data(data_rows=products, name=name,
                                titles=["Product Name", "Product Currency", "Product Price", "Product Brand",
                                        "Product Description", "Product Page Link", "Product Image Link", "Category",
                                        "Sub-Category", "Rating", "Source", "Available", "Delivery", "Release Date"])
        print(skipped)
        return products

    # https://eg.jumia.is/unsafe/fit-in/500x500/filters:fill(white)/product/16/20819/1.jpg?7211

    def enter_products_page(self):
        """It enters each product page link phase 3 note:product name had some issues here soi scraped it in phase 4"""
        name = "product_profile"
        skipped = 0
        products_pages = []
        c = 0
        for sub_category in self.sub_categories:
            try:
                sub_category_link = sub_category[2]
                response = requests.get(url=sub_category_link)
                soup = BeautifulSoup(response.content, 'lxml')
                category_name = sub_category[0]
                sub_category_name = sub_category[1]
                articles = soup.find_all('article', class_='prd')
                for article in articles:
                    product_page = []
                    product_link = article.find('a')
                    product_price = article.find('div', class_='prc')
                    product_image = article.find('img')
                    if product_link != None and product_price != None and product_image != None:
                        product_currency = (product_price.text).split(' ')[0]
                        product_price_only = (product_price.text).split(' ')[1]
                        # Product page necessary data
                        product_page.append(product_currency)
                        product_page.append(product_price_only)
                        product_page.append(self.company_url + product_link.attrs['href'])
                        product_page.append(product_image.attrs['data-src'])
                        product_page.append(category_name)
                        product_page.append(sub_category_name)
                        if len(product_page) != 0:
                            products_pages.append(product_page)
                            print(c)
                            c += 1
                    else:
                        print(
                            f"✔️skipped:{sub_category_link}    {category_name} {sub_category_name} , image :{product_image} ")
            except KeyError as e:
                skipped += 1
                print(f"Skipped Keyerror: {e}")
                continue
            except AttributeError as e:
                skipped += 1
                print(f"Skipped Attribute error:{e}")
                continue
            except requests.exceptions.ConnectionError:
                skipped += 1
                sleep(6)
                print("skipped request error")
                continue
            except IndexError as e:
                print(f"Skipped IndeErorr: {e}")
                sleep(2)
                skipped += 1
                continue

        if not self.check_path(name=name):
            self.save_page_data(data_rows=products_pages, name=name,
                                titles=["Product Currency", "Product Price", "Product Page Link", "Product Image Link",
                                        "Category", "Sub-Category"])
        print(skipped)
        print(c)
        return products_pages

    def see_all_buttons(self):
        """it scraps all the sub-categories page links phase 2"""
        products_page = []
        i = 0
        while i < len(self.categories):

            (category_name, category_link) = self.categories[i]
            try:
                sleep(0.5)  # for request exception
                i += 1
                response = requests.get(url=category_link)
                soup = BeautifulSoup(response.content, 'lxml')
                headers = soup.find_all(name='header', class_="row")
                for header in headers:
                    try:
                        button = (header.find('a'))
                        if button != None and button.text == "See All":
                            link = button.attrs['href']
                            if "https:" in link:
                                sub_category_name = (header.find('h2')).text
                                if sub_category_name != "Bundles" and sub_category_name != "Tops & Tees":
                                    product_page = (category_name, sub_category_name, link)
                                    products_page.append(product_page)
                                    print(product_page)
                    except KeyError:
                        pass
                print("-----------------------")
            except requests.exceptions.ConnectionError:
                print(category_name + " is skipped")
                sleep(9)
                i -= 1
        if (not os.path.exists(f'{os.getcwd()}/saved/sub_categories_page.csv')):
            self.save_page_data(data_rows=products_page, titles=["Category", "Sub-Category", "Products Link"],
                                name="sub_categories")
        return products_page

    def find_categories(self):
        """Searches for categories and their names phase 1"""
        response = requests.get(url=self.company_url)
        soup = BeautifulSoup(response.content, 'lxml')
        navigation_bar = soup.find_all('a', {'class': "itm"})
        categories = []
        for category in navigation_bar:
            try:
                if category.text != "":
                    categories.append((category.text, self.company_url + category.attrs['href']))
            except KeyError:
                continue
        if (not os.path.exists(f'{os.getcwd()}/saved/categories_page.csv')):
            self.save_page_data(data_rows=categories, name="categories", titles=['Category Name', 'Category Link'])
        return categories

    def read_page_data(self, name):
        """Reading Categories.csv incase Amazon scrape bot error"""
        with open(f'{os.getcwd()}/Scraped_Data/jumia_data/saved/{name}_page.csv', newline='') as file:
            reader = csv.reader(file)
            category = []
            i = 0
            for row in reader:
                if i == 0:
                    i += 1
                    continue
                category.append(row)
        return category

    def save_page_data(self, data_rows, name, titles):
        """Save categories_first_page incase amazon bot detected us"""
        with open(f'{os.getcwd()}/saved/{name}_page.csv', 'w') as file:
            write = csv.writer(file)
            write.writerow(titles)
            write.writerows(data_rows)

    def get_date(self) -> str:
        """it prints the date in nice format ex: september 12,2001"""
        month = calendar.month_name[datetime.now().month]
        day = datetime.now().day
        year = datetime.now().year
        date = f"{month} {day},{year}"
        return date

    def check_path(self, name: str):
        """it checks if the path already exists or no"""
        """check if the that csv file was previously created"""
        return os.path.exists(f'{os.getcwd()}/Scraped_Data/jumia_data/saved/{name}_page.csv')

    def __str__(self):
        return self.value




if __name__ == "__main__":
    jumia = Jumia()

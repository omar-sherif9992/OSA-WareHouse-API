import requests
from bs4 import BeautifulSoup
from itertools import zip_longest
from pprint import pprint
from alive_progress import alive_bar
import os
import csv
from itertools import zip_longest
import pandas


class Amazon:
    AMAZON_URL = "https://www.amazon.eg/?&tag=egtxabkgode-21&ref=pd_sl_1y3qitcccr_e&adgrpid=123527996621&hvpone=&hvptwo=&hvadid=542972048817&hvpos=&hvnetw=g&hvrand=4384277889709581080&hvqmt=e&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=21468&hvtargid=kwd-550262326951&hydadcr=335_2546797&gclid=Cj0KCQjwv5uKBhD6ARIsAGv9a-xcZutqBmTaoCgIFsMu_hcUr1iwcgUSjAovjSf3pHxu3QqDtVs79rQaAgQhEALw_wcB&language=en_AE"

    def __init__(self):
        self.page=1
        try:
            self.categories_first_page = self.find_categories()
        except IndexError as message:
            print("find_categories Failed")
            self.categories_first_page =self.read_categories()
        self.see_all_results()

    def read_categories(self):
        """Reading Categories.csv incase Amazon scrape bot error"""
        with open(f'./amazon/saved/categories_{self.page}_page.csv', newline='') as file:
            reader = csv.reader(file)
            category=[]
            i=0
            for row in reader:
                if i==0:
                    i+=1
                    continue
                category.append((row[0],row[1]))
        return category

    def save_categories(self,categories):
        """Save categories_first_page incase amazon bot detected us"""
        with open(f'./amazon/saved/categories_{self.page}_page.csv', 'w') as file:
            write = csv.writer(file)
            write.writerow(['Category Name', 'Category Link'])
            write.writerows(categories)
        self.page+=1

    def find_categories(self):
        """Searches for categories and their names"""
        response = requests.get(url=self.AMAZON_URL)
        soup = BeautifulSoup(response.content, 'lxml')
        navigation_bar = soup.find_all('div', {'class': "nav-progressive-content"})
        if len(navigation_bar)<1:
            raise IndexError("find_categories Failed")
        try:
            navigation_bar=navigation_bar[1]
        except IndexError:
            raise IndexError("find_categories Failed")
        navigation_bar_items = navigation_bar.find_all('a')[4:]
        categories = []
        total = len(navigation_bar_items)
        # with alive_bar(total, bar='filling', title='Gathering Categories') as bar:
        for a in navigation_bar_items:
            categories.append((a.text,"https://www.amazon.eg" + a.attrs['href']))
        # https: // www.amazon.eg / - / en / % D9 % 85 % D9 % 88 % D8 % B6 % D8 % A9 / b /?ie = UTF8 & node = 18018165031 & ref_ = nav_cs_fashion_955d436ca76f494aad7f471fb2881b08
        self.save_categories(categories=categories) #Categories saved here
        return categories
    def see_all_results(self):
        """Scraping the see all results button link for each category"""
        categories=[]
        for (category_name,category_link) in self.categories_first_page:
            response = requests.get(url=category_link)
            soup = BeautifulSoup(response.content, 'lxml')
            buttons=soup.select(selector="div > div > div >div > div > div > a ")
            for button in buttons:
                if button.text=="See all results":
                   categories.append((category_name,"https://www.amazon.eg" + button.attrs['href']))
        self.save_categories(categories=categories)  # Categories saved here
        return categories





    def __str__(self):
        return self.value


if __name__ == "__main__":
    amazon = Amazon()

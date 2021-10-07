import pandas
import csv
import os
# https://www.geeksforgeeks.org/how-to-convert-dictionary-to-pandas-dataframe/

class Inventory:
    def __init__(self,my_products):
        self.my_products = my_products


    def prepare_data(self):
        if os.path.exists("../static/files/user_inventory.csv"):
            os.remove("../static/files/user_inventory.csv")
        # data = [{'area': 'new-hills', 'rainfall': 100, 'temperature': 20},
        #         {'area': 'cape-town', 'rainfall': 70, 'temperature': 25},
        #         {'area': 'mumbai', 'rainfall': 200, 'temperature': 39}]

        data_frame = pandas.DataFrame.from_dict(self.my_products)
        data_frame.to_csv("./static/files/user_inventory.csv")


def save_page_data(self, data_rows, name, titles):
        """Save categories_first_page incase amazon bot detected us"""
        with open(f'/saved/{name}_page.csv', 'w') as file:
            write = csv.writer(file)
            write.writerow(titles)
            write.writerows(data_rows)
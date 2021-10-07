import pandas
import csv
import os
# https://www.geeksforgeeks.org/how-to-convert-dictionary-to-pandas-dataframe/

class Profile:
    def __init__(self,my_profile):
        self.my_profile = my_profile
    def prepare_data(self):
        if os.path.exists("../static/files/user_profile.csv"):
            os.remove("../static/files/user_profile.csv")
        # data = [{'area': 'new-hills', 'rainfall': 100, 'temperature': 20},
        #         {'area': 'cape-town', 'rainfall': 70, 'temperature': 25},
        #         {'area': 'mumbai', 'rainfall': 200, 'temperature': 39}]

        data_frame = pandas.DataFrame.from_dict(self.my_profile)
        data_frame=data_frame[['name','phone','email',	'api_key','gender','status','country',	'birth_date'	,'number_of_products','since_date']]
        data_frame=data_frame.drop(['api_key'],axis=1)
        data_frame.to_csv("./static/files/user_profile.csv")



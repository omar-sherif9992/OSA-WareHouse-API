import os
from user import User
class Company:
    """Creates a Company"""
    def __init__(self, company):
        self.company = company
        self.name = company.name
        self.country = company.country
        self.email = company.email
        self.phone = company.phone
        self.birth_date = None
        self.gender=None
        self.service=company.service
        self.company_url=company.company_url




import os

class User:
    """Creates a user"""
    def __init__(self, user):
        self.company=user
        self.name=user.name
        self.country=user.country
        self.email=user.email
        self.phone=user.phone
        self.birth_date=user.birth_date

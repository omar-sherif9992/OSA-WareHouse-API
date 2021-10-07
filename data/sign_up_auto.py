from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from user import User
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

URL = "http://127.0.0.1:5000/register"


def sign_up_user(user):
    """"It register for a user """

    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    browser = webdriver.Chrome(options=op)
    browser.get(url=URL)

    sleep(2)

    email_input = browser.find_element_by_id('email')
    email_input.send_keys(user.email)

    name_input = browser.find_element_by_id('name')
    name_input.send_keys(user.name)

    phone_input = browser.find_element_by_id('phone')
    phone_input.send_keys(user.phone)

    country_input = browser.find_element_by_id('country')
    country_input.select_by_visible_text(user.country)

    status_input = browser.find_element_by_id('status-0')
    status_input.click()

    gender_input = browser.find_element_by_id('gender')
    gender_input.select.select_by_visible_text(user.gender)

    submit_input = browser.find_element_by_id('submit')
    submit_input.click()

    #laoding while registering
    sleep(6)


    try:
        # It means that i am in the thank you page which doesnt have a name input field
        name_input = browser.find_element_by_id('name')
    except NoSuchElementException:
        browser.close()
        return True

    browser.close()
    return False


def sign_up_company(company):
    """"It register for a Company """
    # browser = webdriver.Chrome()
    # browser.get(url=URL)
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    browser = webdriver.Chrome(options=op)
    browser.get(url=URL)
    sleep(1)
    email_input = browser.find_element_by_id('email')
    email_input.send_keys((company.email).title())

    name_input = browser.find_element_by_id('name')
    name_input.send_keys((company.name).title())

    phone_input = browser.find_element_by_id('phone')
    phone_input.send_keys(company.phone)

    country_input = Select(browser.find_element_by_id('country'))
    country_input.select_by_value(company.country)
    sleep(1.5)
    status_input = browser.find_element_by_id('status-1')
    status_input.click()

    service_input = Select(browser.find_element_by_id('service'))
    service_input.select_by_value((company.service).title())

    company_url_input = browser.find_element_by_id('company_url')
    company_url_input.send_keys(company.company_url)


    submit_input = browser.find_element_by_id('submit')
    submit_input.click()

    sleep(6)

    try:
        # It means that i am in the thank you page which doesnt have a name input field
        name_input = browser.find_element_by_id('name')
    except NoSuchElementException:
        browser.close()
        return True

    browser.close()
    return False

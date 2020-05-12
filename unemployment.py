#!/usr/bin/python3
import os
import sys
import json
import time
from selenium import webdriver

# load config for credentials
dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = f"{dir_path}/config.json"

if os.path.isfile(config_path) is False:
    raise Exception(
        f"Ensure {config_path} is a file and has username and password fields defined"
    )

with open(config_path) as json_file:
    data = json.load(json_file)

username = data.get("username")
password = data.get("password")

if None in [username, password]:
    raise Exception(
        f"{config_path} file exists but unable to parse username and/or password fields"
    )

driver = webdriver.Chrome()
driver.maximize_window()

# sign in
driver.get("https://applications.labor.ny.gov/Individual/")
username_field = driver.find_element_by_id("USERNAME")
password_field = driver.find_element_by_id("PASSWORD")
sign_in_button = driver.find_element_by_class_name("signinButtonDiv")
username_field.send_keys(username)
password_field.send_keys(password)
sign_in_button.click()

# unemployment services
driver.get(
    "https://applications.labor.ny.gov/Individual/UIES/UIESConnectivity?DEST=UI&LOCALE=en_US"
)
time.sleep(2)
content = driver.find_element_by_id("content")
if "You have already claimed benefits for this week" in content.text:
    driver.close()
    raise Exception("Benefits already claimed this week")
time.sleep(1)
certify_form_link = "UserAuthenticationServlet"
payment_history_form_link = "viewHistory"
forms = driver.find_elements_by_tag_name("form")

found = False
for form in forms:
    if found:
        break
    if certify_form_link in form.get_attribute("action"):
        input_children = form.find_elements_by_tag_name("input")
        for child in input_children:
            if "submit" == child.get_attribute("type"):
                child.click()
                found = True

found = False
forms = driver.find_elements_by_tag_name("form")
for form in forms:
    if found:
        break
    if "beginClaim" in form.get_attribute("action"):
        input_children = form.find_elements_by_tag_name("input")
        for child in input_children:
            if "submit" == child.get_attribute("type"):
                child.click()
                found = True
time.sleep(1)

# certify weekly benefits
buttons = driver.find_elements_by_tag_name("button")
for button in buttons:
    if "Certify Benefits" in button.get_attribute("value"):
        button.click()
        break


print("1. During the week ending 5/10/2020, did you refuse any job offer or referral?")
driver.find_element_by_id("G05_REFUSE_OFFER0").click()

from selenium.webdriver.support.ui import Select

print(
    "2. How many days did you work, including self-employment, during the week ending 5/10/2020?"
)
days_worked_select = driver.find_element_by_id("G05_TOTAL_DAYS_WORKED")
Select(days_worked_select).select_by_value("0")

print(
    "\t2a. Excluding earnings from self-employment, did you earn more than $504? - N/A"
)
driver.find_element_by_id("G05_EXCEEDED_MAX_EARNINGS3").click()

print("3. How many days were you NOT ready, willing, and able to work?")
days_not_ready_select = driver.find_element_by_id("G05_DAYS_NOT_RWA")
Select(days_not_ready_select).select_by_value("0")

print("4. How many days were you owed vacation pay or did you receive vacation pay?")
days_vacation_paid_select = driver.find_element_by_id("G05_VACATION_PAY_DAYS")
Select(days_vacation_paid_select).select_by_value("0")

print("5. How many days were you owed holiday pay or did you receive holiday pay?")
days_holiday_paid_select = driver.find_element_by_id("G05_HOLIDAY_PAY_DAYS")
Select(days_holiday_paid_select).select_by_value("0")

print("6. Have you returned to work?")
driver.find_element_by_id("G05_RETURNED_FULL_TIME0").click()

buttons = driver.find_elements_by_tag_name("button")
for button in buttons:
    if "Continue" in button.get_attribute("value"):
        button.click()
        break


buttons = driver.find_elements_by_tag_name("button")
for button in buttons:
    if "Certify Claim" in button.get_attribute("value"):
        button.click()
        break
time.sleep(10)
driver.close()

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# Scrape all of the user data and put it in a csv file
# Then make a program that takes those csv files and merges them into one
# Then make a program that allows you to find the top anime and how many people its shared by


driver = webdriver.Chrome() # Give this later
wait = WebDriverWait(driver, 5) # Look up what this does

# Type username of the person you want here:
user_name = ""

links = []

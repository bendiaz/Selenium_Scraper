import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

import os
from pathlib import Path
import glob



###if chromedriver doesn't have permissions then navigate to folder where chromedriver is and
### allow permissions by running this in the terminal (MacOS):
# $ xattr -d com.apple.quarantine chromedriver 


# a = [
# "Curriculum Review",
# "annual update",
# "memorandum of understanding",
# "cirriculum map",
# "Institutional Assessment",
# "Assessment of Learning",
# "Student Learning Outcomes",
# "Institutional Learning Outcomes",
# "Outcomes Assessment",
# "Assessment",
# "Program Review",
# "Academic Program Review",
# "Co-Curricular Program Review",
# "Campus Unit Program Review",
# "Non-Academic Program Review",
# "Student Affairs Program Review",
# "Continuous Improvement",
# "Quality Assurance",
# "General Education",
# "General Education Review"

# ]


# b = [
#     "Azusa Pacific University",
# "Biola University ",
# "California Baptist University",
# "California Lutheran University",
# "Chapman University",
# "Gonzaga University",
# "Loma Linda University",
# "Loyola Marymount University",
# "Occidental College", 
# "Pacific Lutheran University",
# "Pacific University",
# "Pepperdine University",
# "Pitzer College",
# "Point Loma Nazarene University",
# "Saint Mary's College of California",
# "Seattle Pacific University",
# "Seattle University", 
# "University of Portland",
# "University of Puget Sound",
# "University of Redlands",
# "University of San Diego",
# "University of San Francisco",
# "University of the Pacific",
# "Westmont College",
# "Whitman College",
# "Whittier College"
# ] 

# #uneven works lists work



# c = [
# "mathematics"
# ]

INST_PATH = "/Users/adiaz3/Desktop/python stuff/Web Scraping for Program Review/keywords/MBA ETS MFT Institutions.csv"
WORD_PATH = "/Users/adiaz3/Desktop/python stuff/Web Scraping for Program Review/keywords/MBA ETS MFT Keywords.csv"

a_data = pd.read_csv(INST_PATH, delimiter=",", names =["name"] )
b_data = pd.read_csv(WORD_PATH, delimiter=",", names =["name"] )

a = a_data["name"].values.tolist()
b = b_data["name"].values.tolist()

# print(a)
# print(b)

keys = []


for x,y in [(x,y) for x in a for y in b]:
    keys.append(x +" "+ y)

# for x,y,z in [(x,y,z) for x in a for y in b for z in c]:
#     keys.append(z +" "+ x +" "+ y)

links_list = []




path_to_driver = r"/Users/adiaz3/Desktop/python stuff/Web Scraping for Program Review/chromedriver"
download_dir = r"/Users/adiaz3/Desktop/python stuff/Web Scraping for Program Review/pdf_dump"

dwn_dir = Path("/Users/adiaz3/Desktop/python stuff/Web Scraping for Program Review/pdf_dump")

'''these lines below set the options to hide the application, allows chrome to work in the background and
ignore any certificate errors that may arise, then it sends the commands and tells it to download
into the download path we set in our directory

the for loop waits 10 seconds (decent laod time for any OS), loads google, waits another 5,
sends in the query (our lists we passed a+b+c) then moves down 1 (our first search result) and searches
for a pdf, counts down for us and tells us whether the pdf exists or not, downloads (or not) then moves
onto the next query we want to pass into google, no matter if a pdf exists or if there's no 
search result...
'''

chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
  "download.default_directory": download_dir,
  "download.prompt_for_download": False,
})
chrome_options.add_argument("--headless")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--incognito")
driver = webdriver.Chrome(path_to_driver, options=chrome_options)
driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
command_result = driver.execute("send_command", params)

for k, key in enumerate(keys):
    try:
        start = time.time()
        driver.implicitly_wait(10)
        driver.get("https://www.google.com/")

        sleep_between_interactions = 5
        searchbar = driver.find_element_by_name("q")
        searchbar.send_keys(key)
        searchbar.send_keys(Keys.ARROW_DOWN)
        searchbar.send_keys(Keys.RETURN)
        pdf_element = driver.find_elements(By.XPATH, ("//a[contains(@href, '.pdf')]"))
        key_index_number = str(keys.index(key) +1 )
        key_length = str(len(keys))
        print(key_index_number + " out of " + key_length)
            
        if len(pdf_element) > 0 and  key_length < key_index_number :
            print("pdf found for: "+ key)
            pdf_element[0].click()
            time.sleep(sleep_between_interactions)
            #let's try here
            # os.rename(str(pdf_element[0]),str(key)+'_'+str(key_index_number)+'.pdf') #doesn't work because pdf_element isn't actual file
            #end of attempt
            print("downloaded " + key_index_number + " out of "+ str(len(keys)))
            


            # # this code kinda works, but it rewrites EVERY file which is unhelpful
            # for f,file in enumerate(dwn_dir.iterdir()):
            #     if file.is_file() and file.stem != ".DS_Store":
            #         directory = file.parent
            #         extension = file.suffix
            #         old_name = file.stem
            #         new_name = f'{key}-{key_index_number}{extension}'
            #         file.rename(Path(old_name, new_name))
                
                
        elif len(pdf_element) == 0 and key_index_number != key_length:
            print("pdf NOT found for "+ key)
            print(key + " pdf not downloaded, moving on...")  
            
            
 
            
            try:
                google_search = f"https://www.google.com/search?q={key}"
                driver.get(google_search)
                clicked_link = driver.find_element(By.XPATH, '(//h3)[1]/../../a').click()
                driver.implicitly_wait(10)

            except JavascriptException:
                continue
                html_source_code = driver.execute_script("return document.body.innerHTML;")
                html_soup: BeautifulSoup = BeautifulSoup(html_source_code, 'html.parser')
                links_list = [html_soup for potato in html_soup.find_all('a')]
                
            
        elif len(pdf_element) == 0 and str(keys.index(key)) == str(len(keys)):
            print('Empty')
            
    except IndexError as index_error:
        print("Couldn't find pdf file for "+"\"" + key + "\""+" due to Index Error moving on....")
        print(key_index_number + " out of " + str(len(keys)))
        continue
    except NoSuchElementException:
        print("search bar didn't load, iterating next in loop")
        print(" pdf NOT found for "+ key)
        print(key + " pdf not downloaded, moving on...")
        continue
    except ElementNotInteractableException:
        print("element either didn't load or doesn't exist")
        driver.get("https://www.google.com/")
        continue
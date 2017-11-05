#HKUST ARR Schedule WebSpider(WIP)
#Author: Patrick Wu(@patrick330602)
import os
from time import gmtime, strftime
import requests

from bs4 import BeautifulSoup as bs

ver = "v0.1"
dept_link = []
total_count = 0

def info_print(input):
    print("["+strftime("%H:%M:%S", gmtime())+"]"+input)

info_print("HKUST ARR Schdule WebSpider "+ver)
info_print("Constructing connections...")
base_req = requests.get("https://w5.ab.ust.hk/wcq/cgi-bin/")
info_print("Connection established.")
base_res = base_req.text
base_soup = bs(base_res, 'lxml')
base_course = base_soup.select("div.depts > a")
for cotitle in base_course:
    dept_link.append(cotitle.get("href"))
if not os.path.exists("courses"):
    os.makedirs("courses")
for x in dept_link:
    url = 'https://w5.ab.ust.hk'+x
    info_print("Connecting to "+url+"...")
    req = requests.get(url)
    info_print("Connection Established.")
    res = req.text
    soup = bs(res, 'lxml')
    needed_data = soup.select("[class~=course]")
    data_count = 0
    for course in needed_data:
        course_soup = bs(str(course), 'lxml')
        course_title = course_soup.find('a').get('name')
        source = open("courses/"+course_title+".html","w+")
        source.write(str(course_soup))
        data_count += 1
        total_count += 1
    info_print("complete retrive "+str(data_count)+" course(s).")
info_print("Action complete. Retrived "+str(total_count)+" course(s).")

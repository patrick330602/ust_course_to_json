#HKUST ARR Schedule WebSpider(WIP)
#Author: Patrick Wu(@patrick330602)
import os
from time import gmtime, strftime
import requests
import json
from bs4 import BeautifulSoup as bs

ver = "v0.1"
dept_link = []
total_count = 0
baseJsonStr = {}

'''Beautify Print'''
def info_print(input):
    print("["+strftime("%H:%M:%S", gmtime())+"]"+input)

'''Convert Raw Course HTML to json object(WIP)'''
def arr2json(input):
    course_soup = bs(str(input), 'lxml')
    course_title = course_soup.find('a').get('name')
    source = open("courses/"+course_title+".html","w+")
    baseJsonStr['courses'][course_title] = {'id': course_title}
    source.write(str(course_soup))

baseJsonStr['courses'] = {}
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
    info_print("Retrive data from "+url+"...")
    req = requests.get(url)
    res = req.text
    soup = bs(res, 'lxml')
    needed_data = soup.select("[class~=course]")
    data_count = 0
    for course in needed_data:
        arr2json(course)
        data_count += 1
        total_count += 1
    info_print("complete retrive "+str(data_count)+" course(s).")
result = open("courses_dict.json", "w+")
result.write(json.dumps(baseJsonStr))
info_print("Action complete. Retrived "+str(total_count)+" course(s).")

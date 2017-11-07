#!/usr/bin/env python3
#HKUST ARR Schedule WebSpider(WIP)
#Author: Patrick Wu(@patrick330602)
import os
import shutil
import time
import json
import re
import requests
from bs4 import BeautifulSoup as bs

ver = "v0.1"
dept_link = []
baseJsonStr = {}

def info_print(input):
    '''Beautify Print
    '''
    print("["+time.strftime("%H:%M:%S", time.localtime())+"]"+input)

def course2deptcode(input):
    '''Convert course code to department code and numerial course code
    '''
    return input[:4],input[(len(input)-4):] 

def title2creditname(input):
    '''Convert title to credit and name
    '''
    credit_untrimed = re.search('\([\s\S]+\)',input)
    credit = (re.search('\d',credit_untrimed[0]))[0]
    name_untrimed = re.search('-\s[\s\S]+\s\(', input)
    name = name_untrimed[0].replace('- ','').replace(' (','')
    return credit, name

def arr2json(input):
    '''Convert Raw Course HTML to json object
    '''
    course_soup = bs(str(input), 'lxml')
    course_title = course_soup.find('a').get('name')
    source = open("courses/"+course_title+".html","w+")

    #Overivew
    dept,code = course2deptcode(course_title)
    credit,name = title2creditname(str(course_soup.find('h2').next))

    #Detail
    detail_data = []
    detail_soup = course_soup.find('table', attrs={'width':'400'})
    rows = detail_soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        detail_data.append([ele for ele in cols if ele])

    baseJsonStr['courses'][course_title] = {'id': course_title, 'department': dept, 'code':code,'credit':credit,'name': name, 'details':{}, 'sections':[]}

    baseJsonStr['courses'][course_title]['details']['description'] = detail_data[-1]
    source.write(str(course_soup))

def main():
    total_count = 0
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
        req = requests.get(url)
        res = req.text

        soup = bs(res, 'lxml')
        needed_data = soup.select("[class~=course]")
        data_count = 0
        for course in needed_data:
            arr2json(course)
            data_count += 1
            total_count += 1
        info_print("complete retrive "+str(data_count)+" course(s) from "+url+".")
    #shutil.rmtree('courses')
    result = open("courses_dict.json", "w+")
    result.write(json.dumps(baseJsonStr))
    info_print("Action complete. Retrived "+str(total_count)+" course(s).")

if __name__ == "__main__":
    main()

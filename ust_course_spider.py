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

dept_links = []
baseJsonStr = {}

def info_print(input):
    '''Beautify Print
    '''
    print("["+time.strftime("%H:%M:%S", time.localtime())+"]"+input)

def course2deptcode(input):
    '''Convert course code to department code and numerial course code
    '''
    return input[:4], input[(len(input)-4):] 

def title2creditname(input):
    '''Convert title to credit and name
    '''
    credit_untrimed = re.search('\([\s\S]+\)', input)
    credit = (re.search('\d', credit_untrimed[0]))[0]
    name_untrimed = re.search('-\s[\s\S]+\s\(', input)
    name = name_untrimed[0].replace('- ', '').replace(' (', '')
    return credit, name

def arr2json(input):
    '''Convert Raw Course HTML to json object
    '''
    course_soup = bs(str(input), 'lxml')
    course_title = course_soup.find('a').get('name')
    #Overivew
    dept, code = course2deptcode(course_title)
    credit, name = title2creditname(str(course_soup.find('h2').next))

    baseJsonStr['courses'][course_title] = {}
    baseJsonStr['courses'][course_title]['id'] = course_title
    baseJsonStr['courses'][course_title]['department'] = dept
    baseJsonStr['courses'][course_title]['code'] = code
    baseJsonStr['courses'][course_title]['credit'] = credit
    baseJsonStr['courses'][course_title]['name'] = name

    #Details
    detail_data = {}
    baseJsonStr['courses'][course_title]['details'] = {}
    
    detail_soup = course_soup.find('table', attrs={'width':'400'})
    for row in detail_soup.find_all('tr'):
        headers = row.find('th')
        subdata = row.find('td')
        if str(headers.next) == "INTENDED":
            break
        detail_data[str(headers.next)] = subdata.next
    
    detail_strings = ['ATTRIBUTES','VECTOR', 'PRE-REQUISITE', 'CO-REQUISITE', 'PREVIOUS CODE', 'EXCLUSION']
    for dstring in detail_strings:
        if dstring in detail_data:
            content = detail_data[dstring]
            baseJsonStr['courses'][course_title]['details'][dstring.lower()] = content

    desc = detail_data['DESCRIPTION']
    desc = re.sub(r'[\xc2-\xf4][\x80-\xbf]+',lambda m: m.group(0).encode('latin1').decode('utf8'),desc)
    baseJsonStr['courses'][course_title]['details']['description'] = desc

    #Sections
    baseJsonStr['courses'][course_title]['sections'] = []

def main():
    total_count = 0
    baseJsonStr['courses'] = {}

    info_print("HKUST ARR Schdule WebSpider")
    info_print("Constructing connections...")
    base_req = requests.get("https://w5.ab.ust.hk/wcq/cgi-bin/")
    base_req.encoding = 'utf-8'
    base_res = base_req.text
    base_soup = bs(base_res,'lxml')
    base_course = base_soup.select("div.depts > a")

    for cotitle in base_course:
        dept_links.append(cotitle.get("href"))

    for link in dept_links:
        url = 'https://w5.ab.ust.hk'+link
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
    result = open("courses_dict.json", "w+")
    result.write(json.dumps(baseJsonStr))
    info_print("Action complete. Retrived "+str(total_count)+" course(s).")

if __name__ == "__main__":
    main()

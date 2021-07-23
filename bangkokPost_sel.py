import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

import pandas as pd
import os
import sys
import time
import datetime

url = "https://search.bangkokpost.com/search/result?start=0&q=korea&category=all&refinementFilter=&sort=newest&rows=10"
driver = webdriver.Chrome(executable_path='./chromedriver')
driver.implicitly_wait(time_to_wait=5)

driver.get(url=url)


def process_datetime(type, info):
    if type == 0:
        date_obj = datetime.datetime.strptime(info, "%d %b %Y at %H:%M")
        date = date_obj.strftime("%Y-%m-%d")
        times = date_obj.strftime("%H:%M")
        return date + " " + times + ":00"
    else:
        date_obj = datetime.datetime.strptime(info, "%d/%m/%Y")
        date = date_obj.strftime("%Y-%m-%d")
        return date + " " + "00:00:00"

def get_content(href):
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url=href)
    time.sleep(3)
    dt = 0
    content = ""
    try:
        body = driver.find_element_by_class_name("articl-content")
        article = body.find_elements_by_xpath("./p")
        for b in article:
            content += b.get_attribute("textContent").strip()
        dt = driver.find_element_by_class_name("article-info").find_element_by_xpath("./div/div/p").get_attribute("textContent")
        dt = process_datetime(0, dt[11:].strip())
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return [dt, content]
    except NoSuchElementException or KeyboardInterrupt:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return [dt, content]
    return [0, 0]


def get_html():
    results = {}
    results['country'] = list()
    results['media'] = list()
    results['date'] = list()
    results['headline'] = list()
    results['article'] = list()
    results['url'] = list()
    try:
        curBtn = driver.find_element_by_class_name("page-Navigation").find_element_by_class_name("active")
        while curBtn.find_element_by_xpath("following-sibling::a"):
            time.sleep(3)
            lists = driver.find_element_by_class_name("SearchList").find_elements_by_xpath("./li")
            for li in lists:
                if len(str(li.get_attribute('class'))) == 0:
                    article = li.find_element_by_class_name("detail")
                    title = article.find_element_by_xpath("./h3/a").get_attribute("textContent")
                    href = article.find_element_by_xpath("./h3/a").get_attribute("href")
                    [date, content] = get_content(href)
                    if date == 0:
                        date = process_datetime(1, article.find_element_by_class_name("writerdetail").find_element_by_xpath("./span/a").get_attribute("textContent"))
                    if date != 0 and content != 0:
                        results['country'].append('Thailand')
                        results['media'].append('Bangkok Post')
                        results['date'].append(date)
                        results['headline'].append(title)
                        results['article'].append(content)
                        results['url'].append(href)
            driver.get(curBtn.find_element_by_xpath("following-sibling::a").get_attribute("href"))
            curBtn = driver.find_element_by_class_name("page-Navigation").find_element_by_class_name("active")
    except NoSuchElementException or KeyboardInterrupt as e:
        driver.close()
        return results
    return results


if __name__ == '__main__':
    xlxs_dir = "./BangkokPost.xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    csv = get_html()
    dict_to_df = pd.DataFrame.from_dict(csv)
    dict_to_df.to_excel(writer, sheet_name="Bangkok Post")
    writer.save()
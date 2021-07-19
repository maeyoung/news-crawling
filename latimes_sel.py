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

url = "https://www.latimes.com/search?q=korea&s=1&p=1"
options = webdriver.ChromeOptions()
options.add_argument('disable-gpu')
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-ssl-errors')
# options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')
options.add_argument("lang=ko_KR")


driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=options)
driver.implicitly_wait(time_to_wait=5)
driver.get(url=url)

def process_datetime(type, info):
    if type == 0:
        date = info[:10]
        time = info[11:19]
        return date + " " + time
    else:
        date_obj = datetime.datetime.fromtimestamp(info/100)
        date = date_obj.strftime("%Y-%m-%d")
        times = date_obj.strftime("%H:%M:%S")
        return date + " " + times



def get_content(href):
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url=href)
    time.sleep(3)
    date = 0
    content = ""
    try:
        body = driver.find_element_by_class_name("rich-text-article-body")
        article = body.find_elements_by_xpath("./div/p | ./div/ul/li")
        for b in article:
            content += b.get_attribute("textContent").strip()
        date = driver.find_element_by_class_name("byline").find_element_by_tag_name("time").get_attribute("datetime")
        date = process_datetime(0, date)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return [date, content]
    except NoSuchElementException or KeyboardInterrupt:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return [date, content]
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
        nextBtn = driver.find_element_by_class_name("search-results-module-next-page")
        i = 1
        while nextBtn.find_element_by_tag_name("a"):
            if (i % 10 == 0):
                time.sleep(5)
            time.sleep(3)
            lists = driver.find_element_by_class_name("search-results-module-results-menu").find_elements_by_tag_name("li")
            for li in lists:
                article = li.find_element_by_class_name("promo-title")
                title = article.find_element_by_tag_name("a").get_attribute("textContent")
                href = article.find_element_by_tag_name("a").get_attribute("href")
                [date, content] = get_content(href)
                if date == 0:
                    date = process_datetime(1, int(li.find_element_by_class_name("promo-timestamp").get_attribute("data-timestamp")))
                if date != 0 and content != 0:
                    results['country'].append('USA')
                    results['media'].append('LATimes')
                    results['date'].append(date)
                    results['headline'].append(title)
                    results['article'].append(content)
                    results['url'].append(href)
            driver.get(nextBtn.find_element_by_tag_name("a").get_attribute("href"))
            nextBtn = driver.find_element_by_class_name("search-results-module-next-page")
            i += 1
    except KeyboardInterrupt or NoSuchElementException:
        driver.close()
        return results
    return results

if __name__ == '__main__':
    xlxs_dir = "./LATimes.xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    csv = get_html()
    dict_to_df = pd.DataFrame.from_dict(csv)
    dict_to_df.to_excel(writer, sheet_name="LA TIMES")
    writer.save()

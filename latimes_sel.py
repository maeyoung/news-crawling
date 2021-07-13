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
import time

url = "https://www.latimes.com/search?q=korea&s=1&p=3"
driver = webdriver.Chrome(executable_path='chromedriver')
driver.implicitly_wait(time_to_wait=5)

driver.get(url=url)


def process_datetime(info):
    date = info[:10]
    time = info[11:19]
    return date + " " + time


def get_content(href):
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url=href)
    time.sleep(3)
    datetime = driver.find_element_by_class_name("byline").find_element_by_tag_name("time").get_attribute("datetime")
    datetime = process_datetime(datetime)
    try:
        body = driver.find_element_by_class_name("rich-text-article-body")
        article = body.find_elements_by_xpath("./div/p")
        content = ""
        for b in article:
            content += b.get_attribute("textContent").strip()
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return [datetime, content]
    except NoSuchElementException:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
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
        time.sleep(2)
        while nextBtn.find_element_by_tag_name("a"):
            lists = driver.find_element_by_class_name("search-results-module-results-menu").find_elements_by_tag_name(
                "li")
            for li in lists:
                article = li.find_element_by_class_name("promo-title")
                title = article.find_element_by_tag_name("a").get_attribute("textContent")
                href = article.find_element_by_tag_name("a").get_attribute("href")
                [date, content] = get_content(href)
                if date != 0 and content != 0:
                    results['country'].append('USA')
                    results['media'].append('LATimes')
                    results['date'].append(date)
                    results['headline'].append(title)
                    results['article'].append(content)
                    results['url'].append(href)
            driver.get(nextBtn.find_element_by_tag_name("a").get_attribute("href"))
            nextBtn = driver.find_element_by_class_name("search-results-module-next-page")
    except NoSuchElementException:
        driver.close()
        return results
    return results


if __name__ == '__main__':
    ############################### TODO :: edit path ############################
    base_dir = "C:/Users/kimjiwoo/Desktop/"
    ##############################################################################
    file = "LATimes.xlsx"
    xlxs_dir = os.path.join(base_dir, file)
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    csv = get_html()
    dict_to_df = pd.DataFrame.from_dict(csv)
    dict_to_df.to_excel(writer, sheet_name="LA TIMES")
    writer.save()

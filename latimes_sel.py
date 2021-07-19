# import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver import ActionChains

# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By

# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.support.ui import WebDriverWait

import pandas as pd
# import os
# import sys
import time
import datetime

results = {}
results['country'] = list()
results['media'] = list()
results['date'] = list()
results['headline'] = list()
results['article'] = list()
results['url'] = list()

url = "https://www.google.com/search?q=site%3Ahttps%3A%2F%2Fwww.latimes.com%2F+2010..2020+korea&ei=QoL1YLn9Es-UmAXI7qr4Bg&oq=site%3Ahttps%3A%2F%2Fwww.latimes.com%2F+2010..2020+korea&gs_lcp=Cgdnd3Mtd2l6EANKBAhBGAFQ-AxY5B5g1B9oAXAAeACAAdwCiAGoEpIBBzMuOS4xLjKYAQCgAQGqAQdnd3Mtd2l6wAEB&sclient=gws-wiz&ved=0ahUKEwi5puHWou_xAhVPCqYKHUi3Cm8Q4dUDCA4&uact=5"
driver = webdriver.Chrome(executable_path='./chromedriver')
driver.implicitly_wait(time_to_wait=5)
driver.get(url=url)

# get news url from google html script
def get_href_date(hrefs):
    try:
        parts = driver.find_elements_by_class_name('tF2Cxc')
        for elem in parts:
            head = elem.find_element_by_class_name('yuRUbf')
            body = elem.find_element_by_class_name('IsZvec')
            href = head.find_element_by_tag_name('a').get_attribute('href')
            date = body.find_element_by_class_name('MUxGbd.wuQ4Ob.WZ8Tjf').get_attribute("textContent")
            hrefs.append([href, date])
        # html = driver.find_elements_by_class_name('yuRUbf')
        # for elem in html:
        #     href = elem.find_element_by_tag_name('a').get_attribute('href')
        #     hrefs.append(href)
        return (hrefs)

    except KeyboardInterrupt or NoSuchElementException:
        print('Error')
        driver.close()


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


def get_content():
    date = 0
    content = ""
    try:
        body = driver.find_element_by_class_name("rich-text-article-body")
        article = body.find_elements_by_xpath("./div/p | ./div/ul/li")
        title = driver.find_element_by_class_name("page-content.paywall")
        headline = title.find_element_by_class_name("headline").get_attribute("textContent").strip()
        for b in article:
            content += b.get_attribute("textContent").strip()
        if check_is_exist("class", "byline"):
            date = driver.find_element_by_class_name("byline").find_element_by_tag_name("time").get_attribute("datetime")
            date = process_datetime(0, date)
        return [headline, date, content]
    except NoSuchElementException or KeyboardInterrupt:
        return [headline, date, content]


def get_html(hrefs):
    
    try:
       
        for link in hrefs:
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(3)

            [title, date, content] = get_content(link)
            if date == 0:
                # to-do: get date info from google lists
                continue
            if date != 0 and content != 0:
                results['country'].append('USA')
                results['media'].append('LATimes')
                results['date'].append(date)
                results['headline'].append(title)
                results['article'].append(content)
                results['url'].append(link)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except KeyboardInterrupt or NoSuchElementException:
        dict_to_df = pd.DataFrame.from_dict(results)
        dict_to_df.to_excel(writer, sheet_name="LA TIMES")
        writer.save()
        print("현재 데이터까지 저장완료")
        driver.close()
    return results

def check_is_exist(type, name):
    try:
        if (type == "class"):
            driver.find_element_by_class_name(name)
        elif (type == "id"):
            driver.find_element_by_id(name)
    except NoSuchElementException:
        return False
    return True


def check_exist_button(b_name):
    try:
        next = driver.find_element_by_id(b_name)
        next.click()
        time.sleep(3)
    except NoSuchElementException:
        return False
    return True


if __name__ == '__main__':
    hrefs = []
    hrefs = get_href_date(hrefs)
    csv = get_content(hrefs)
    while check_exist_button('pnnext'):
        hrefs = []
        hrefs = get_href_date(hrefs)
        csv = get_content(hrefs)
    xlxs_dir = "./LATimes.xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(csv)
    dict_to_df.to_excel(writer, sheet_name="LA TIMES")
    writer.save()
    print("데이터 수집 완료")
    driver.close()

import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import  NoSuchElementException

column_list = ["country", "media", "date", "headline", "article", "url"]

df = pd.DataFrame(columns=column_list)

# site:https://www.bild.de/ 2010..2020 korea
url = 'https://www.google.com/search?q=site%3Ahttps%3A%2F%2Fwww.bild.de%2F+korea&biw=1792&bih=1008&source=lnt&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2010%2Ccd_max%3A12%2F31%2F2020&tbm='
driver = webdriver.Chrome(executable_path='./chromedriver')

# remove cookie banner
# driver.get('https://www.bild.de/suche.bild.html?query=korea')
driver.get(url)

def get_href():
    hrefs = []
    try:
        html = driver.find_elements_by_class_name('yuRUbf')
        for elem in html:
            href = elem.find_element_by_tag_name('a').get_attribute('href')
            hrefs.append(href)
        # print(hrefs)
        return (hrefs)

    except KeyboardInterrupt or NoSuchElementException:
        print('Error')
        driver.close()

def process_datetime(info):
    date = info[:10]
    time = info[11:19]
    return date + " " + time

def get_data(hrefs):
    try:
        for link in hrefs:
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(3)

            data = ['German', 'Bild']

            if check_is_exist("class", "authors__pubdate") == False:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            n_date = driver.find_element_by_class_name("authors__pubdate").get_attribute("datetime")            
            n_date = process_datetime(n_date)
            # print(n_date)
            data.append(n_date)

            # 중간에 <br>있는 경우 '\n'로 들어가는거 처리하기~!~!~!~!~!~!
            news_title = driver.find_element_by_class_name("headline").text
            data.append(news_title)

            if check_is_exist("class", "txt") == False:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            body = driver.find_element_by_class_name("txt")
            article = body.find_elements_by_tag_name("p")
            content = ""
            for t in article:
                if t != "":
                    content += t.get_attribute("textContent").strip()
            data.append(content)

            data.append(driver.current_url)
            df.loc[len(df)] = data

            # print(data)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except KeyboardInterrupt or NoSuchElementException:
        xlxs_dir = "./bild.xlsx"
        writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
        df.to_excel(writer, sheet_name="bild")
        writer.save()
        print("현재 데이터까지 저장완료")
        driver.close()


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
    hrefs = get_href()
    get_data(hrefs)
    while check_exist_button('pnnext'):
        hrefs = get_href()
        get_data(hrefs)
    xlxs_dir = "./bild.xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    df.to_excel(writer, sheet_name="bild")
    writer.save()
    print("데이터 수집 완료")
    driver.close()

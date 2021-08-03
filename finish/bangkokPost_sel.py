import traceback

import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
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
url = "https://search.bangkokpost.com/search/result?q=korea&category=all&sort=newest&rows=10&refinementFilter=&publishedDate=%5B2010-01-01T00%3A00%3A00Z%3B2020-12-31T23%3A59%3A59Z%5D"
# url = "https://search.bangkokpost.com/search/result?start=0&q=korea&category=all&refinementFilter=&sort=newest&rows=10"
# url ="https://search.bangkokpost.com/search/result?start=1620&q=korea&category=all&refinementFilter=&sort=newest&rows=10"
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "normal"
driver = webdriver.Chrome(desired_capabilities=caps, executable_path='./chromedriver')
driver.implicitly_wait(time_to_wait=5)


def save(year, results):
    xlxs_dir = "./BangkokPost("+str(year)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="Bangkok Post")
    writer.save()

def check_is_exist(window, type, name):
    try:
        if (type == "class"):
            window.find_element_by_class_name(name)
        elif (type == "id"):
            window.find_element_by_id(name)
        elif (type == 'xpath'):
            window.find_element_by_xpath(name)
    except NoSuchElementException:
        return False
    return True

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
    dt = 0
    content = ""
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url=href)
    try:
        body = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "articl-content"))
        )
        article = body.find_elements_by_xpath("./p")
        for b in article:
            if len(b.get_attribute('id')) == 0:
                content += b.get_attribute("textContent").strip()
        if check_is_exist(driver, 'class', 'article-info'):
            article_info = driver.find_element_by_class_name('article-info')
            if check_is_exist(article_info, 'xpath', './div/div/p'):
                dt = article_info.find_element_by_xpath('./div/div/p').get_attribute('textContent')
            elif check_is_exist(article_info, 'xpath', './div/div/div'):
                dt = article_info.find_element_by_xpath('./div/div/div').get_attribute('textContent')
            dt = process_datetime(0, dt[11:].strip())
    except TimeoutException:
        print("타임아웃 에러: "+href)
    except NoSuchElementException or KeyboardInterrupt:
        print("요소 에러 위치: "+href)
        traceback.print_exc()
    except Exception as e:
        print("에러 위치: "+href)
        print(e)
    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return [dt, content]


def get_html(year, results):
    try:
        href = driver.current_url
        while True:
            time.sleep(3)
            lists = driver.find_element_by_class_name("SearchList").find_elements_by_xpath("./li")
            for li in lists:
                if len(str(li.get_attribute('class'))) == 0:
                    article = li.find_element_by_class_name("detail")
                    title = article.find_element_by_xpath("./h3/a").get_attribute("textContent")
                    href = article.find_element_by_xpath("./h3/a").get_attribute("href")
                    [date, content] = get_content(href)
                    if date == 0:
                        if check_is_exist(article, 'class', 'writerdetail'):
                            date = process_datetime(1, article.find_element_by_class_name("writerdetail").find_element_by_xpath("./span/a").get_attribute("textContent"))
                    if date != 0 and content != "":
                        if 'korea' in content or 'KOREA' in content or 'Korea' in content:
                            results['country'].append('Thailand')
                            results['media'].append('Bangkok Post')
                            results['date'].append(date)
                            results['headline'].append(title)
                            results['article'].append(content)
                            results['url'].append(href)
            if not check_is_exist(driver.find_element_by_class_name('page-Navigation'), 'class', 'active'):
                break
            curBtn = driver.find_element_by_class_name('page-Navigation').find_element_by_class_name('active')
            if check_is_exist(curBtn, 'xpath', 'following-sibling::a'):
                driver.get(curBtn.find_element_by_xpath("following-sibling::a").get_attribute("href"))
            else:
                break
    except KeyboardInterrupt or NoSuchElementException:
        save(year, results)
        print("현재 데이터까지 저장 완료")
        print("요소 에러 - 에러 위치: "+href)
        return 0, results
    except Exception as e:
        save(year, results)
        print("현재 데이터까지 저장 완료")
        print("기타 에러 - 에러 위치: "+href)
        print(e)
        return 0, results
    finally:
        return 1, results


if __name__ == '__main__':
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    m31 = [1, 3, 5, 7, 8, 10, 12]
    m30 = [4, 6, 9, 11]
    start = time.time()
    csv = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}
    try:
        for year in years:
            month = 1
            csv = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}
            while month < 13:
                if month == 2 and year % 4 == 0:
                    day = 29
                elif month == 2:
                    day = 28
                elif month in m30:
                    day = 30
                elif month in m31:
                    day = 31
                mindate = str(year)+"-"+str(month).zfill(2)+"-01"
                maxdate = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)
                month += 1
                url = "https://search.bangkokpost.com/search/result?q=korea&category=all&sort=newest&rows=10&refinementFilter=&publishedDate=%5B"+mindate+"T00%3A00%3A00Z%3B"+maxdate+"T23%3A59%3A59Z%5D"
                driver.get(url=url)
                status, csv = get_html(year, csv)
            save(year, csv)
            # xlxs_dir = "./BangkokPost.xlsx"
            # writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
            # dict_to_df = pd.DataFrame.from_dict(csv)
            # dict_to_df.to_excel(writer, sheet_name="Bangkok Post")
            # writer.save()
        if status == 1:
            print("데이터 수집 완료")
    except KeyboardInterrupt:
        save(year, csv)
        print("keyboard interrupt")
    except Exception as e:
        save(year, csv)
    finally:
        driver.close()
        print("소요시간 : " + str(time.time()- start)+"초")

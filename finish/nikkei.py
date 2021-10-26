

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


caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "normal"
options = webdriver.ChromeOptions()
options.add_argument('disable-gpu')
driver = webdriver.Chrome(desired_capabilities=caps, options=options, executable_path='./chromedriver')
driver.implicitly_wait(time_to_wait=5)
cnt = 0

login_url = 'https://id.nikkei.com/lounge/nl/connect/page/LA7010.seam?cid=2507060'

# login part
# driver.get(url=login_url)
# driver.find_element_by_name("LA7010Form01:LA7010Email").send_keys("cyjeon8@gmail.com")
# driver.find_element_by_name("LA7010Form01:LA7010Password").send_keys("hufsmedia")
# driver.find_element_by_class_name("btnM1").send_keys(Keys.ENTER)
# print("로그인 성공")




def save(year, results):
    xlxs_dir = "./Nikkei("+str(year)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="Nikkei")
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
        dateinfo = info.split()[0]
        dateinfo = dateinfo.strip()
        date = ""
        for i in dateinfo:
            if i.isdigit():
                date += i
            else:
                date += '-'
        timeinfo = info.split()[1]
        return date[:-1]+" "+timeinfo

def get_content(href):
    dt = 0
    content = ""
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url=href)
    try:
        body = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container_cz8tiun"))
        )
        article = body.find_elements_by_xpath("./p")
        for b in article:
            content += b.get_attribute('textContent')
        if check_is_exist(driver, 'class', 'TimeStamp_t165nkxq'):
            article_info = driver.find_element_by_class_name('TimeStamp_t165nkxq')
            date_info = article_info.find_element_by_tag_name('time').get_attribute('textContent')
            dt = process_datetime(3, date_info)
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
        driver.switch_to.window(driver.window_handles[-1])
        return [dt, content]

def get_html(year, results):
    try:
        href = driver.current_url
        if check_is_exist(driver, 'class', 'nui-button.search__more-button'):
            button = driver.find_element_by_class_name('nui-button.search__more-button')
        while button.get_attribute('aria-hidden') == "false" :
            button.click()
            button = driver.find_element_by_class_name('nui-button.search__more-button')
            time.sleep(2)
        lists = driver.find_elements_by_class_name('search__result-articles')
        for list in lists:
            items = list.find_elements_by_class_name('search__result-item')
            for item in items:
                title_info = item.find_element_by_class_name('nui-card__head')
                href = title_info.find_element_by_tag_name('a').get_attribute('href')
                title = title_info.find_element_by_tag_name('a').get_attribute('title')
                meta_info = item.find_element_by_class_name('nui-card__meta')
                if check_is_exist(meta_info, 'class', 'nui-card__icon-lock.nui-icon.nui-icon--lock-16'):
                    continue
                [date, content] = get_content(href)
                if date == 0:
                    date_info = meta_info.find_element_by_tag_name(time)
                    date = date_info.get_attribute('datetime')
                    date = date_info[0:10] + ' ' + date_info[11:16]
                if date != 0 and content != "":
                    if '韓国' in content:
                        results['country'].append('Japan')
                        results['media'].append('Nikkei')
                        results['date'].append(date)
                        results['headline'].append(title)
                        results['article'].append(content)
                        results['url'].append(href)
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
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[-1])
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
                mindate = str(year)+"/"+str(month).zfill(2)+"/01"
                maxdate = str(year)+"/"+str(month).zfill(2)+"/"+str(day).zfill(2)
                month += 1
                url = "https://r.nikkei.com/search?keyword=to%3A"+maxdate+"++from%3A"+mindate+"++%E9%9F%93%E5%9B%BD&volume=3"
                driver.get(url=url)
                status, csv = get_html(year, csv)
            save(year, csv)
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


#
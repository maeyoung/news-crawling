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
import time
import datetime


caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "normal"
options = webdriver.ChromeOptions()
options.add_argument('disable-gpu')
driver = webdriver.Chrome(desired_capabilities=caps, options=options, executable_path='./chromedriver')
driver.implicitly_wait(time_to_wait=5)
cnt = 0

monthinfo = {'January':1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July':7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December':12}
def save(year, results):
    xlxs_dir = "./VietnamNews("+str(year)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="VietnamNews")
    writer.save()

def check_is_exist(window, type, name):
    try:
        if (type == "class"):
            window.find_element_by_class_name(name)
        elif (type == "id"):
            window.find_element_by_id(name)
        elif (type == 'xpath'):
            window.find_element_by_xpath(name)
        elif (type == 'tag'):
            window.find_element_by_tag_name(name)
    except NoSuchElementException:
        return False
    return True

def process_datetime(type, info):
    if type == 0:
        date_obj = datetime.datetime.strptime(info, "%d %b %Y at %H:%M")
        date = date_obj.strftime("%Y-%m-%d")
        times = date_obj.strftime("%H:%M")
        return date + " " + times + ":00"
    elif type == 3:
        dates = info.split(",")
        month = str(monthinfo[dates[0]]).zfill(2)
        dayandtime = dates[1].strip().split()
        day= dayandtime[0].split("/")[0]
        year = dayandtime[0].split("/")[1]
        time = dayandtime[2]
        return year+"-"+month+"-"+day+" "+time
    else:
        date_obj = datetime.datetime.strptime(info, "%d/%m/%Y")
        date = date_obj.strftime("%Y-%m-%d")
        return date + " " + "00:00:00"

def get_content(href):
    dt = 0
    content = ""
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[-1])
    try:
        driver.get(url=href)
        body = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vnnews-text-post"))
        )
        article = body.find_elements_by_tag_name("p")
        for b in article:
            content += b.get_attribute("textContent") + " "
        if check_is_exist(driver, 'class', 'vnnews-time-post'):
            article_info = driver.find_element_by_class_name('vnnews-time-post').find_element_by_tag_name("span")
            dt = article_info.get_attribute('textContent').strip()
            dt = process_datetime(3, dt)
    except TimeoutException:
        print("타임아웃 에러: "+href)
    except NoSuchElementException:
        print("요소 에러 위치: "+href)
        traceback.print_exc()
    except KeyboardInterrupt:
        print("취소")
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
            lists = driver.find_element_by_class_name("vnnews-list-news").find_elements_by_xpath("./ul/li")
            for li in lists:
                if (li.get_attribute('class') == 'google-auto-placed'):
                    continue
                article = li.find_element_by_tag_name("a")
                title = article.find_element_by_class_name("vnnews-tt-list-news").get_attribute('textContent').strip()
                href = article.get_attribute("href")
                [date, content] = get_content(href)
                # if date == 0:
                #     if check_is_exist(article, 'class', 'writerdetail'):
                #         date = process_datetime(1, article.find_element_by_class_name("writerdetail").find_element_by_xpath("./span/a").get_attribute("textContent"))
                if date != 0 and content != "":
                    if 'korea' in content or 'KOREA' in content or 'Korea' in content:
                        results['country'].append('Vietnam')
                        results['media'].append('Vietnam News')
                        results['date'].append(date)
                        results['headline'].append(title)
                        results['article'].append(content)
                        results['url'].append(href)
            if not check_is_exist(driver.find_element_by_class_name('vnnews-paging'), 'tag', 'a'):
                break
            curBtn = driver.find_element_by_class_name('vnnews-paging').find_element_by_class_name('current')
            if check_is_exist(curBtn, 'xpath', 'following-sibling::a'):
                driver.get(curBtn.find_element_by_xpath("following-sibling::a").get_attribute('href'))
            else:
                break
    except KeyboardInterrupt:
        save(year, results)
        print("현재 데이터까지 저장 완료")
        print("취소 - 에러 위치: "+href)
        return 0, results
    except NoSuchElementException:
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
    years = [2016, 2017, 2018, 2019, 2020]
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
                mindate = "01/"+str(month).zfill(2)+"/"+str(year)
                maxdate = str(day).zfill(2)+"/"+str(month).zfill(2)+"/"+str(year)
                month += 1
                url = "https://vietnamnews.vn/search.html?s=korea&fd="+mindate+"&td="+maxdate+"&p=1&c=311"
                driver.get(url=url)
                time.sleep(1)
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

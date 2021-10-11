from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import pandas as pd
import sys
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

import sys, traceback
import logging
logging.basicConfig(level=logging.ERROR)

article_cnt = 0

login_url = 'https://digital.asahi.com/login/?iref=pc_gnavi&jumpUrl=https%3A%2F%2Fwww.asahi.com%2F'

caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"
driver = webdriver.Chrome(desired_capabilities=caps, executable_path='./chromedriver')
# driver = webdriver.Chrome(executable_path='./chromedriver')
# driver.implicitly_wait(time_to_wait=5)

# login part
driver.get(url=login_url)
driver.find_element_by_name("login_id").send_keys("cyjeon8@gmail.com")
driver.find_element_by_name("login_password").send_keys("hufsmedia")
driver.find_element_by_id("submitBtn").send_keys(Keys.ENTER)
print("로그인 성공")

init_results = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}

date_word = ["年", "月", "日", "時", "分"]

def data_save(status, results):
    xlxs_dir = "./Asahi("+str(status)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="Asahi")
    results = init_results
    writer.save()

def get_href_date():
    hrefs = []
    dates = []
    try:
        parts = driver.find_elements_by_class_name('tF2Cxc')
        for elem in parts:
            head = elem.find_element_by_class_name('yuRUbf')
            body = elem.find_element_by_class_name('IsZvec')
            href = head.find_element_by_tag_name('a').get_attribute('href')
            date = ""
            if check_is_exist(body, "class", 'MUxGbd.wuQ4Ob.WZ8Tjf'):
                date = body.find_element_by_class_name("MUxGbd.wuQ4Ob.WZ8Tjf").get_attribute("textContent")
            hrefs.append(href)
            if date.count(".") != 3 or date.count(" ") != 4:
                date = ""
            dates.append(process_datetime(1, date))
        return hrefs, dates
    except:
        print('error')
        driver.close()

def process_datetime(type, info):

    try:
        # tag = datetime
        if type == 0:
            date = info[:10]
            time = info[11:19]
            return date + " " + time

        # google datetime
        elif type == 1:
            if info != "":
                date_obj = datetime.strptime(info, "%Y. %m. %d. — ")
                date_obj = date_obj.replace(tzinfo=None)
                date = date_obj.strftime("%Y-%m-%d")
                return date + " " + "00:00:00"

            else:
                return "no date information"

        # tag = p
        elif type == 2:
            for word in date_word:
                info = info.replace(word, ' ')
            info = info.split()
            date = info[0]+'-'+info[1]+'-'+info[2]
            # time = info[3]+':'+info[4]+':00'
            time = "00:00:00"
            dt = datetime.strptime(date+' '+time, '%Y-%m-%d %H:%M:%S')
            return dt
    except:
        return "datetime error"


def get_data_sub(auth_date, cur_url, param, param_type, results):

    try:
        global article_cnt

        title_var = param[0]
        title_type = param_type[0]

        article_var = param[1]
        article_type = param_type[1]

        util_var = param[2]
        util_type = param_type[2]

        date_var = param[3]
        date_type = param_type[3]


        if check_is_exist(driver, title_type, title_var) == False:
            return "Error"
        if check_is_exist(driver, article_type, article_var) == False:
            return "Error"


        # date
        if check_is_exist(driver, util_type, util_var):
            util = driver.find_element_by_class_name(util_var)
            if check_is_exist(util, date_type, date_var) == False:
                date = auth_date
                # print("1 ")
            else:
                # print("util_var: " + util_var)
                if date_var == "time":
                    date = util.find_element_by_tag_name(date_var).get_attribute("datetime")
                    date = process_datetime(0, date)
                    # print("2 ")
                else:
                    date = util.find_element_by_tag_name(date_var).text
                    date = process_datetime(2, date)
                    # print("3 ")

                if date == "datetime error":
                    date = auth_date
                    # print("4 ")
        else:
            date = auth_date
            # print("5 ")

        # print(date)
        
        # headline
        if title_type == "class": 
            title = driver.find_element_by_class_name(title_var)
        else:
            title = driver.find_element_by_id(title_var)

        if check_is_exist(title, "tag", "h1") == False:
            return "Error"
        title = title.find_element_by_tag_name("h1").text
        
        # article 
        body = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, article_var))
        )
        article = body.find_elements_by_tag_name("p")
        content = ""
        for t in article:
            if t != "":
                content += t.get_attribute("textContent").strip()
        if "韓国" not in content:
            return "Error"

        # url
        results['country'].append('Japan')
        results['media'].append('Asahi')
        results['date'].append(date)
        results['headline'].append(title)
        results['article'].append(content)
        results['url'].append(cur_url)

        article_cnt += 1
        # print("article_cnt: ", article_cnt)

        return results
    
    except:
        return "Error"


def get_data(hrefs, dates, results):

    global article_cnt

    try:
        for link, auth_date in zip(hrefs, dates):

            # 사진만 있는 기사 스킵 
            if "gallery" in link or "photo" in link:
                time.sleep(3)
                continue

            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(6)

            cur_url = driver.current_url
            if cur_url == "https://www.asahi.com/":
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])
                continue

            param = [
                ["HeadLine", "BodyTxt", "Utility", "p"],
                ["Title", "ArticleText", "UpdateDate", "time"],
                ["VPrPX", "_2rW9J", "_3Xns0", "time"]
            ]
            param_type = [
                ["id", "class", "class", "tag"],
                ["class", "class", "class", "tag"],
                ["class", "class", "class", "tag"]
            ]

            for p, pt in zip(param, param_type):
                new_data = get_data_sub(auth_date, cur_url, p, pt, results)
                if new_data != "Error":
                    results = new_data
                    break

            driver.close()
            driver.switch_to.window(driver.window_handles[-1])

        if len(hrefs) < 9:
            time.sleep(40)
            # print("time wait.....")

        return results

    except TimeoutException as e:
        print(e + " : " + cur_url)
    
    except NoSuchElementException as e:
        print(e + " : " + cur_url)

    except KeyboardInterrupt:
        # data_save(year, results)
        print("취소")
        print("keyboard Interrupt")

    except:
        logging.error(traceback.print_exc())
        print("에러 위치 : " + cur_url)


def check_is_exist(window, type, name):
    try:
        if (type == "class"):
            window.find_element_by_class_name(name)
        elif (type == "id"):
            window.find_element_by_id(name)
        elif (type == "tag"):
            window.find_element_by_tag_name(name)
    except NoSuchElementException:
        return False
    return True


def check_exist_button(b_name):
    try:
        next = driver.find_element_by_id(b_name)
        next.send_keys(Keys.ENTER)
        time.sleep(3)
    except NoSuchElementException:
        return False
    return True


if __name__ == '__main__':

    years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    m31 = [1, 3, 5, 7, 8, 10, 12]
    m30 = [4, 6, 9, 11]
    start = time.time()

    try:
        for year in years:
            article_cnt = 0
            results = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}
            month = 12
            while month < 13:
                if month == 2 and year % 4 == 0:
                    day = 29
                elif month == 2:
                    day = 28
                elif month in m30:
                    day = 30
                elif month in m31:
                    day = 31
                mindate = str(month) + "/1/" + str(year)
                maxdate = str(month) + "/" + str(day) + "/" + str(year)

                search_url = "https://www.google.com/search?q=site:www.asahi.com+%E9%9F%93%E5%9B%BD&tbs=cdr:1,cd_min:" + mindate + ",cd_max:" + maxdate + "&filter=0&biw=1792&bih=1008"

                driver.execute_script("window.open();")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(url=search_url)
                # print(search_url)
                time.sleep(10)
                
                hrefs, dates = get_href_date()
                # print(hrefs)
                time.sleep(3)
                results = get_data(hrefs, dates, results)

                while check_exist_button('pnnext'):
                    hrefs, dates = get_href_date()
                    # print(hrefs)
                    time.sleep(3)
                    results = get_data(hrefs, dates, results)

                driver.close()
                driver.switch_to.window(driver.window_handles[-1])

                month += 1

            data_save(year, results)
            print(str(year) + "년 데이터 수집 완료")

    except KeyboardInterrupt:
        data_save(year, results)
        print(str(year) + "년 데이터 중간 저장")
        print("keyboard Interrupt")

    except:
        logging.error(traceback.print_exc())

    finally:
        print("최종소요시간: " + str(time.time() - start) + "초")
        driver.close()
        

# url = 'https://www.google.com/search?q=site:www.asahi.com+%E9%9F%93%E5%9B%BD&tbs=cdr:1,cd_min:01/01/2010,cd_max:12/31/2010&filter=0&biw=1792&bih=1008'
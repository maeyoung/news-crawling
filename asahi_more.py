from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import pandas as pd
import sys
import time
from datetime import datetime

import sys, traceback
import logging
logging.basicConfig(level=logging.ERROR)

article_cnt = 0

login_url = 'https://digital.asahi.com/login/?iref=pc_gnavi&jumpUrl=https%3A%2F%2Fwww.asahi.com%2F'

# caps = DesiredCapabilities().CHROME
# caps["pageLoadStrategy"] = "normal"
# driver = webdriver.Chrome(desired_capabilities=caps, executable_path='./chromedriver')
driver = webdriver.Chrome(executable_path='./chromedriver')
# driver.implicitly_wait(time_to_wait=5)

# login part
driver.get(url=login_url)
driver.find_element_by_name("login_id").send_keys("cyjeon8@gmail.com")
driver.find_element_by_name("login_password").send_keys("hufsmedia")
driver.find_element_by_id("submitBtn").send_keys(Keys.ENTER)
print("로그인 성공")

init_results = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}

date_word = ["年", "月", "日", "時", "分"]
# column_list = ["country", "media", "date", "headline", "article", "url"]
# df = pd.DataFrame(columns=column_list)

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
        if type == 0:
            date = info[:10]
            time = info[11:19]
            return date + " " + time

        elif type == 1:
            if info != "":
                date_obj = datetime.strptime(info, "%Y. %m. %d. — ")
                date_obj = date_obj.replace(tzinfo=None)
                date = date_obj.strftime("%Y-%m-%d")
                return date + " " + "00:00:00"
            else:
                return "no date information"

        elif type == 2:
            for word in date_word:
                info = info.replace(word, ' ')
            info = info.split()
            # print(info)
            date = info[0]+'-'+info[1]+'-'+info[2]
            # time = info[3]+':'+info[4]+':00'
            time = "00:00:00"
            dt = datetime.strptime(date+' '+time, '%Y-%m-%d %H:%M:%S')
            return dt
    except:
        return "datetime error"


def get_data_sub(auth_date, cur_url):

    try:
        global article_cnt

        if check_is_exist(driver, "id", "HeadLine") == False:
            return "Error"
        if check_is_exist(driver, "class", "BodyTxt") == False:
            return "Error"

        html_data = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}

        # date
        if check_is_exist(driver, "class", "Utility"):
            util = driver.find_element_by_class_name("Utility")
            if check_is_exist(util, "tag", "p") == False:
                date = auth_date
            else:
                date = util.find_element_by_tag_name("p").text
                date = process_datetime(2, date)
                if date == "datetime error":
                    date = auth_date
        else:
            date = auth_date
        
        # headline
        title = driver.find_element_by_id("HeadLine")
        if check_is_exist(title, "tag", "h1") == False:
            return "Error"
        title = title.find_element_by_tag_name("h1").text
        
        # article 
        body = driver.find_element_by_class_name("BodyTxt")
        article = body.find_elements_by_tag_name("p")
        content = ""
        for t in article:
            if t != "":
                content += t.get_attribute("textContent").strip()
        if "韓国" not in content:
            return "Error"

        # url
        html_data['country'].append('Japan')
        html_data['media'].append('Asahi')
        html_data['date'].append(date)
        html_data['headline'].append(title)
        html_data['article'].append(content)
        html_data['url'].append(cur_url)

        article_cnt += 1
        print("article_cnt 1 : ", article_cnt)

        return html_data
    
    except:
        return "Error"


def get_data(hrefs, dates, results):

    global article_cnt

    try:
        for link, auth_date in zip(hrefs, dates):

            # 사진만 있는 기사 스킵 
            if "gallery" in link:
                time.sleep(3)
                continue

            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(6)

            cur_url = driver.current_url
            if cur_url == "https://www.asahi.com/":
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

            html_data = get_data_sub(auth_date, cur_url)
            if html_data != "Error":
                results = html_data

            

            # asahi.com/articles 기준 
            else:
                # 헤드라인 있는지 또는 기사내용이 있는지 부터 확인하기
                if check_is_exist(driver, "class", "Title") == False:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                if check_is_exist(driver, "class", "ArticleText") == False:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue

                # date
                if check_is_exist(driver, "class", "UpdateDate"):
                    util = driver.find_element_by_class_name("UpdateDate")
                    if check_is_exist(util, "tag", "time") == False:
                        date = auth_date
                    else:
                        date = util.find_element_by_tag_name("time").get_attribute("datetime")
                        date = process_datetime(0, date)
                        if date == "datetime error":
                            date = auth_date
                else:
                    date = auth_date

                # headline
                title = driver.find_element_by_class_name("Title")
                if check_is_exist(title, "tag", "h1") == False:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                title = title.find_element_by_tag_name("h1").text
                
                # article 
                body = driver.find_element_by_class_name("ArticleText")
                article = body.find_elements_by_tag_name("p")
                content = ""
                for t in article:
                    if t != "":
                        content += t.get_attribute("textContent").strip()
                if "韓国" not in content:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                
                results['country'].append('Japan')
                results['media'].append('Asahi')
                results['date'].append(date)
                results['headline'].append(title)
                results['article'].append(content)
                results['url'].append(cur_url)
                article_cnt += 1
                print("article_cnt 2 : ", article_cnt)
                # print(results)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        return results

    except KeyboardInterrupt:
        data_save(year, results)
        print(str(year) + "년 데이터 중간 저장")
        print("keyboard Interrupt")

    except:
        logging.error(traceback.print_exc())
        # print(results)
        # data_save(year, results)
        print("에러 위치 : " + cur_url)
        # print("현재 데이터까지 저장완료")
        # return results

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
    # cnt = 0
    start = time.time()
    # results = init_results
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
                month += 1
                search_url = "https://www.google.com/search?q=site:www.asahi.com+%E9%9F%93%E5%9B%BD&tbs=cdr:1,cd_min:" + mindate + ",cd_max:" + maxdate + "&filter=0&biw=1792&bih=1008"
                # search_url = "https://www.google.com/search?q=site:www.asahi.com/articles+%E9%9F%93%E5%9B%BD&tbs=cdr:1,cd_min:" + mindate + ",cd_max:" + maxdate + "&ei=NfsAYbuxOs-Fr7wPj6u_0AQ&start=0&sa=N&ved=2ahUKEwj7n7DJk4XyAhXPwosBHY_VD0o4yAEQ8tMDegQIARA5&biw=1029&bih=1008"
                
                driver.get(url=search_url)
                time.sleep(3)
                
                hrefs, dates = get_href_date()
                if len(hrefs) < 9:
                    time.sleep(40)
                results = get_data(hrefs, dates, results)

                while check_exist_button('pnnext'):
                    hrefs, dates = get_href_date()
                    results = get_data(hrefs, dates, results)

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
        # driver.close()
        

# url = 'https://www.google.com/search?q=site:www.asahi.com+%E9%9F%93%E5%9B%BD&tbs=cdr:1,cd_min:01/01/2010,cd_max:12/31/2010&filter=0&biw=1792&bih=1008'
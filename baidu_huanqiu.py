from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from datetime import datetime
import sys, traceback
import logging
logging.basicConfig(level=logging.ERROR)

caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager" # interactive
driver = webdriver.Chrome(desired_capabilities=caps, executable_path='./chromedriver')

# init_results = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}

date_word = ["年", "月", "日", "時", "分"]

def data_save(status, results):
    xlxs_dir = "./Huanqiu("+str(status)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="Huanqiu")
    # results = init_results
    writer.save()

def get_href_date():
    hrefs = []
    dates = []
    try:
        parts = driver.find_elements_by_class_name('result.c-container.new-pmd')
        for elem in parts:
            head = elem.find_element_by_class_name('t')
            body = elem.find_element_by_class_name('c-abstract')
            href = head.find_element_by_tag_name('a').get_attribute('href')
            date = ""
            if check_is_exist(body, "class", 'newTimeFactor_before_abs.c-color-gray2.m'):
                date = body.find_element_by_class_name("newTimeFactor_before_abs.c-color-gray2.m").get_attribute("textContent")
            hrefs.append(href)
            for d in date:
                if not d.isdigit and d not in date_word:
                    date = ""
            dates.append(process_datetime(1, date))
        return hrefs, dates
    except:
        driver.close()
        logging.error(traceback.print_exc())


def process_datetime(type, info):
    if type == 0:
        return info + ":00"
    elif type == 1:
        if info != "":
            date_obj = datetime.strptime(info, "%Y年%m月%d日 ")
            date = date_obj.strftime("%Y-%m-%d")
            return date + " " + "00:00:00"
        else:
            return "no date information"


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
        btns = driver.find_elements_by_class_name(b_name)
        next = btns[-1]
        btn_text = next.get_attribute("textContent")
        print(btn_text)
        # 下一页 >
        if btn_text == "下一页 >":
            next.send_keys(Keys.ENTER)
            time.sleep(3)
            return True
        else:
            return False
    except NoSuchElementException as nse:
        print(nse)
        return False
    except IndexError as i:
        print(i)
        return False
    # return True

def get_data(year, hrefs, dates, results):
    try:
        for link, auth_date in zip(hrefs, dates):
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(3)

            cur_url = driver.current_url

            if check_is_exist(driver, "class", "t-container-title") == False:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            if check_is_exist(driver, "class", "l-con.clear") == False:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

            # date
            if check_is_exist(driver, "class", "time"):
                date = driver.find_element_by_class_name("time").get_attribute("textContent")
                date = process_datetime(0, date)
            else:
                date = auth_date

            # headline
            title = driver.find_element_by_class_name("t-container-title")
            if check_is_exist(title, "tag", "h3") == False:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            title = title.find_element_by_tag_name("h3").text

            # article 
            body = driver.find_element_by_class_name("l-con.clear")
            article = body.find_elements_by_tag_name("p")
            content = ""
            for t in article:
                if t != "":
                    content += t.get_attribute("textContent").strip()
            if "韩国" not in content:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

            results['country'].append('China')
            results['media'].append('Huanqiu')
            results['date'].append(date)
            results['headline'].append(title)
            results['article'].append(content)
            results['url'].append(cur_url)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        if len(hrefs) < 10:
            time.sleep(20)
            print("time wait.....")

    except:
        data_save(year, results)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print("\n\n현재 데이터까지 저장완료")
        print("에러 위치 : " + cur_url + "\n\n")
        logging.error(traceback.print_exc())


if __name__ == '__main__':
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    cnt = 0
    start = time.time()
    results = {'country':list(), 'media': list(), 'date': list(), 'headline': list(), 'article':list(), 'url': list()}
    try:
        for year in years:
            results = {'country':list(), 'media': list(), 'date': list(), 'headline': list(), 'article':list(), 'url': list()}

            month = 1
            while month < 13:
                s_min = "01/"+str(month)+"/"+str(year)+" 00:00:00"
                d_min = datetime.strptime(s_min, "%d/%m/%Y %H:%M:%S")
                r_min = time.mktime(d_min.timetuple())
                mindate = int(r_min)
                if month == 12:
                    s_max = "01/01/"+str(year+1)+" 00:00:00"
                else:
                    s_max = "01/"+str(month+1)+"/"+str(year)+" 00:00:00"
                d_max = datetime.strptime(s_max, "%d/%m/%Y %H:%M:%S")
                r_max = time.mktime(d_max.timetuple())
                maxdate = int(r_max)

                search_url = "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=site%3Ahuanqiu.com%2F%20%2B%E9%9F%A9%E5%9B%BD&ct=2097152&si=huanqiu.com%2F&fenlei=256&oq=site%3Ahuanqiu.com%2F%20%2B%E9%9F%A9%E5%9B%BD&rsv_enter=1&rsv_dl=tb&gpc=stf%3D" + str(mindate) + "%2C" + str(maxdate) + "%7Cstftype%3D2&tfflag=1"
                print("year:" + str(year) + " month: " + str(month))
                month += 1
                driver.get(url=search_url)
                time.sleep(3)

                hrefs, dates = get_href_date()
                get_data(year, hrefs, dates, results)
                while check_exist_button('n'):
                    hrefs, dates = get_href_date()
                    get_data(year, hrefs, dates, results)
            data_save(year, results)
            print(str(year)+"년 데이터 수집 완료")

    except:
        data_save(year, results)
        print("\n\n현재 데이터까지 저장완료\n\n")
        logging.error(traceback.print_exc())

    finally:
        print("\n\n최종소요시간: " + str(time.time() - start) + "초\n\n")
        driver.close()

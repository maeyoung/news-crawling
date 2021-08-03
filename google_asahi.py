from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import pandas as pd
import sys
import time
from datetime import datetime


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
driver.find_element_by_class_name("LoginBtn").send_keys(Keys.ENTER)
print("로그인 성공")

xlxs_dir = "./Asahi.xlsx"
writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')

date_word = ["年", "月", "日", "時", "分"]
column_list = ["country", "media", "date", "headline", "article", "url"]
df = pd.DataFrame(columns=column_list)

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
            if "전" in date:
                date = ""
            dates.append(process_datetime(1, date))
        return hrefs, dates

    except KeyboardInterrupt or NoSuchElementException:
        print('error')
        driver.close()

def process_datetime(type, info):
    if type == 0:
        date = info[:10]
        time = info[11:19]
        return date + " " + time
    elif type == 1:
        if info != "":
            date_obj = datetime.strptime(info, "%Y. %m. %d. — ")
            date = date_obj.strftime("%Y-%m-%d")
            return date + " " + "00:00:00"
        else:
            return "no date information"
    elif type == 2:
        for word in date_word:
            info = info.replace(word, ' ')
        info = info.split()
        print(info)
        date = info[0]+'-'+info[1]+'-'+info[2]
        # time = info[3]+':'+info[4]+':00'
        time = "00:00:00"
        dt = datetime.strptime(date+' '+time, '%Y-%m-%d %H:%M:%S')
        return dt


def get_html_content(auth_date, cur_url):
    html_data = []

    
    if check_is_exist(driver, "id", "HeadLine") == False:
        return "Error"
    if check_is_exist(driver, "class", "BodyTxt") == False:
        return "Error"

    # date
    if check_is_exist(driver, "class", "Utility"):
        date = driver.find_element_by_class_name("Utility").find_element_by_tag_name("p").text
        date = process_datetime(2, date)
    else:
        date = auth_date
    html_data.append(date)

    # headline
    title = driver.find_element_by_id("HeadLine")
    if check_is_exist(title, "tag", "h1") == False:
        return "Error"
    title = title.find_element_by_tag_name("h1").text
    html_data.append(title)

    # article 
    body = driver.find_element_by_class_name("BodyTxt")
    article = body.find_elements_by_tag_name("p")
    content = ""
    for t in article:
        if t != "":
            content += t.get_attribute("textContent").strip()
    html_data.append(content)

    # url
    html_data.append(cur_url)
    return html_data


def get_data(hrefs, dates):
    try:
        for link, auth_date in zip(hrefs, dates):
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(3)

            data = ['Japan', 'Asahi']
            cur_url = driver.current_url

            html_data = get_html_content(auth_date, cur_url)
            if html_data != "Error":
                data = data + html_data
                df.loc[len(df)] = data

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
                    date = driver.find_element_by_class_name("UpdateDate").find_element_by_tag_name("time").get_attribute("datetime")
                    date = process_datetime(0, date)
                else:
                    date = auth_date
                data.append(date)

                # headline
                title = driver.find_element_by_class_name("Title")
                if check_is_exist(title, "tag", "h1") == False:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                title = title.find_element_by_tag_name("h1").text
                data.append(title)

                # article 
                body = driver.find_element_by_class_name("ArticleText")
                article = body.find_elements_by_tag_name("p")
                content = ""
                for t in article:
                    if t != "":
                        content += t.get_attribute("textContent").strip()
                if "韓国" not in content:
                    continue
                data.append(content)
                    
                # url
                data.append(cur_url)

                # print(data)
                df.loc[len(df)] = data

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except KeyboardInterrupt or NoSuchElementException:
        df.to_excel(writer, sheet_name="Asahi")
        writer.save()
        print("다 못하고 중간에 멈췄어요!!")
        print("소요시간: " + str(time.time() - start) + "초")
        print("에러 위치 : " + cur_url)
        print("현재 데이터까지 저장완료")
        driver.close()


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
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    m31 = [1, 3, 5, 7, 8, 10, 12]
    m30 = [4, 6, 9, 11]
    cnt = 0
    start = time.time()
    try:
        for year in years:
            month = 1
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
                get_data(hrefs, dates)
                while check_exist_button('pnnext'):
                    hrefs, dates = get_href_date()
                    get_data(hrefs, dates)
        df.to_excel(writer, sheet_name="Asahi")
        writer.save()
        print("데이터 수집 완료")
        driver.close()
    except KeyboardInterrupt as k:
        print(k)
    finally:
        print("최종소요시간: " + str(time.time() - start) + "초")
        

# url = 'https://www.google.com/search?q=site:www.asahi.com+%E9%9F%93%E5%9B%BD&tbs=cdr:1,cd_min:01/01/2010,cd_max:12/31/2010&filter=0&biw=1792&bih=1008'
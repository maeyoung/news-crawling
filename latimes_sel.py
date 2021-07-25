from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys

# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.support.ui import WebDriverWait

import pandas as pd
import time
import datetime
# get error log
import logging

results = {}
results['country'] = list()
results['media'] = list()
results['date'] = list()
results['headline'] = list()
results['article'] = list()
results['url'] = list()
# url = "https://www.google.com/search?q=site:latimes.com+korea&tbs=cdr:1,cd_min:1/1/2010,cd_max:6/30/2010&sxsrf=ALeKk03Hf-An3StLLG2UrI734Sgb1u3Ryg:1627127389560&ei=Xf77YKvWIY_YhwOska3wDA&start=200&sa=N&filter=0&ved=2ahUKEwjr-Lvw0fvxAhUP7GEKHaxIC84Q8tMDegQIARBA&biw=1396&bih=694"
# url = "https://www.google.com/search?q=site%3Alatimes.com+korea&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2010%2Ccd_max%3A12%2F31%2F2020&ei=YpP2YOyMKdvdmAWDkq-ACg&oq=site%3Alatimes.com+korea&gs_lcp=Cgdnd3Mtd2l6EANKBAhBGAFQiwxYmRBgsxVoAXAAeACAAZsCiAHLBpIBBTEuMi4ymAEAoAEBqgEHZ3dzLXdpesABAQ&sclient=gws-wiz&ved=0ahUKEwjsxbGTp_HxAhXbLqYKHQPJC6AQ4dUDCA4&uact=5"

# caps = DesiredCapabilities().CHROME
# caps["pageLoadStrategy"] = "normal"
caps = DesiredCapabilities().CHROME
caps["unexpectedAlertBehaviour"] = "ACCEPT"
chrome_options = Options()
chrome_options.set_capability('unhandledPromptBehavior', 'accept')
# options = Options()
# options.set_capability("unhandledPromptBehavior", "ACCEPT") #UnexpectedAlertPresentException: Alert Text: Got metadataThe request was forbidden.  Your credentials may be denied or suspended. Message: unexpected alert open: {Alert text : Got metadataThe request was forbidden.  Your credentials may be denied or suspended.}

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='./chromedriver')
driver.implicitly_wait(time_to_wait=5)
# driver.get(url=url)

xlxs_dir = "./LATimes.xlsx"
writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')

# get news url from google html script
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
                date = body.find_element_by_class_name('MUxGbd.wuQ4Ob.WZ8Tjf').get_attribute("textContent")
            hrefs.append(href)
            if "전" in date:
                date = ""
            dates.append(process_datetime(2, date))
        return hrefs, dates

    except KeyboardInterrupt or NoSuchElementException:
        print('Error')
        driver.close()


def process_datetime(type, info):
    if type == 0:
        date = info[:10]
        time = info[11:19]
        return date + " " + time
    elif type == 1:
        date_obj = datetime.datetime.fromtimestamp(info/100)
        date = date_obj.strftime("%Y-%m-%d")
        times = date_obj.strftime("%H:%M:%S")
        return date + " " + times
    else:
        if info != "":
            date_obj = datetime.datetime.strptime(info, "%Y. %m. %d. — ")
            date = date_obj.strftime("%Y-%m-%d")
            return date + " " + "00:00:00"
        else:
            return "no date information"


def get_content():
    date = 0
    headline = 0
    content = ""
    try:
        body = driver.find_element_by_class_name("rich-text-article-body")
        article = body.find_elements_by_xpath("./div/p | ./div/ul/li | ./div/div/div/div/p")
        title = driver.find_element_by_class_name("page-content.paywall")
        headline = title.find_element_by_class_name("headline").get_attribute("textContent").strip()
        for b in article:
            content += b.get_attribute("textContent").strip()
        if check_is_exist(driver, "class", "byline"):
            date = driver.find_element_by_class_name("byline").find_element_by_tag_name("time").get_attribute("datetime")
            date = process_datetime(0, date)
        return [headline, date, content]
    except NoSuchElementException or KeyboardInterrupt:
        return [headline, date, content]


def get_html(hrefs, dates):
    link = ""
    try:
        for link, auth_date in zip(hrefs, dates):
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(3)

            [title, date, content] = get_content()
            if title == 0:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            if date == 0:
                # to-do: get date info from google lists
                date = auth_date
            if date != 0 and content != "":
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
        print("에러 위치 : "+link)
        print("현재 데이터까지 저장완료")
        driver.close()
    return results

def check_is_exist(window, type, name):
    try:
        if (type == "class"):
            window.find_element_by_class_name(name)
        elif (type == "id"):
            window.find_element_by_id(name)
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
    for year in years:
        month = 1
        while month < 13:
            if month == 2 and year % 4 == 0 :
                day = 29
            elif month == 2:
                day = 28
            elif month in m30:
                day = 30
            elif month in m31:
                day = 31
            mindate = str(month)+"/1/"+str(year)
            maxdate = str(month)+"/"+str(day)+"/"+str(year)
            month += 1
            # url = "https://www.google.com/search?q=site:latimes.com+korea&tbs=cdr:1,cd_min:"+mindate+",cd_max:"+maxdate+"&sxsrf=ALeKk03Hf-An3StLLG2UrI734Sgb1u3Ryg:1627127389560&ei=Xf77YKvWIY_YhwOska3wDA&start=0&sa=N&filter=0&ved=2ahUKEwjr-Lvw0fvxAhUP7GEKHaxIC84Q8tMDegQIARBA&biw=1396&bih=694"
            url = "https://www.google.com/search?q=site:latimes.com+korea&hl=ko&tbs=cdr:1,cd_min:"+mindate+",cd_max:"+maxdate+"&sxsrf=ALeKk02YYZF7z-FlZayh-pjIOHwKGUffBw:1627147371767&filter=0&biw=1536&bih=763"
            driver.get(url=url)
            hrefs, dates = get_href_date()
            if len(hrefs) < 10:
                time.sleep(40)
            # csv = get_html(hrefs, dates)
            get_html(hrefs, dates)
            while check_exist_button('pnnext'):
                hrefs, dates = get_href_date()
                get_html(hrefs, dates)
            # csv = get_html(hrefs, dates))
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="LA TIMES")
    writer.save()
    print("데이터 수집 완료")
    print("소요시간: "+str(time.time() - start)+"초")
    driver.close()
# "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd=site%3Ahuanqiu.com%20%E6%9C%9D%E9%B2%9C&ct=2097152&si=huanqiu.com&oq=site%3Ahuanqiu.com%20%E6%9C%9D%E9%B2%9C&rsv_pq=bf92af700009d7fe&rsv_t=0f91uZXQlpsDugWDd7vzdMeYRk%2FbKAI14VStZTYQKZidJ1nWcGiV32Wv20w&rqlang=cn&rsv_dl=tb&rsv_enter=1&gpc=stf%3D1262358000%2C1609426800%7Cstftype%3D2&tfflag=95&bs=site%3Ahuanqiu.com%20%E6%9C%9D%E9%B2%9C&rsv_jmp=fail"
# "https://www.baidu.com/s?wd=site%3Ahuanqiu.com%20%E6%9C%9D%E9%B2%9C&pn=10&oq=site%3Ahuanqiu.com%20%E6%9C%9D%E9%B2%9C&ct=2097152&ie=utf-8&si=huanqiu.com&rsv_pq=e2ae024d0009e590&rsv_t=9619UV2s2cfUtOqtq1wFbVIK%2B1nGllqVUaRTk22JNy7OFQOuGWm2bJTfaTQ&gpc=stf%3D1262358000%2C1609426800%7Cstftype%3D2&tfflag=95&bs=site%3Ahuanqiu.com%20%E6%9C%9D%E9%B2%9C&rsv_jmp=fail"
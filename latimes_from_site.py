from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys

import pandas as pd
import time
import datetime
# get error log
import logging

# results = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}
# caps = DesiredCapabilities().CHROME
# caps["pageLoadStrategy"] = "normal"
caps = DesiredCapabilities().CHROME
caps["unexpectedAlertBehaviour"] = "ACCEPT"
chrome_options = Options()
chrome_options.set_capability('unhandledPromptBehavior', 'accept')
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='./chromedriver')
driver.implicitly_wait(time_to_wait=5)
year = "2021"
def save(year, results) :
    xlxs_dir = "./LATimes("+str(year)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="LA TIMES")
    writer.save()

# get news url from google html script
def get_href_date():
    hrefs = []
    dates = []
    try:
        lists = driver.find_element_by_class_name("search-results-module-results-menu").find_elements_by_tag_name("li")
        for li in lists:
            article = li.find_element_by_class_name("promo-title")
            if check_is_exist(article, "tag_name", "a"):
                href = article.find_element_by_tag_name("a").get_attribute("href")
                hrefs.append(href)
                if check_is_exist(li, "class", "promo-timestamp"):
                    date = li.find_element_by_class_name("promo-timestamp").get_attribute("data-timestamp")
                    date = process_datetime(1, int(date))
                    dates.append(date)
                else:
                    dates.append("")
        return hrefs, dates

    except KeyboardInterrupt or NoSuchElementException:
        print (href)
        print ("Error")
        driver.close()


def process_datetime(type, info):
    if type == 0:
        date = info[:10]
        time = info[11:19]
        return date + " " + time
    elif type == 1:
        date_obj = datetime.datetime.fromtimestamp(info/1000)
        date = date_obj.strftime("%Y-%m-%d")
        times = date_obj.strftime("%H:%M:%S")
        return date + " " + times
    elif type == 2:
        if info != "":
            date_obj = datetime.datetime.strptime(info, "%Y. %m. %d. — ")
            date = date_obj.strftime("%Y-%m-%d")
            return date + " " + "00:00:00"
        else:
            return "no date information"
    else:
        date_obj = datetime.datetime.strptime(info, "%b. %d, &Y")
        date = date_obj.strftime("%Y-%m-%d")
        return date + " " + "00:00:00"


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


def get_html(year, hrefs, dates, results):
    link = ""
    try:
        for link, auth_date in zip(hrefs, dates):
            if auth_date.startswith("2009"):
                break
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
                if 'korea' in content or 'Korea' in content or 'KOREA' in content:
                    results['country'].append('USA')
                    results['media'].append('LATimes')
                    results['date'].append(date)
                    results['headline'].append(title)
                    results['article'].append(content)
                    results['url'].append(link)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except KeyboardInterrupt or NoSuchElementException:
        save(year, results)
        print("에러 위치 : "+link)
        print("현재 데이터까지 저장완료")
        # driver.close()
    return results

def check_is_exist(window, type, name):
    try:
        if type == "class":
            window.find_element_by_class_name(name)
        elif type == "id":
            window.find_element_by_id(name)
        elif type == "tag_name":
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
    start = time.time()
    results = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}
    try:
        url = "https://www.latimes.com/search?q=korea&s=1&p=647"
        driver.get(url=url)
        breakSignal = False
        while True:
            nextBtn = driver.find_element_by_class_name("search-results-module-next-page")
            if check_is_exist(nextBtn, "tag_name", "a") is not True:
                break
            hrefs, dates = get_href_date()
            print(dates[0][:4])
            count_of_under_years = 0
            for date in dates:
                if int(date[:4]) < 2010:
                    count_of_under_years += 1
            if count_of_under_years >= 10:
                break
            if dates[0][:4] != year and int(dates[0][:4]) >= 2010:
                save(year, results)
                year = str(int(year) - 1)
                results = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}
            results = get_html(year, hrefs, dates, results)
            driver.get(url=nextBtn.find_element_by_tag_name("a").get_attribute("href"))
        save(year, results)
    except KeyboardInterrupt:
        save(year, results)
        print("keyboard Interrupt")
    else:
        save(year, results)
    finally:
        print("소요시간: "+str(time.time() - start)+"초")
        driver.close()
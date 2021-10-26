from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import pandas as pd
import sys
import time
from datetime import datetime


login_url = 'https://digital.asahi.com/login/?iref=pc_gnavi&jumpUrl=https%3A%2F%2Fwww.asahi.com%2F'
search_url = 'https://sitesearch.asahi.com/sitesearch/?Keywords=%E9%9F%93%E5%9B%BD&Searchsubmit2=search&Searchsubmit=%E6%A4%9C%E7%B4%A2&iref=pc_ss_date_btn14&sort=&start=2570'
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

init_results = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}

date_word = ["年", "月", "日", "時", "分"]
# column_list = ["country", "media", "date", "headline", "article", "url"]
# df = pd.DataFrame(columns=column_list)

def data_save(status, results):
    xlxs_dir = "./Asahi("+str(status)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="Asahi")
    # results = init_results
    writer.save()

def get_href_date():
    hrefs = []
    dates = []
    try:
        parts = driver.find_element_by_id('SiteSearchResult')
        ul = parts.find_elements_by_tag_name('li')
        for elem in ul:
            article = elem.find_element_by_tag_name('a')
            href = article.get_attribute('href')
            headline = article.find_element_by_class_name('SearchResult_Headline')
            head = headline.find_element_by_tag_name('em').get_attribute('textContent')
            date = ""
            if check_is_exist(headline, "class", 'Date'):
                dates = headline.find_element_by_class_name("Date").get_attribute("textContent")
                print(dates)
            hrefs.append(href)
            if date.count(".") != 3 or date.count(" ") != 4:
                date = ""
            dates.append(process_datetime(1, date))
        return hrefs, dates
    except:
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
        # print(info)
        date = info[0]+'-'+info[1]+'-'+info[2]
        # time = info[3]+':'+info[4]+':00'
        time = "00:00:00"
        dt = datetime.strptime(date+' '+time, '%Y-%m-%d %H:%M:%S')
        return dt


def get_html_content(auth_date, cur_url):
    if check_is_exist(driver, "id", "HeadLine") == False:
        return "Error"
    if check_is_exist(driver, "class", "BodyTxt") == False:
        return "Error"

    html_data = init_results

    # date
    if check_is_exist(driver, "class", "Utility"):
        date = driver.find_element_by_class_name("Utility").find_element_by_tag_name("p").text
        date = process_datetime(2, date)
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
    return html_data


def get_data(hrefs, dates, results):
    try:
        for link, auth_date in zip(hrefs, dates):
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(3)

            cur_url = driver.current_url

            html_data = get_html_content(auth_date, cur_url)
            if html_data != "Error":
                results = html_data
                # print(results)

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
                    continue

                results['country'].append('Japan')
                results['media'].append('Asahi')
                results['date'].append(date)
                results['headline'].append(title)
                results['article'].append(content)
                results['url'].append(cur_url)
                # print(results)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        # return results

    # except KeyboardInterrupt or NoSuchElementException:
    except:
        data_save(year, results)
        print("에러 위치 : " + cur_url)
        print("현재 데이터까지 저장완료")
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
    cnt = 0
    start = time.time()
    results = init_results
    try:
        driver.get(url=search_url)
        time.sleep(3)
        hrefs, dates = get_href_date()
        get_data(hrefs, dates, results)
        while check_exist_button('pnnext'):
            hrefs, dates = get_href_date()
            get_data(hrefs, dates, results)
            data_save(year, results)
            print(str(year) + "년 데이터 수집 완료")
    # except KeyboardInterrupt:
    except KeyboardInterrupt:
        data_save(year, results)
        print("Error")
    except:
        data_save(year, results)
    finally:
        print("최종소요시간: " + str(time.time() - start) + "초")
        driver.close()


# url = 'https://www.google.com/search?q=site:www.asahi.com+%E9%9F%93%E5%9B%BD&tbs=cdr:1,cd_min:01/01/2010,cd_max:12/31/2010&filter=0&biw=1792&bih=1008'
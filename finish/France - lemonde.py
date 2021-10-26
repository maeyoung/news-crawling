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

login_url = 'https://secure.lemonde.fr/sfuser/connexion?_ga=2.222672979.913906484.1633582789-1386295463.1628866481'

# caps = DesiredCapabilities().CHROME
# caps["pageLoadStrategy"] = "normal"
# driver = webdriver.Chrome(desired_capabilities=caps, executable_path='./chromedriver')
driver = webdriver.Chrome(executable_path='./chromedriver')
# driver.implicitly_wait(time_to_wait=5)

# login part
driver.get(url=login_url)
driver.find_element_by_name("email").send_keys("cyjeon8@gmail.com")
driver.find_element_by_name("password").send_keys("cyjeon88!!")
driver.find_element_by_class_name("button").send_keys(Keys.ENTER)
print("로그인 성공")



monthsInfo = {'janvier':1, 'février':2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12}

def save(year, results):
    xlxs_dir = "./LeMonde("+str(year)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="LeMonde")
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
    elif type == 3:
        date = info.split()
        day = date[2]
        mon = str(monthsInfo[date[3]]).zfill(2)
        yea = date[4]
        hourAndminute = date[6]
        hour = hourAndminute.split('h')[0]
        mins = hourAndminute.split('h')[1]
        #Publié le 23 juin 2010 à 12h21 - Mis à jour le 23 juin 2010 à 12h21
        return yea+"-"+mon+"-"+day+" "+hour+":"+mins
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
            EC.presence_of_element_located((By.CLASS_NAME, "article__content.old__article-content-single"))
        )
        article = body.find_elements_by_class_name("article__paragraph ")
        for b in article:
            content += b.get_attribute("textContent") + " "
        if check_is_exist(driver, 'class', 'meta__date.meta__date--header'):
            article_info = driver.find_element_by_class_name('meta__date.meta__date--header')
            dt = article_info.get_attribute('textContent')
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
            lists = driver.find_element_by_class_name("js-river-search").find_elements_by_class_name("teaser.teaser--inline-picture ")
            for li in lists:
                article = li.find_element_by_tag_name("a")
                title = article.find_element_by_class_name("teaser__title").get_attribute('textContent')
                href = article.get_attribute("href")
                [date, content] = get_content(href)
                # if date == 0:
                #     if check_is_exist(article, 'class', 'writerdetail'):
                #         date = process_datetime(1, article.find_element_by_class_name("writerdetail").find_element_by_xpath("./span/a").get_attribute("textContent"))
                if date != 0 and content != "":
                    if 'Corée' in content or 'corée' in content:
                        results['country'].append('France')
                        results['media'].append('Le Monde')
                        results['date'].append(date)
                        results['headline'].append(title)
                        results['article'].append(content)
                        results['url'].append(href)
            if not check_is_exist(driver.find_element_by_class_name('river__pagination'), 'class', 'river__pagination.river__pagination--page-search.river__pagination--focus-search'):
                break
            curBtn = driver.find_element_by_class_name('river__pagination').find_element_by_class_name('river__pagination.river__pagination--page-search.river__pagination--focus-search')
            if check_is_exist(curBtn, 'xpath', 'following-sibling::a'):
                driver.get(curBtn.find_element_by_xpath("following-sibling::a").get_attribute("href"))
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
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    m31 = [1, 3, 5, 7, 8, 10, 12]
    m30 = [4, 6, 9, 11]
    start = time.time()
    csv = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}
    time.sleep(10)
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
                mindate = "1/"+str(month)+"/"+str(year)
                maxdate = str(day)+"/"+str(month)+"/"+str(year)
                month += 1
                url = "https://www.lemonde.fr/recherche/?search_keywords=cor%C3%A9e&start_at="+mindate+"&end_at="+maxdate+"&search_sort=relevance_desc"
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

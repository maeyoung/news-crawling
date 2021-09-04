import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import  NoSuchElementException

# url = 'https://www.google.com/search?q=site%3Ahttps%3A%2F%2Fwww.bild.de%2F+korea&biw=1792&bih=1008&source=lnt&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2010%2Ccd_max%3A12%2F31%2F2020&tbm='
driver = webdriver.Chrome(executable_path='./chromedriver')

# remove cookie banner
# driver.get('https://www.bild.de/suche.bild.html?query=korea')
driver.get("https://www.bild.de/suche.bild.html?query=korea")

# file save
def save(year, results) :
    xlxs_dir = "./Bild("+str(year)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="Bild")
    writer.save()


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
        next.click()
        time.sleep(3)
    except NoSuchElementException:
        return False
    return True


def get_href_date():
    hrefs = []
    dates = []
    try:
        if check_is_exist(driver, "class", "tF2Cxc"):
            parts = driver.find_elements_by_class_name('tF2Cxc')
            for elem in parts:
                head = elem.find_element_by_class_name('yuRUbf')
                body = elem.find_element_by_class_name('IsZvec')
                href = head.find_element_by_tag_name('a').get_attribute('href')
                hrefs.append(href)
                date = ""
                if check_is_exist(body, "class", 'MUxGbd.wuQ4Ob.WZ8Tjf'):
                    date = body.find_element_by_class_name('MUxGbd.wuQ4Ob.WZ8Tjf').get_attribute("textContent")
                if date.count(".") != 3 or date.count(" ") != 4:
                    date = ""
                dates.append(process_datetime(2, date))
            return hrefs, dates
        else:
            return 0, 0
    except KeyboardInterrupt or NoSuchElementException:
        print('Error')
        driver.close()


def process_datetime(type, info):
    if type == 0:
        date = info[:10]
        time = info[11:19]
        return date + " " + time
    elif type == 2:
        if info != "":
            date_obj = datetime.strptime(info, "%Y. %m. %d. — ")
            date = date_obj.strftime("%Y-%m-%d")
            return date + " " + "00:00:00"
        else:
            return "no date information"

def get_content():
    date = 0
    headline = 0
    content = ""
    try:
        # if check_is_exist(driver, "class", "authors__pubdate") == False or check_is_exist(driver, "class", "txt") == False:
        #     driver.close()
        #     driver.switch_to.window(driver.window_handles[0])
        date = driver.find_element_by_class_name("authors__pubdate").get_attribute("datetime")
        date = process_datetime(0, date)
        headline = driver.find_element_by_class_name("headline").text
        body = driver.find_element_by_class_name("txt")
        article = body.find_elements_by_tag_name("p")
        for t in article:
            if t != "":
                content += t.get_attribute("textContent").strip() + " "
            #todo
            # 중간에 <br> 있는 경우 '\n'으로 처리
        return [headline, date, content]
    except NoSuchElementException or KeyboardInterrupt:
        return [headline, date, content]


def get_data(year, hrefs, dates, results):
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
                date = auth_date
            if date != 0 and content != "":
                if 'korea' in content or 'Korea' in content or 'KOREA' in content:
                    results['country'].append('Germany')
                    results['media'].append('Bild')
                    results['date'].append(date)
                    results['headline'].append(title)
                    results['article'].append(content)
                    results['url'].append(link)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    except KeyboardInterrupt or NoSuchElementException:
        save(year, results)
        print("에러 위치 :"+link)
        print("현재 데이터까지 저장 완료")
    return results



if __name__ == '__main__':
    year = 2013
    m31 = [1, 3, 5, 7, 8, 10, 12]
    m30 = [4, 6, 9, 11]
    start = time.time()
    results = {'country':list(), 'media': list(), 'date': list(), 'headline': list(), 'article':list(), 'url': list()}
    try:
        while year < 2021:
            results = {'country':list(), 'media': list(), 'date': list(), 'headline': list(), 'article':list(), 'url': list()}
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
                url = "https://www.google.com/search?q=site:www.bild.de+korea&hl=ko&tbs=cdr:1,cd_min:"+mindate+",cd_max:"+maxdate+"&sxsrf=ALeKk02YYZF7z-FlZayh-pjIOHwKGUffBw:1627147371767&filter=0&biw=1536&bih=763"
                driver.get(url=url)
                hrefs, dates = get_href_date()
                if hrefs == 0:
                    continue
                if len(hrefs) < 9:
                    time.sleep(40)
                results = get_data(year, hrefs, dates, results)
                while check_exist_button('pnnext'):
                    hrefs, dates = get_href_date()
                    results = get_data(year, hrefs, dates, results)
            save(year, results)
            print(str(year)+"년 데이터 수집 완료")
            year+=1
    except KeyboardInterrupt:
        save(year, results)
        print("keyboard Interrupt")
    else:
        save(year, results)
    finally:
        print("소요시간: "+str(time.time() - start) + "초")
        driver.close()
    #get_data(hrefs)

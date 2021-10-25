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
# driver.get("https://www.bild.de/suche.bild.html?query=korea")

dayinfo = {"January": '1', "February": '2', "March": '3', "April": '4', "May": '5', "June": '6', "July": '7', "August": '8', "September": '9', "October": '10', "November": '11', "December": '12'}

# file save
def save(year, results) :
    xlxs_dir = "./theJakartaPost("+str(year)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="theJakartaPost")
    writer.save()


def check_is_exist(window, type, name):
    try:
        if (type == "class"):
            window.find_element_by_class_name(name)
        elif (type == "id"):
            window.find_element_by_id(name)
        elif (type == "xpath"):
            window.find_element_by_xpath(name)
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
    else:
        if info != "":
            date_list = info.split(', ')
            month = date_list[1].split()[0].strip()
            day = date_list[1].split()[1].strip()
            year = date_list[2].strip()
            return year + "-" + str(dayinfo[month].zfill(2)) + "-" + str(day.zfill(2)) + " 00:00:00"

def get_content():
    date = 0
    headline = 0
    content = ""
    try:
        postinfo = driver.find_element_by_class_name("post-like")
        if check_is_exist(postinfo, 'class', 'special.btn-subscriber'):
            return [headline, date, content]
        date = driver.find_element_by_class_name("posting").find_element_by_class_name('day').get_attribute("textContent")
        date = process_datetime(3, date)
        headline = driver.find_element_by_class_name("title-large").get_attribute("textContent").strip()
        body = driver.find_element_by_class_name("show-define-area")
        while check_is_exist(body, 'xpath', 'following-sibling::p') or check_is_exist(body, 'xpath', 'following-sibling::div'):
            if check_is_exist(body, 'xpath', 'following-sibling::p'):
                content += body.find_element_by_xpath("following-sibling::p").get_attribute('textContent').strip() + " "
                body = body.find_element_by_xpath("following-sibling::p")
            else:
                body = body.find_element_by_xpath("following-sibling::div")
        # print(date + " " +headline)
        # print(content)
        return [headline, date, content]
    except NoSuchElementException:
        return [headline, date, content]
    except KeyboardInterrupt:
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
            # print(title+ " "+date)
            # print(content)
            if title == 0:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            if date == 0:
                date = auth_date
            if date != 0 and content != "":
                if 'korea' in content or 'Korea' in content or 'KOREA' in content:
                    results['country'].append('Indonesia')
                    results['media'].append('JakartaPost')
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
    year = 2010
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
                url = "https://www.google.com/search?q=site:www.thejakartapost.com+korea&hl=ko&tbs=cdr:1,cd_min:"+mindate+",cd_max:"+maxdate+"&sxsrf=ALeKk02YYZF7z-FlZayh-pjIOHwKGUffBw:1627147371767&filter=0&biw=1536&bih=763"
                driver.get(url=url)
                hrefs, dates = get_href_date()
                if hrefs == 0:
                    time.sleep(40)
                elif len(hrefs) < 9:
                    time.sleep(20)
                if hrefs != 0:
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

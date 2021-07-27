import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchAttributeException, NoSuchElementException

months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr':4, 'May': 5, 'Jun': 6, 'Jul': '7', 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
column_list = ["country", "media", "date", "headline", "article", "url"]

df = pd.DataFrame(columns=column_list)

# site:https://www.aljazeera.com/ 2010..2020 korea
# url = 'https://www.google.com/search?q=site%3Ahttps%3A%2F%2Fwww.aljazeera.com%2F+2010..2020+korea&oq=site%3Ahttps%3A%2F%2Fwww.aljazeera.com%2F+2010..2020+korea&aqs=chrome.0.69i59j69i58.785j0j7&sourceid=chrome&ie=UTF-8'
driver = webdriver.Chrome(executable_path='./chromedriver')

# remove cookie banner
driver.get('https://www.aljazeera.com/search/korea')

def get_href_date():
    hrefs = []
    dates = []
    try:
        parts = driver.find_elements_by_class_name('tF2Cxc')
        for elem in parts:
            head = elem.find_element_by_class_name('yuRUbf')
            body = elem.find_element_by_class_name('IsZvec')
            href = head.find_element_by_tag_name('a').get_attribute('href')
            title = head.find_element_by_class_name("LC20lb.DKV0Md").text
            if "| Today's latest from Al Jazeera" in title:
                continue
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
        date_obj = datetime.fromtimestamp(info/100)
        date = date_obj.strftime("%Y-%m-%d")
        times = date_obj.strftime("%H:%M:%S")
        return date + " " + times
    else:
        if info != "":
            date_obj = datetime.strptime(info, "%Y. %m. %d. — ")
            date = date_obj.strftime("%Y-%m-%d")
            return date + " " + "00:00:00"
        else:
            return "no date information"


# def get_href(hrefs):
#     try:
#         html = driver.find_elements_by_class_name('yuRUbf')
#         for elem in html:
#             head = elem.find_element_by_class_name("LC20lb.DKV0Md").text
#             if "| Today's latest from Al Jazeera" in head:
#                 continue
#             href = elem.find_element_by_tag_name('a').get_attribute('href')
#             hrefs.append(href)
#         return (hrefs)

#     except KeyboardInterrupt or NoSuchElementException:
#         print('Error')
#         driver.close()

def get_data(hrefs):

    try:
        for link in hrefs:

            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(3)

            data = ['Israel', 'ALJAZEERA']
            
            if check_is_exist(driver, "class", "date-simple.css-1mfvvdi-DateSimple") == False:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            n_date = driver.find_element_by_class_name("date-simple.css-1mfvvdi-DateSimple").text
            n_date = n_date.split(' ')
            n_date[1] = months[n_date[1]]
            n_date = list(map(int, n_date))
            d = datetime(n_date[2],n_date[1],n_date[0])
            news_date = str(d.strftime("%Y-%m-%d 00:00:00"))
            data.append(news_date)

            news_title = driver.find_element_by_tag_name("h1")
            data.append(news_title.text)

            if check_is_exist(driver, "class", "wysiwyg.wysiwyg--all-content.css-1vsenwb") == False:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            body = driver.find_element_by_class_name("wysiwyg.wysiwyg--all-content.css-1vsenwb")
            article = body.find_elements_by_tag_name("p") 
            content = ""
            for t in article:
                if t != "":
                    content += t.get_attribute("textContent").strip()
            if 'korea' in content:
                data.append(content)
                data.append(driver.current_url)
                df.loc[len(df)] = data

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except KeyboardInterrupt or NoSuchElementException:
        xlxs_dir = "./aljazeera.xlsx"
        writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
        df.to_excel(writer, sheet_name="Al Jazeera")
        writer.save()
        print("현재 데이터까지 저장완료")
        driver.close()


def check_is_exist(element, type, name):
    try:
        if (type == "class"):
            element.find_element_by_class_name(name)
        elif (type == "id"):
            element.find_element_by_id(name)
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



if __name__ == '__main__':
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    m31 = [1, 3, 5, 7, 8, 10, 12]
    m30 = [4, 6, 9, 11]
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
                mindate = str(month)+"/1/"+str(year)
                maxdate = str(month)+"/"+str(day)+"/"+str(year)
                month += 1
                url = "https://www.google.com/search?q=site:aljazeera.com+korea&hl=ko&tbs=cdr:1,cd_min:"+mindate+",cd_max:"+maxdate+"&sxsrf=ALeKk02YYZF7z-FlZayh-pjIOHwKGUffBw:1627147371767&filter=0&biw=1536&bih=763"
                driver.get(url=url)
                hrefs, dates = get_href_date()
                if len(hrefs) < 9:
                    time.sleep(20)
                get_data(hrefs)
                while check_exist_button('pnnext'):
                    hrefs, dates = get_href_date()
                    get_data(hrefs)
    except:
        print("error")
    # hrefs = []
    # hrefs = get_href(hrefs)
    # get_data(hrefs)
    # while check_exist_button('pnnext'):
    #     hrefs = []
    #     hrefs = get_href(hrefs)
    #     get_data(hrefs)
    finally:
        xlxs_dir = "./aljazeera.xlsx"
        writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
        df.to_excel(writer, sheet_name="Al Jazeera")
        writer.save()
        print("데이터 수집 완료")
        print("소요시간: "+str(time.time() - start)+"초")
        driver.close()
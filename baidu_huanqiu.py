from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from datetime import datetime

url = "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=site%3Ahuanqiu.com%2F%20%2B%E9%9F%A9%E5%9B%BD&fenlei=256&oq=site%253Ahuanqiu.com%252F%2520%252B%25E9%259F%25A9%25E5%259B%25BD&rsv_pq=a72ae8b300008076&rsv_t=7ad1BpvE6L3vgxVx89WMKngBTDoJ0NAXJWCWa3AK%2B8j29D5QTlxkfpqD568&rqlang=cn&rsv_enter=1&rsv_dl=tb&rsv_sug3=1&rsv_sug2=0&rsv_btype=t&inputT=8&rsv_sug4=325"

driver = webdriver.Chrome(executable_path='./chromedriver')
driver.get(url=url)

init_results = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}

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
        print('error')
        driver.close()


def process_datetime(type, info):
    if type == 0:
        # date = info[:10]
        # time = info[11:19]
        # return date + " " + time
        return info + ":00"
    elif type == 1:
        if info != "":
            date_obj = datetime.strptime(info, "%Y年%m月%d日 ")
            date = date_obj.strftime("%Y-%m-%d")
            return date + " " + "00:00:00"
        else:
            return "no date information"
    # elif type == 2:
    #     for word in date_word:
    #         info = info.replace(word, ' ')
    #     info = info.split()
    #     print(info)
    #     date = info[0]+'-'+info[1]+'-'+info[2]
    #     # time = info[3]+':'+info[4]+':00'
    #     time = "00:00:00"
    #     dt = datetime.strptime(date+' '+time, '%Y-%m-%d %H:%M:%S')
    #     return dt


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
        next.send_keys(Keys.ENTER)
        time.sleep(3)
    except NoSuchElementException:
        return False
    return True

def get_data(hrefs, dates, results):
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

            print(results)

            # date
            if check_is_exist(driver, "class", "time"):
                date = driver.find_element_by_class_name("time").get_attribute("textContent")
                date = process_datetime(0, date)
            else:
                date = auth_date
            print(results)
            # headline
            title = driver.find_element_by_class_name("t-container-title")
            if check_is_exist(title, "tag", "h3") == False:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            title = title.find_element_by_tag_name("h3").text
            print(results)
            # article 
            body = driver.find_element_by_class_name("l-con.clear")
            article = body.find_elements_by_tag_name("p")
            content = ""
            for t in article:
                if t != "":
                    content += t.get_attribute("textContent").strip()
            if "韩国" not in content:
                continue

            print(results)
            results['country'].append('China')
            results['media'].append('Huanqiu')
            results['date'].append(date)
            results['headline'].append(title)
            results['article'].append(content)
            results['url'].append(cur_url)
            print(results)


            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except:
        data_save("error", results)
        print("에러 위치 : " + cur_url)
        print("현재 데이터까지 저장완료")
        # return results


if __name__ == '__main__':
    try:
        start = time.time()
        results = init_results
        hrefs, dates = get_href_date()
        # print(hrefs)
        # print(dates)
        get_data(hrefs, dates, results)
        while check_exist_button('n'):
            hrefs, dates = get_href_date()
            # print(hrefs)
            # print(dates)
            get_data(hrefs, dates, results)
        data_save("correct", results)
        # driver.close()

    except:
        data_save("error", results)
        print("Error")

    finally:
        print("최종소요시간: " + str(time.time() - start) + "초")
        driver.close()
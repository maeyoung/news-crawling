from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import pandas as pd
import sys
import time


login_url = 'https://digital.asahi.com/login/?iref=pc_gnavi&jumpUrl=https%3A%2F%2Fwww.asahi.com%2F'
search_url = 'https://sitesearch.asahi.com/sitesearch/?Keywords=%E9%9F%93%E5%9B%BD&Searchsubmit2=%E6%A4%9C%E7%B4%A2&Searchsubmit=%E6%A4%9C%E7%B4%A2&iref=pc_gnavi'
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

driver.get(url=search_url)
time.sleep(3)

xlxs_dir = "./Asahi.xlsx"
writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')

column_list = ["country", "media", "date", "headline", "article", "url"]
df = pd.DataFrame(columns=column_list)

# class_names = ['digital', 'shimbun', 'book', 'EduA', 'webronza']
class_names = ['digital', 'shimbun', 'webronza']
# class_names = ['webronza']
# def get_class_names():
# news_list = driver.find_element_by_class_name("ListBlock")
# lists = news_list.find_elements_by_tag_name("li")
# for li in lists:
#     list = li.get_attribute("class")
#     if list not in class_names:
#         class_names.append(list)
#     else:
#         continue

def get_href():
    hrefs = []
    category = []
    try:
        news_list = driver.find_element_by_class_name("ListBlock")
        lists = news_list.find_elements_by_tag_name("li")
        # href_list = news_list.find_elements_by_tag_name("a")
        for li in lists:
            news_category = li.get_attribute("class")
            if news_category not in class_names:
                continue

            if news_category == "webronza":
                category.append("1")
            else:
                category.append("0")

            href = li.find_element_by_tag_name("a").get_attribute("href")
            hrefs.append(href)
            # print(hrefs)
            # print(category)
        return (hrefs, category)
    except KeyboardInterrupt or NoSuchElementException:
        print('Error')
        driver.close()

def process_datetime(info):
    date = info[:10]
    time = info[11:19]
    return date + " " + time

def get_data(hrefs, category):
    try:
        for link, class_name in zip(hrefs, category):
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(3)

            data = ['Japan', 'Asahi']

            if class_name == "0":
            
                # date
                date = driver.find_element_by_class_name("_3F5gI").find_element_by_tag_name("time").get_attribute("datetime")
                date = process_datetime(date)
                data.append(date)

                # headline
                title = driver.find_element_by_class_name("_2CsPo").find_element_by_tag_name("h1").text
                data.append(title)

                # article 
                body = driver.find_element_by_class_name("_3YqJ1")
                article = body.find_elements_by_tag_name("p")
                content = ""
                for t in article:
                    if t != "":
                        content += t.get_attribute("textContent").strip()
                data.append(content)
                  
                # url
                cur_url = driver.current_url
                data.append(cur_url)

                df.loc[len(df)] = data

            # else:
            #     # date
            #     title = ""


            driver.close()
            driver.switch_to.window(driver.window_handles[0])


    except KeyboardInterrupt or NoSuchElementException:
        df.to_excel(writer, sheet_name="Asahi")
        writer.save()
        print("에러 위치 : " + cur_url)
        print("현재 데이터까지 저장완료")
        driver.close()


def check_is_exist(window, type, name):
    try:
        if (type == "class"):
            window.find_element_by_class_name(name)
        elif (type == "id"):
            window.find_element_by_id(name)
    except NoSuchElementException:
        return False
    return True


def check_exist_button():
    try:
        curBtns = driver.find_elements_by_class_name("page-link")
        nextBtn = curBtns[-1]
        nextBtn.click()
        time.sleep(3)
    except NoSuchElementException:
        return False
    return True


if __name__ == '__main__':
    start = time.time()
    try:
        hrefs, category = get_href()
        get_data(hrefs, category)
        while check_exist_button():
            hrefs, category = get_href()
            get_data(hrefs, category)
    # except:
    #     print("Error")
    except:
        df.to_excel(writer, sheet_name="Asahi")
        writer.save()
        print("데이터 수집 완료")
        print("소요시간: " + str(time.time() - start) + "초")
        driver.close()


# function to find class names

# class_names = ['digital', 'shimbun', 'book', 'EduA', 'webronza']

# def get_class_names():
# news_list = driver.find_element_by_class_name("ListBlock")
# lists = news_list.find_elements_by_tag_name("li")
# for li in lists:
#     list = li.get_attribute("class")
#     if list not in class_names:
#         class_names.append(list)
#     else:
#         continue

# if __name__ == '__main__':
#     try:
#         get_class_names()
#         while check_exist_button():
#             get_class_names()
#         driver.close()
#     except KeyboardInterrupt:
#         print(class_names)
import time
import pandas as pd
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchAttributeException, NoSuchElementException

month = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr':4, 'May': 5, 'Jun': 6, 'Jul': '7', 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
column_list = ["country", "media", "date", "headline", "article", "url"]

df = pd.DataFrame(columns=column_list)

url = 'https://www.google.com/search?q=site:https://www.aljazeera.com/+2010..2020+korea&ei=VDHsYMbuNYWkmAXk8Z7oAw&start=20&sa=N&ved=2ahUKEwjG6PWdwN3xAhUFEqYKHeS4Bz04ChDw0wN6BAgBEEw&biw=1200&bih=848'
driver = webdriver.Chrome(executable_path='./chromedriver')

# remove cookie banner
driver.get('https://www.aljazeera.com/search/korea')
driver.get(url)

def get_href(hrefs):
    try:
        html = driver.find_elements_by_class_name('yuRUbf')
        for elem in html:
            head = elem.find_element_by_class_name("LC20lb.DKV0Md").text
            if "| Today's latest from Al Jazeera" in head:
                continue
            href = elem.find_element_by_tag_name('a').get_attribute('href')
            hrefs.append(href)
        print(hrefs)
        return (hrefs)

    except KeyboardInterrupt or NoSuchElementException:
        print('Error')
        driver.close()

def get_data(hrefs):

    try:
        for link in hrefs:

            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url=link)
            time.sleep(3)

            data = ['Israel', 'ALJAZEERA']
            
            if check_is_exist("class", "date-simple.css-1mfvvdi-DateSimple") == False:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            n_date = driver.find_element_by_class_name("date-simple.css-1mfvvdi-DateSimple").text
            n_date = n_date.split(' ')
            n_date[1] = month[n_date[1]]
            n_date = list(map(int, n_date))
            d = date(n_date[2],n_date[1],n_date[0])
            news_date = str(d.strftime("%Y-%m-%d 00:00:00"))
            data.append(news_date)

            news_title = driver.find_element_by_tag_name("h1")
            data.append(news_title.text)

            if check_is_exist("class", "wysiwyg.wysiwyg--all-content.css-1vsenwb") == False:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            body = driver.find_element_by_class_name("wysiwyg.wysiwyg--all-content.css-1vsenwb")
            article = body.find_elements_by_tag_name("p") 
            content = ""
            for t in article:
                content += t.get_attribute("textContent").strip()

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


def check_is_exist(type, name):
    try:
        if (type == "class"):
            driver.find_element_by_class_name(name)
        elif (type == "id"):
            driver.find_element_by_id(name)
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
    hrefs = []
    hrefs = get_href(hrefs)
    get_data(hrefs)
    while check_exist_button('pnnext'):
        hrefs = []
        hrefs = get_href(hrefs)
        get_data(hrefs)
    xlxs_dir = "./aljazeera.xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    df.to_excel(writer, sheet_name="Al Jazeera")
    writer.save()
    print("데이터 수집 완료")
    driver.close()
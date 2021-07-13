#-*-coding:utf-8-*-
# import os
# import pandas as pd
import csv
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

month = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr':4, 'May': 5, 'Jun': 6, 'Jul': '7', 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

def aljazeera_crawl():
    
    url = 'https://www.aljazeera.com/search/korea'
    # url = 'https://www.aljazeera.com/search/korea?page=2'
    column_list = ["country", "media", "date", "headline", "article", "url"]

    with open('aljazeera.csv', 'w', -1, newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(column_list)

        driver = webdriver.Chrome('/Users/maeyoung/Downloads/chromedriver')
        driver.get(url)

        i = 1
        while (1):
            driver.get(url)
            time.sleep(1)

            if i == 11:
                button = driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div/div/div[3]/div[12]/a')
                if button.is_enabled():
                    button.click()
                    time.sleep(1)
                    i = 1
                    url = driver.current_url
                else: 
                    print("데이터 수집 완료")
                    break

            data = ['Israel', 'ALJAZEERA']
            path = f'//*[@id="root"]/div/div[2]/div/div/div/div[2]/article[{i}]/div[2]/div[1]/h3/a'
            
            if driver.find_element_by_xpath(path).text != '':
                span_path = path + '/span'
                header = driver.find_element_by_xpath(span_path).text
                if "| Today's latest from Al Jazeera" in header:
                    i += 1
                    continue
                else:
                    driver.find_element_by_xpath(path).send_keys(Keys.ENTER)
                    time.sleep(1)
                    
                    n_date = driver.find_element_by_class_name("date-simple.css-1mfvvdi-DateSimple").text
                    n_date = n_date.split(' ')
                    n_date[1] = month[n_date[1]]
                    n_date = list(map(int, n_date))
                    d = date(n_date[2],n_date[1],n_date[0])
                    news_date = str(d.strftime("%Y-%m-%d 00:00:00"))
                    print(type(news_date))
                    data.append(news_date)

                    news_title = driver.find_element_by_tag_name("h1")
                    data.append(news_title.text)

                    div_elem = driver.find_element_by_class_name("wysiwyg.wysiwyg--all-content.css-1vsenwb")
                    main_text = div_elem.find_elements_by_tag_name("p") # element에 's'를 붙여야 list로 나옴 
                    text = main_text[0].text
                    for j in range(len(main_text)):
                        t = main_text[j].text
                        if t != "" :
                            text = text + ' ' + t

                    data.append(text)
                    data.append(driver.current_url)
                    w.writerow(data)
                    i += 1

    driver.close()

def main():
    aljazeera_crawl()

if __name__ == '__main__':
    main()

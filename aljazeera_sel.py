#-*-coding:utf-8-*-
import time
import pandas as pd
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

month = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr':4, 'May': 5, 'Jun': 6, 'Jul': '7', 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
column_list = ["country", "media", "date", "headline", "article", "url"]

df = pd.DataFrame(columns=column_list)

url = 'https://www.aljazeera.com/search/korea'
driver = webdriver.Chrome(executable_path='./chromedriver')

driver.get(url)
driver.get(url)

def aljazeera_crawl():
    
    try:

        i = 1
        while (1):
            
            if i == 11:
                button = driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div/div/div[3]/div[12]/a')
                if button.get_attribute("disabled") is None:
                    button.click()
                    time.sleep(3)
                    i = 1
                else:
                    xlxs_dir = "./aljazeera.xlsx"
                    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
                    df.to_excel(writer, sheet_name="Al Jazeera")
                    writer.save()
                    print("데이터 수집 완료")
                    break

            data = ['Israel', 'ALJAZEERA']
            path = f'//*[@id="root"]/div/div[2]/div/div/div/div[2]/article[{i}]/div[2]/div[1]/h3/a'
            href = driver.find_element_by_xpath(path).get_attribute("href")

            if driver.find_element_by_xpath(path).text != '':
                span_path = path + '/span'
                header = driver.find_element_by_xpath(span_path).text
                if "| Today's latest from Al Jazeera" in header:
                    i += 1
                    continue
                else:
                    driver.execute_script("window.open();")
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.get(url=href)
                    time.sleep(3)

                    n_date = driver.find_element_by_class_name("date-simple.css-1mfvvdi-DateSimple").text
                    n_date = n_date.split(' ')
                    n_date[1] = month[n_date[1]]
                    n_date = list(map(int, n_date))
                    d = date(n_date[2],n_date[1],n_date[0])
                    news_date = str(d.strftime("%Y-%m-%d 00:00:00"))
                    data.append(news_date)

                    news_title = driver.find_element_by_tag_name("h1")
                    data.append(news_title.text)

                    body = driver.find_element_by_class_name("wysiwyg.wysiwyg--all-content.css-1vsenwb")
                    article = body.find_elements_by_tag_name("p") # element에 's'를 붙여야 list로 나옴 
                    content = ""
                    for t in article:
                        content += t.get_attribute("textContent").strip()

                    # //*[@id="root"]/div/div[3]/div/div[1]/div[1]/div[2]/text()[1]

                    data.append(content)
                    data.append(driver.current_url)
                    df.loc[len(df)] = data
                    i += 1
            
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
        driver.close()
        
    except KeyboardInterrupt or NoSuchElementException:
        # df.to_csv('./aljazeera.csv', encoding='utf-8-sig')
        print("현재 데이터까지 저장완료")
        xlxs_dir = "./aljazeera.xlsx"
        writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
        df.to_excel(writer, sheet_name="Al Jazeera")
        writer.save()
        driver.close()

def main():
    aljazeera_crawl()

if __name__ == '__main__':
    main()

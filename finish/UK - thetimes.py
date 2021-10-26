from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import pandas as pd
import time
from datetime import datetime


login_url = 'https://account.thetimes.co.uk/login?state=hKFo2SBaLWJXZnhKZE9RY3hJa0NxWDVWZzlHZGoyMWpMVW5wb6FupWxvZ2luo3RpZNkgc1ZmYklMZHdkREdlQlpxeHN2MHVZNFpNMkxOSXlpR1ajY2lk2SBEbXNVM0JCbXltb1VYT1JuWG9xcXJxaUJMTEtJNkl2Sg&client=DmsU3BBmymoUXORnXoqqrqiBLLKI6IvJ&protocol=oauth2&prompt=login&scope=openid%20profile%20email&response_type=code&redirect_uri=https%3A%2F%2Flogin.thetimes.co.uk%2Foidc%2Frp%2Fcallback&nustate=eyJyZXR1cm5fdXJsIjoiaHR0cHM6Ly93d3cudGhldGltZXMuY28udWsvIiwic2lnblVwTGluayI6Imh0dHBzOi8vam9pbi50aGV0aW1lcy5jby51ay8ifQ%3D%3D'

# caps = DesiredCapabilities().CHROME
# caps["pageLoadStrategy"] = "normal"
# driver = webdriver.Chrome(desired_capabilities=caps, executable_path='./chromedriver')
driver = webdriver.Chrome(executable_path='./chromedriver')
# driver.implicitly_wait(time_to_wait=5)

# login part
driver.get(url=login_url)
driver.find_element_by_name("email").send_keys("cyjeon8@gmail.com")
driver.find_element_by_name("password").send_keys("cyjeon88!!")
driver.find_element_by_name("submit").send_keys(Keys.ENTER)
driver.implicitly_wait(time_to_wait=30)

init_results = {'country': list(), 'media': list(), 'date': list(), 'headline': list(), 'article': list(), 'url': list()}

def save(status, results):
    xlxs_dir = "./TheTimes("+str(status)+").xlsx"
    writer = pd.ExcelWriter(xlxs_dir, engine='xlsxwriter')
    dict_to_df = pd.DataFrame.from_dict(results)
    dict_to_df.to_excel(writer, sheet_name="TheTimes")
    # results = init_results
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
    elif type == 1:
        date_obj = datetime.strptime(info, "%Y-%m-%dT%H:%M:%S.%fZ")
        date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        return date
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
        if check_is_exist(driver, 'class', 'responsiveweb__DatePublicationContainer-sc-1nipn43-0.duAfph.responsiveweb__DatePublicationContainer-sc-1nipn43-0.duAfph.css-901oao.r-1khp51w.r-j2s0nr.r-n6v787.r-fxxt2n.r-1g94qm0'):
            date = driver.find_element_by_class_name("responsiveweb__DatePublicationContainer-sc-1nipn43-0.duAfph.responsiveweb__DatePublicationContainer-sc-1nipn43-0.duAfph.css-901oao.r-1khp51w.r-j2s0nr.r-n6v787.r-fxxt2n.r-1g94qm0").find_element_by_tag_name("time").get_attribute("datetime")
            date = process_datetime(1, date)
        elif check_is_exist(driver, 'class', 'css-901oao.css-16my406.r-1khp51w.r-j2s0nr.r-n6v787.r-fxxt2n'):
            date = driver.find_element_by_class_name("css-901oao.css-16my406.r-1khp51w.r-j2s0nr.r-n6v787.r-fxxt2n").find_element_by_tag_name("time").get_attribute("datetime")
            date = process_datetime(1, date)
        if check_is_exist(driver, 'class', 'responsiveweb__HeadlineContainer-sc-1jw79sf-0.hGQexq.css-4rbku5.responsiveweb__HeadlineContainer-sc-1jw79sf-0.hGQexq.css-901oao.r-1yqk5fa.r-iirzy8.r-1ra0lkn.r-1j8sj39.r-11mo1y0'):
            headline = driver.find_element_by_class_name("responsiveweb__HeadlineContainer-sc-1jw79sf-0.hGQexq.css-4rbku5.responsiveweb__HeadlineContainer-sc-1jw79sf-0.hGQexq.css-901oao.r-1yqk5fa.r-iirzy8.r-1ra0lkn.r-1j8sj39.r-11mo1y0").text
        elif check_is_exist(driver, 'class', 'responsiveweb__HeadlineContainer-sc-1nipn43-3.fNhwNg.css-4rbku5.responsiveweb__HeadlineContainer-sc-1nipn43-3.fNhwNg.css-901oao.r-iirzy8.r-1ra0lkn.r-1j8sj39.r-15d164r.r-q4m81j'):
            headline = driver.find_element_by_class_name("responsiveweb__HeadlineContainer-sc-1nipn43-3.fNhwNg.css-4rbku5.responsiveweb__HeadlineContainer-sc-1nipn43-3.fNhwNg.css-901oao.r-iirzy8.r-1ra0lkn.r-1j8sj39.r-15d164r.r-q4m81j")
        body = driver.find_element_by_tag_name("article")
        if check_is_exist(body, 'class', 'responsiveweb__Paragraph-sc-1isfdlb-0.YieBL'):
            article = body.find_elements_by_class_name("responsiveweb__Paragraph-sc-1isfdlb-0.YieBL")
            for t in article:
                if t != "":
                    content += t.get_attribute("textContent").strip() + " "
            #todo
            # 중간에 <br> 있는 경우 '\n'으로 처리
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
            if title == 0:
                driver.close()
                driver.switch_to.window(driver.window_handles[1])
                continue
            if date == 0:
                date = auth_date
            if date != 0 and content != "":
                if 'korea' in content or 'Korea' in content or 'KOREA' in content:
                    results['country'].append('U.K')
                    results['media'].append('The Times')
                    results['date'].append(date)
                    results['headline'].append(title)
                    results['article'].append(content)
                    results['url'].append(link)
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
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
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[-1])
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
                url = "https://www.google.com/search?q=site:www.thetimes.co.uk+korea&hl=ko&tbs=cdr:1,cd_min:"+mindate+",cd_max:"+maxdate+"&sxsrf=ALeKk02YYZF7z-FlZayh-pjIOHwKGUffBw:1627147371767&filter=0&biw=1536&bih=763"
                driver.get(url=url)
                hrefs, dates = get_href_date()
                if hrefs == 0:
                    continue
                if len(hrefs) < 9:
                    time.sleep(20)
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
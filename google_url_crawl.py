import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchAttributeException, NoSuchElementException

# url = 'https://www.google.com/search?q=site%3Ahttps%3A%2F%2Fwww.bild.de%2F+2010..2020+korea&biw=1792&bih=1008&ei=7P3rYIGoPKS2mAW16KTwBg&oq=site%3Ahttps%3A%2F%2Fwww.bild.de%2F+2010..2020+korea&gs_lcp=Cgdnd3Mtd2l6EANKBAhBGAFQAFgAYJwkaAFwAHgAgAFuiAFukgEDMC4xmAEAqgEHZ3dzLXdpesABAQ&sclient=gws-wiz&ved=0ahUKEwiBzuWaj93xAhUkG6YKHTU0CW44eBDh1QMIDg&uact=5'
url = 'https://www.google.com/search?q=site:https://www.bild.de/+2010..2020+korea&ei=kBnsYMypKqGymAWPp6LoCA&start=270&sa=N&ved=2ahUKEwjMseDIqd3xAhUhGaYKHY-TCI04mAIQ8tMDegQIARBJ&biw=964&bih=1008&dpr=2'
driver = webdriver.Chrome(executable_path='./chromedriver')

driver.get(url)

def get_href(hrefs):
    try:
        html = driver.find_elements_by_class_name('yuRUbf')
        for elem in html:
            href = elem.find_element_by_tag_name('a').get_attribute('href')
            hrefs.append(href)
        return (hrefs)

    except KeyboardInterrupt or NoSuchElementException:
        print('error')
        driver.close()

def create_new_window(hrefs):
    
    for link in hrefs:
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url=link)
        time.sleep(3)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])


def check_exist_button():
    try:
        next = driver.find_element_by_id('pnnext')
        next.click()
        time.sleep(3)
    except NoSuchElementException:
        return False
    return True



if __name__ == '__main__':
    hrefs = []
    hrefs = get_href(hrefs)
    create_new_window(hrefs)
    while check_exist_button():
        hrefs = []
        hrefs = get_href(hrefs)
        create_new_window(hrefs)
    driver.close()

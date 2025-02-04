import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
url = "https://www.olx.co.id/tangerang-kab_g4000076/dijual-rumah-apartemen_c5158?filter=type_eq_rumah"
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get(url)

try:
    for i in range(500):
        time.sleep(5)
        try:
            driver.find_element(By.CSS_SELECTOR, "div._38O09 > button").click()
            time.sleep(5)
        except NoSuchElementException:
            break
    time.sleep(8)

    rumah = []
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for item in soup.find_all('li', class_='_1DNjI'):
        product_name = item.find('span', class_='_2poNJ')
        price = item.find('span', class_='_2Ks63')
        
        url_link = item.find('a', class_='_2cbZ2')
        if not url_link:
            url_link = item.find('a')
        
        product_name_text = product_name.text if product_name else "N/A"
        price_text = price.text if price else "N/A"
        url_link_text = f"https://www.olx.co.id{url_link['href']}" if url_link else "N/A"
        
        rumah.append((product_name_text, price_text, url_link_text))
    
    df = pd.DataFrame(rumah, columns=['Rumah', 'Harga', 'URL'])
    print(df)  # Print the DataFrame

    df.to_csv('OLX Selenium Test.csv', index=False)
    print("Data saved!")
finally:
    driver.close()
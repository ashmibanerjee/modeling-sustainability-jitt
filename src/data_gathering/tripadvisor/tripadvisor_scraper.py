import time
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def get_reviews(city: str):
    base_url = "https://www.tripadvisor.com/"

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    # driver.implicitly_wait(10)
    driver.get(base_url)

    time.sleep(5)
    # click on I accept cookies
    driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/div[1]/button").click()
    time.sleep(5)

    wait = WebDriverWait(driver, 30)
    # click on search bar
    search = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                    "//input[@class='hUpcN _G G_ B- z F1 _J w Cj R0 NBfGt H3' and "
                                                    "@placeholder='Places to go, things to do, hotels...']")))
    search.send_keys(city)
    search.send_keys(Keys.RETURN)
    time.sleep(10)
    review_count = driver.find_element(By.CLASS_NAME, "review-count").text

    # clicking on the first result
    driver.find_element(By.XPATH,
                        "/html/body/div[2]/div/div[2]/div/div/div/div/div[1]/div/div[1]/div/div[3]/div/div["
                        "1]/div/div[2]/div/div/div/div/div/div/div[1]").click()

    time.sleep(10)
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)
    time.sleep(5)
    # clicking on things to do
    wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Things to Do"))).click()
    # switching windows
    next_window = driver.window_handles[1]
    driver.switch_to.window(next_window)
    time.sleep(5)
    try:
        # finding attraction info table
        table = driver.find_element(By.CLASS_NAME, "kcEwm")
        table_html = table.get_attribute("innerHTML")
        table_data = parse_html(table_html)
    except NoSuchElementException:
        table_data = [np.nan, np.nan, np.nan, np.nan]

    driver.quit()

    table_data[:0] = [city, review_count]

    # create_dataframe(table_data).to_csv(f"../data/tripadvisor_data/{city}_popularity.csv", index=False,
    #                                     encoding='utf-8')
    return table_data


def parse_html(table_html) -> list:
    soup = BeautifulSoup(table_html, "html.parser")
    data = []
    rows = soup.find_all('tr')
    for row in rows:
        d = row.find("td")
        data.append(d.text)
    return data


def create_dataframe(table_data):
    column_names = ["city", "review_count", "number_of_attractions", "attraction_reviews", "attraction_photos",
                    "local_time"]
    df = pd.DataFrame([table_data], columns=column_names)
    return df

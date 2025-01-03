import time
import logging
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import numpy as np

SRC = "FRA"
DEST = "DEL"
MAX_TRIES = 5


def scraper(src, dest):
    logging.basicConfig(filename='../../../logs/scraper.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - '
                                                                             '%(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    tries = 0
    while (tries < MAX_TRIES):
        try:
            flights = get_flights(src, dest)
            return flights
        except Exception as e:
            tries += 1
            logging.error(f"Error while scraping flights for {src} to {dest} for try nr: {tries}: {e}")
            time.sleep(10)


def get_flights(src, dest):
    url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{src}%20"

    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(10)
    # click on TOC page
    driver.find_element(By.XPATH,
                        '/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[1]/div/div/button/span').click()  # clicks the reject all
    time.sleep(10)
    flights_data = []
    try:
        flights = driver.find_element(By.CLASS_NAME, "Rk10dc")
        time.sleep(7)
        flights_html = flights.get_attribute('innerHTML')
        driver.quit()
        flights_data = parse_html(src, dest, flights_html)
        print(f"flights found & parsed for {src} to {dest}")
        logging.info(flights_data)
    except NoSuchElementException:
        driver.quit()
        logging.warning(f'No flights found for {src} to {dest}')
        flights_data.append([src, dest, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
    return flights_data


def parse_html(src, dest, flights_html):
    soup = BeautifulSoup(flights_html, "html.parser")
    flights_data = []
    flight_elements = soup.find_all('li', class_='pIav2d')
    for flight in flight_elements:
        span_tag = flight.select_one('.sSHqwe.tPgKwe.ogfYpf span')
        # Extract the text from the <span> tag
        airline = span_tag.get_text(strip=True)

        # airline = flight.select('div.sSHqwe.tPgKwe.ogfYpf.tPgKwe')[0].text
        departure_time = flight.find('div', class_='wtdjmc').text
        departure_time = departure_time.replace("\u202f", " ")

        arrival_time = flight.find('div', class_='XWcVob').text
        arrival_time = arrival_time.replace("\u202f", " ")

        duration = flight.find('div', class_='gvkrdb').text

        number_of_stops = flight.find("div", "EfT7Ae AdWm1c tPgKwe").text
        stops_info = flight.select('div.BbR8Ec div.ogfYpf')[0].text

        co2_emission = flight.find("div", class_="O7CXue").text
        flights_data.append(
            [src, dest, airline, departure_time, arrival_time, duration, number_of_stops, stops_info, co2_emission])

    return flights_data


if __name__ == '__main__':
    scraper(SRC, DEST)

import time
import logging
from typing import Optional
from flights.flight_scraper import get_flights
from tripadvisor.tripadvisor_scraper import get_reviews

MAX_TRIES = 5


def scraper(src: str, dest: Optional[str] = None, category: str = "flights"):
    logging.basicConfig(filename=f'../logs/{category}_scraper.log', filemode='w', format='%(asctime)s %(name)s - %('
                                                                                         'levelname)s - ''%(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    tries = 0
    while tries < MAX_TRIES:
        try:
            data = scrape_data(src, dest, category)
            print("\t data scraped")
            return data
        except Exception as e:
            tries += 1
            logging.error(f"Error while scraping for {src} for try nr: {tries}: {e}")
            time.sleep(10)


def scrape_data(src: str, dest: Optional[str] = None, category: str = "reviews"):
    match category.lower():
        case "flights":
            return get_flights(src, dest)
        case "reviews":
            return get_reviews(src)
        case "trains":
            raise NotImplementedError
        case _:
            raise ValueError(f"Category {category} not supported")


if __name__ == '__main__':
    table_data = scraper(src="Frankfurt", category="reviews")


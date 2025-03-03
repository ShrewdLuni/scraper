import re
import math
import requests
from bs4 import BeautifulSoup
from functools import lru_cache


class CeneoScraper:
    def __init__(self, base_url="https://www.ceneo.pl/"):
        self.base_url = base_url
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    @lru_cache(maxsize=32)
    def __get_html(self, url):
        try:
            return requests.get(url, headers=self.headers, timeout=10).text
        except requests.exceptions.RequestException:
            return ""

    @staticmethod
    def __extract(obj, tag, cls=None, attr=None, default=None):
        if not obj: return default
        elem = obj.find(tag, class_=cls) if cls else obj.find(tag)
        if attr: return elem.get(attr) if elem else default
        return elem.text.strip().replace("\n", " ") if elem and elem.text else default

    @staticmethod
    def get_product_data(self, product_id):
        soup = BeautifulSoup(self.__get_html(f"{self.base_url}{product_id}#tab=reviews"), "html.parser")
        
        try:
            review_amount = int(re.search(r"\((\d+)\)", soup.find_all("span", class_="page-tab__title js_prevent-middle-button-click")[2].text).group(1))
        except (IndexError, AttributeError, ValueError):
            raise Exception("No reviews found")
            
        reviews = []
        for page in range(1, math.ceil(review_amount / 10) + 1):
            page_soup = BeautifulSoup(self.__get_html(f"{self.base_url}{product_id}/opinie-{page}"), "html.parser")
            for review in page_soup.find_all("div", class_="user-post__body"):
                features = review.find_all("div", class_="review-feature__col")
                pros = len(features[0].findChildren("div", recursive=False)) - 1 if features and len(features) > 0 else 0
                cons = len(features[1].findChildren("div", recursive=False)) - 1 if features and len(features) > 1 else 0
                review_data = {
                    "author": self.__extract(review, "span", "user-post__author-name"),
                    "comment_date": self.__extract(review, "time", attr="datetime"),
                    "purchase_date": self.__extract(review, "time", attr="datetime", default="Brak") if len(review.find_all("time")) > 1 else "Brak",
                    "opinion": self.__extract(review, "div", "user-post__text"),
                    "recommendation": self.__extract(review, "em", "recommended", default="Nie polecam"),
                    "score": self.__extract(review, "span", "user-post__score-count"),
                    "likes": self.__extract(review.find("button", class_="js_vote-yes"), "span") or "0",
                    "dislikes": self.__extract(review.find("button", class_="js_vote-no"), "span") or "0",
                    "pros": pros,
                    "cons": cons
                }
                if review_data["author"] and review_data["score"]:
                    reviews.append(review_data)
                
        return {
            "product": self.__extract(soup, "h1", "product-top__product-info__name", default="Product has no name"),
            "reviews": reviews
        }
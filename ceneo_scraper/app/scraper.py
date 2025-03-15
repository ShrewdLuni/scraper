import re
import math
import requests
from bs4 import BeautifulSoup
from functools import lru_cache


class CeneoScraper:
    BASE_URL = "https://www.ceneo.pl/"
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    @staticmethod
    @lru_cache(maxsize=32)
    def _get_html(url):
        try:
            return requests.get(url, headers=CeneoScraper.HEADERS, timeout=10).text
        except requests.exceptions.RequestException:
            return ""

    @staticmethod
    def _extract(obj, tag, cls=None, attr=None, default=None):
        if not obj: return default
        elem = obj.find(tag, class_=cls) if cls else obj.find(tag)
        if attr: return elem.get(attr) if elem else default
        return elem.text.strip().replace("\n", " ") if elem and elem.text else default
    
    @staticmethod
    def is_valid(product_id):
        try:
            soup = BeautifulSoup(CeneoScraper._get_html(f"{CeneoScraper.BASE_URL}{product_id}#tab=reviews"), "html.parser")
            review_amount = int(re.search(r"\((\d+)\)", soup.find_all("span", class_="page-tab__title js_prevent-middle-button-click")[2].text).group(1))
            return True
        except (IndexError, AttributeError, ValueError):
            return False

    @staticmethod
    def get_product_data(product_id, base_url=None):
        if base_url is None:
            base_url = CeneoScraper.BASE_URL
        soup = BeautifulSoup(CeneoScraper._get_html(f"{base_url}{product_id}#tab=reviews"), "html.parser")
        try:
            review_amount = int(re.search(r"\((\d+)\)", soup.find_all("span", class_="page-tab__title js_prevent-middle-button-click")[2].text).group(1))
        except (IndexError, AttributeError, ValueError):
            raise Exception("No reviews found")
        product_data = {
            "name": CeneoScraper._extract(soup, "h1", "product-top__product-info__name", default="Product has no name"),
            "opinions_count": 0,
            "disadvantages_count": 0,
            "advantages_count": 0,
            "recommendations_count": 0,
            "average_score": 0.0,
        }
        reviews = []
        for page in range(1, math.ceil(review_amount / 10) + 1):
            page_soup = BeautifulSoup(CeneoScraper._get_html(f"{base_url}{product_id}/opinie-{page}"), "html.parser")
            for review in page_soup.find_all("div", class_="user-post__body"):
                features = review.find_all("div", class_="review-feature__section")
                pros = [item.text for item in features[0].findChildren("div", recursive=False)][1:] if features and len(features) > 0 else ["None"]
                cons = [item.text for item in features[1].findChildren("div", recursive=False)][1:] if features and len(features) > 1 else ["None"]
                review_data = {
                    "author": CeneoScraper._extract(review, "span", "user-post__author-name"),
                    "publish_date": CeneoScraper._extract(review, "time", attr="datetime"),
                    "purchase_date": CeneoScraper._extract(review, "time", attr="datetime", default="Brak") if len(review.find_all("time")) > 1 else "Brak",
                    "content": CeneoScraper._extract(review, "div", "user-post__text"),
                    "recommendation": CeneoScraper._extract(review, "em", "recommended", default="Nie polecam"),
                    "score": CeneoScraper._extract(review, "span", "user-post__score-count"),
                    "helpful_count": CeneoScraper._extract(review.find("button", class_="js_vote-yes"), "span") or "0",
                    "unhelpful_count": CeneoScraper._extract(review.find("button", class_="js_vote-no"), "span") or "0",
                    "advantages": pros,
                    "disadvantages": cons
                }
                if review_data["author"] and review_data["score"]:
                    reviews.append(review_data)
                    product_data["opinions_count"] += 1
                    product_data["disadvantages_count"] += bool(review_data["disadvantages"][0] != "None")
                    product_data["advantages_count"] += bool(review_data["advantages"][0] != "None")
                    product_data["recommendations_count"] += 1 if review_data["recommendation"] == "Polecam" else 0
                    product_data["average_score"] += int(review_data["score"][0])
        product_data["average_score"] /= product_data["opinions_count"]
        return {
            "product": product_data,
            "reviews": reviews
        }
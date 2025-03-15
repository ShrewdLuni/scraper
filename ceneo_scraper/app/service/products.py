from bson import ObjectId
from ..db import products_collection, opinions_collection

def create_product(product_id, product_data):
    product = {
        "_id": product_id,
        "name": product_data.get("name"),
        "opinions_count": product_data.get("opinions_count"),
        "disadvantages_count": product_data.get("disadvantages_count"),
        "advantages_count": product_data.get("advantages_count"),
        "recommendations_count": product_data.get("recommendations_count"),
        "average_score": product_data.get("average_score"),
    }
    products_collection.insert_one(product)
    return product_id

def get_product_with_opinions_by_id(product_id):
    product = products_collection.find_one({"_id": product_id})
    if product:
        opinions = list(opinions_collection.find({"product_id": product_id}))
        product["opinions"] = opinions
        return product
    return None

def get_products_with_opinions():
    products = list(products_collection.find({}))
    for product in products:
        product_id = product["_id"]
        opinions = list(opinions_collection.find({"product_id": product_id}))
        product["opinions"] = opinions
    return products
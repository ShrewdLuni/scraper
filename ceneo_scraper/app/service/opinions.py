from bson import ObjectId
from ..db import opinions_collection

def create_opinion(product_id, opinion_data, custom_id=None):
    opinion_id = custom_id if custom_id else str(ObjectId())

    opinion = {
      "_id": opinion_id,
      "product_id": product_id,
      "author": opinion_data.get("author"),
      "recommendation": opinion_data.get("recommendation"),
      "score": opinion_data.get("score"),
      "content": opinion_data.get("content"),
      "advantages": opinion_data.get("advantages", []),
      "disadvantages": opinion_data.get("disadvantages", []),
      "helpful_count": opinion_data.get("helpful_count", 0),
      "unhelpful_count": opinion_data.get("unhelpful_count", 0),
      "publish_date": opinion_data.get("publish_date"),
      "purchase_date": opinion_data.get("purchase_date"),
    }

    opinions_collection.insert_one(opinion)
    return opinion

def get_opinions_by_product_id(product_id):
  return list(opinions_collection.find({"product_id": product_id}))
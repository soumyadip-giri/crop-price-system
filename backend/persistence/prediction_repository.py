# backend/persistence/prediction_repository.py
from datetime import datetime, timedelta
from bson import ObjectId
from .mongo_client import get_predictions_collection
from bson import ObjectId

def save_prediction(user_id, request_data, features_used, predicted_price, advice):
    col = get_predictions_collection()
    doc = {
        "userId": user_id,
        "request": request_data,
        "featuresUsed": features_used,
        "predictedPrice": float(predicted_price),
        "advice": advice,
        "createdAt": datetime.utcnow(),
    }
    res = col.insert_one(doc)
    return str(res.inserted_id)

def find_by_user(user_id, limit=50):
    col = get_predictions_collection()
    cursor = col.find({"userId": user_id}).sort("createdAt", -1).limit(limit)
    return list(cursor)

def aggregate_by_district(crop=None, days=7):
    col = get_predictions_collection()
    since = datetime.utcnow() - timedelta(days=days)

    pipeline = [
        {"$match": {"createdAt": {"$gte": since}}},
        {"$group": {
            "_id": {
                "market": "$request.market",
                "crop": "$request.crop",
            },
            "avgPrice": {"$avg": "$predictedPrice"},
        }},
    ]
    results = list(col.aggregate(pipeline))
    out = []
    for r in results:
        if crop and r["_id"]["crop"] != crop:
            continue
        out.append({
            "market": r["_id"]["market"],
            "crop": r["_id"]["crop"],
            "avgPrice": float(r["avgPrice"]),
        })
    return out

def update_actual_price(prediction_id: str, actual_price: float):
    """
    Store actual realised price for a prediction and return updated document.
    """
    col = get_predictions_collection()
    try:
        oid = ObjectId(prediction_id)
    except Exception:
        return None

    doc = col.find_one({"_id": oid})
    if not doc:
        return None

    diff = float(actual_price) - float(doc["predictedPrice"])
    col.update_one(
        {"_id": oid},
        {"$set": {
            "actualPrice": float(actual_price),
            "priceDiff": diff,
        }}
    )
    doc["actualPrice"] = float(actual_price)
    doc["priceDiff"] = diff
    return doc

def delete_prediction(user_id, prediction_id: str) -> bool:
    """
    Delete a prediction document for this user.
    Returns True if a document was deleted.
    """
    col = get_predictions_collection()
    try:
        oid = ObjectId(prediction_id)
    except Exception:
        return False

    res = col.delete_one({"_id": oid, "userId": user_id})
    return res.deleted_count == 1
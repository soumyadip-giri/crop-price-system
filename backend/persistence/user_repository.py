# backend/persistence/user_repository.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .mongo_client import get_users_collection

def create_user(name, email, userid, password, dob):
    col = get_users_collection()

    if col.find_one({"userid": userid}):
        return None, "USERID_EXISTS"
    if col.find_one({"email": email}):
        return None, "EMAIL_EXISTS"

    doc = {
        "name": name,
        "email": email,
        "userid": userid,
        "passwordHash": generate_password_hash(password),
        "dob": dob,
        "createdAt": datetime.utcnow(),
    }
    res = col.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc, None

def find_by_userid(userid):
    col = get_users_collection()
    return col.find_one({"userid": userid})

def verify_user(userid, raw_password):
    user = find_by_userid(userid)
    if not user:
        return None
    if not check_password_hash(user["passwordHash"], raw_password):
        return None
    return user

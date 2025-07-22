import json, os
from keys.secrets import ACCESS_PASSWORD

WHITELIST = os.path.join("storage", "whitelist.json")

def verify_password(given: str) -> bool:
    if given == ACCESS_PASSWORD:
        return True
    return False

def is_user_allowed(user_id: int) -> bool: 
    if not os.path.exists("storage") or not os.path.exists(WHITELIST):
        return False

    with open(WHITELIST, "r") as f:
        loaded_ids = json.load(f)

    if user_id in loaded_ids:
        return True

    return False
    
def allow_user(user_id: int) -> None:
    os.makedirs("storage", exist_ok=True)
    ids = {user_id}

    if os.path.exists(WHITELIST):
        with open(WHITELIST, "r") as f:
            try:
                ids = set(json.load(f))
                ids.add(user_id)
            except:
                pass

    with open(WHITELIST, "w") as f:
        json.dump(list(ids), f)
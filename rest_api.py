import json
from copy import deepcopy

class RestAPI:
    def __init__(self, database=None):
        self.database = database if database else {"users": []}

    def get(self, url, payload=None):
        if url == "/users":
            if payload is None:
                return json.dumps({"users": sorted(self.database["users"], key=lambda x: x["name"])})
            
            data = json.loads(payload)
            requested_users = data["users"]
            filtered_users = [user for user in self.database["users"] 
                            if user["name"] in requested_users]
            return json.dumps({"users": sorted(filtered_users, key=lambda x: x["name"])})

    def post(self, url, payload=None):
        if payload is None:
            return None
            
        data = json.loads(payload)
        
        if url == "/add":
            new_user = {
                "name": data["user"],
                "owes": {},
                "owed_by": {},
                "balance": 0.0
            }
            self.database["users"].append(new_user)
            return json.dumps(new_user)
            
        elif url == "/iou":
            lender = data["lender"]
            borrower = data["borrower"]
            amount = float(data["amount"])
            
            lender_record = next(user for user in self.database["users"] 
                               if user["name"] == lender)
            borrower_record = next(user for user in self.database["users"] 
                                 if user["name"] == borrower)
            
            # Update lender's records
            if borrower in lender_record["owes"]:
                if lender_record["owes"][borrower] >= amount:
                    lender_record["owes"][borrower] -= amount
                    if lender_record["owes"][borrower] == 0:
                        del lender_record["owes"][borrower]
                else:
                    remaining = amount - lender_record["owes"][borrower]
                    del lender_record["owes"][borrower]
                    lender_record["owed_by"][borrower] = lender_record.get("owed_by", {}).get(borrower, 0) + remaining
            else:
                lender_record["owed_by"][borrower] = lender_record.get("owed_by", {}).get(borrower, 0) + amount
                
            # Update borrower's records
            if borrower_record.get("owed_by", {}).get(lender, 0) > 0:
                if borrower_record["owed_by"][lender] >= amount:
                    borrower_record["owed_by"][lender] -= amount
                    if borrower_record["owed_by"][lender] == 0:
                        del borrower_record["owed_by"][lender]
                else:
                    remaining = amount - borrower_record["owed_by"][lender]
                    del borrower_record["owed_by"][lender]
                    borrower_record["owes"][lender] = borrower_record.get("owes", {}).get(lender, 0) + remaining
            else:
                borrower_record["owes"][lender] = borrower_record.get("owes", {}).get(lender, 0) + amount
            
            # Update balances
            for user in [lender_record, borrower_record]:
                user["balance"] = sum(user.get("owed_by", {}).values()) - sum(user.get("owes", {}).values())
            
            return json.dumps({
                "users": sorted([lender_record, borrower_record], key=lambda x: x["name"])
            })

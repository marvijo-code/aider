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
        print("\n" + "="*50)  
        print(f"PfffffffffffffffOST request to {url}")
        if payload is None:
            return None
            
        data = json.loads(payload)
        print(f"Received payload: {data}")
        
        if url == "/add":
            new_user = {
                "name": data["user"],
                "owes": {},
                "owed_by": {},
                "balance": 0.0
            }
            self.database["users"].append(new_user)
            print(f"Adding new user: {new_user}")
            return json.dumps(new_user)
            
        elif url == "/iou":
            lender = data["lender"]
            borrower = data["borrower"]
            amount = float(data["amount"])
            
            lender_record = next(user for user in self.database["users"] 
                               if user["name"] == lender)
            borrower_record = next(user for user in self.database["users"] 
                                 if user["name"] == borrower)
            
            print(f"\nProcessing IOU: {lender} lending {amount} to {borrower}")
            print(f"Before update - Lender {lender}: {json.dumps(lender_record, indent=2)}")
            print(f"Before update - Borrower {borrower}: {json.dumps(borrower_record, indent=2)}")
            
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
                owed_by_sum = sum(user.get("owed_by", {}).values())
                owes_sum = sum(user.get("owes", {}).values())
                user["balance"] = owed_by_sum - owes_sum
                print(f"\nCalculating balance for {user['name']}:")
                print(f"  Owed by others: {owed_by_sum}")
                print(f"  Owes to others: {owes_sum}")
                print(f"  Final balance: {user['balance']}")
            
            print(f"\nAfter update - Lender {lender}: {json.dumps(lender_record, indent=2)}")
            print(f"After update - Borrower {borrower}: {json.dumps(borrower_record, indent=2)}")
            print("="*50 + "\n")
            
            return json.dumps({
                "users": sorted([lender_record, borrower_record], key=lambda x: x["name"])
            })

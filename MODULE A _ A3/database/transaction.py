import json
import os
import threading

class TransactionManager:
    def __init__(self, db_manager, log_file="log.txt"):
        self.db = db_manager
        self.log_file = log_file
        self.active_txn = None
        self.txn_id = 0
        self.lock = threading.Lock()

  
    def begin(self):
        self.lock.acquire()
        self.txn_id += 1
        self.active_txn = {
            "id": self.txn_id,
            "operations": []
        }
        self._log({"type": "BEGIN", "txn_id": self.txn_id})
        print(f"Transaction {self.txn_id} STARTED")



    def insert(self, table, key, value):
  
        if isinstance(value, dict):

            # Balance constraint
            if "balance" in value and value["balance"] < 0:
                raise Exception("Invalid: Negative balance")

            # Stock constraint
            if "stock" in value and value["stock"] < 0:
                raise Exception("Invalid: Negative stock")

        old_value = table.search(key)

        self._log({
            "type": "INSERT",
            "txn_id": self.txn_id,
            "table": table.name,
            "key": key,
            "old": old_value,
            "new": value
        })

        self.active_txn["operations"].append(
            ("INSERT", table, key, old_value)
        )

        table.insert(key, value)

  
    def update(self, table, key, new_value):
        old_value = table.search(key)

        if isinstance(new_value, dict):

            # 1. Balance should not be negative
            if "balance" in new_value and new_value["balance"] < 0:
                raise Exception("Invalid: Negative balance")

            # 2. Stock should not be negative
            if "stock" in new_value and new_value["stock"] < 0:
                raise Exception("Invalid: Negative stock")

       
        self._log({
            "type": "UPDATE",
            "txn_id": self.txn_id,
            "table": table.name,
            "key": key,
            "old": old_value,
            "new": new_value
        })

        self.active_txn["operations"].append(
            ("UPDATE", table, key, old_value)
        )

        table.update(key, new_value)

  
    def delete(self, table, key):
        old_value = table.search(key)

        self._log({
            "type": "DELETE",
            "txn_id": self.txn_id,
            "table": table.name,
            "key": key,
            "old": old_value
        })

        self.active_txn["operations"].append(
            ("DELETE", table, key, old_value)
        )

        table.delete(key)


    def commit(self):
        self._log({"type": "COMMIT", "txn_id": self.txn_id})

        self.db.save()   # save AFTER logging

        print(f"Transaction {self.txn_id} COMMITTED")

        self.active_txn = None
        self.lock.release()


    def rollback(self):
        print(f"ROLLBACK Transaction {self.txn_id}")

        for op in reversed(self.active_txn["operations"]):
            action, table, key, old_value = op

            if action == "INSERT":
                table.delete(key)

            elif action == "DELETE":
                table.insert(key, old_value)

            elif action == "UPDATE":
                table.update(key, old_value)

        self._log({"type": "ROLLBACK", "txn_id": self.txn_id})
        self.active_txn = None
        self.lock.release()

    def _log(self, record):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(record) + "\n")

    
    def recover(self):
        import os, json

        if not os.path.exists(self.log_file):
            return

        print("Recovering from log...")

        with open(self.log_file, "r") as f:
            logs = [json.loads(line) for line in f]

        committed = set()
        active = set()


        for log in logs:
            if log["type"] == "BEGIN":
                active.add(log["txn_id"])
            elif log["type"] == "COMMIT":
                committed.add(log["txn_id"])
                active.discard(log["txn_id"])

   
        print("Undoing incomplete transactions...")
        for log in reversed(logs):
            txn_id = log.get("txn_id")

            if txn_id in committed:
                continue

            if log["type"] == "INSERT":
                table = self.db.get_table(log["table"])
                table.delete(log["key"])

            elif log["type"] == "DELETE":
                table = self.db.get_table(log["table"])
                table.insert(log["key"], log["old"])

            elif log["type"] == "UPDATE":
                table = self.db.get_table(log["table"])
                table.update(log["key"], log["old"])

        print("Recovery complete.")

   
        open(self.log_file, "w").close()
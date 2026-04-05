from fileinput import filename
import os


class DBManager:
    """Simple database manager for handling multiple tables"""
    
    def __init__(self):
        self.tables = {}
    
    def create_table(self, name, index):
        from .table import Table
        self.tables[name] = Table(name, index)
        return self.tables[name]
    
    def get_table(self, name):
        return self.tables.get(name)
    
    def list_tables(self):
        return list(self.tables.keys())
    
    def save(self, filename="db.pkl"):
        import pickle
        with open(filename, "wb") as f:
            pickle.dump(self.tables, f)

    def load(self, filename="db.pkl"):
        import pickle, os
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                self.tables = pickle.load(f)
    
    def get_all_tables(self):
        return self.tables

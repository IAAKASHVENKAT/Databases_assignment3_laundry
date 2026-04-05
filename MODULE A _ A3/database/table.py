class Table:
    """Table abstraction using B+ Tree as index"""
    
    def __init__(self, name, index):
        self.name = name
        self.index = index
    
    def insert(self, key, value):
        self.index.insert(key, value)
    
    def search(self, key):
        return self.index.search(key)
    
    def delete(self, key):
        self.index.delete(key)
    
    def range_query(self, start, end):
        return self.index.range_query(start, end)
    
    def get_all(self):
        return self.index.get_all()
    
    def update(self, key, new_value):
        return self.index.update(key, new_value)

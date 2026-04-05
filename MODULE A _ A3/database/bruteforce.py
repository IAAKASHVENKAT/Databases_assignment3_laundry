class BruteForceIndex:
    """Simple list-based indexing for performance comparison"""
    
    def __init__(self):
        self.data = []
    
    def insert(self, key, value):
        self.data.append((key, value))
        self.data.sort(key=lambda x: x[0])
    
    def search(self, key):
        for k, v in self.data:
            if k == key:
                return v
        return None
    
    def delete(self, key):
        self.data = [(k, v) for k, v in self.data if k != key]
    
    def range_query(self, start, end):
        return [(k, v) for k, v in self.data if start <= k <= end]
    
    def get_all(self):
        return self.data
    
    def update(self, key, new_value):
        for i, (k, v) in enumerate(self.data):
            if k == key:
                self.data[i] = (k, new_value)
                return True
        return False

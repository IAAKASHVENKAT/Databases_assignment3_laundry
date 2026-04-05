import time
import sys
from .bplustree import BPlusTree
from .bruteforce import BruteForceIndex


class PerformanceAnalyzer:
    """Benchmark B+ Tree against Brute Force"""
    
    def __init__(self, n, runs=5):
        self.n = n
        self.runs = runs
        self.keys = list(range(n))
    
    def test_insert(self):
        bpt_times = []
        bf_times = []
        
        for _ in range(self.runs):
            start = time.time()
            bpt = BPlusTree()
            for key in self.keys:
                bpt.insert(key, key)
            bpt_times.append(time.time() - start)
            
            start = time.time()
            bf = BruteForceIndex()
            for key in self.keys:
                bf.insert(key, key)
            bf_times.append(time.time() - start)
        
        return sum(bpt_times) / len(bpt_times), sum(bf_times) / len(bf_times)
    
    def test_search(self):
        bpt = BPlusTree()
        bf = BruteForceIndex()
        for key in self.keys:
            bpt.insert(key, key)
            bf.insert(key, key)
        
        bpt_times = []
        bf_times = []
        
        for _ in range(self.runs):
            start = time.time()
            for key in self.keys:
                bpt.search(key)
            bpt_times.append(time.time() - start)
            
            start = time.time()
            for key in self.keys:
                bf.search(key)
            bf_times.append(time.time() - start)
        
        return sum(bpt_times) / len(bpt_times), sum(bf_times) / len(bf_times)
    
    def test_delete(self):
        bpt_times = []
        bf_times = []
        
        for _ in range(self.runs):
            bpt = BPlusTree()
            bf = BruteForceIndex()
            for key in self.keys:
                bpt.insert(key, key)
                bf.insert(key, key)
            
            start = time.time()
            for key in self.keys[:self.n//2]:
                bpt.delete(key)
            bpt_times.append(time.time() - start)
            
            start = time.time()
            for key in self.keys[:self.n//2]:
                bf.delete(key)
            bf_times.append(time.time() - start)
        
        return sum(bpt_times) / len(bpt_times), sum(bf_times) / len(bf_times)
    
    def test_range(self):
        bpt = BPlusTree()
        bf = BruteForceIndex()
        for key in self.keys:
            bpt.insert(key, key)
            bf.insert(key, key)
        
        bpt_times = []
        bf_times = []
        
        for _ in range(self.runs):
            start = time.time()
            bpt.range_query(self.n//4, 3*self.n//4)
            bpt_times.append(time.time() - start)
            
            start = time.time()
            bf.range_query(self.n//4, 3*self.n//4)
            bf_times.append(time.time() - start)
        
        return sum(bpt_times) / len(bpt_times), sum(bf_times) / len(bf_times)
    
    def memory_usage(self):
        import tracemalloc
        
        tracemalloc.start()
        bpt = BPlusTree()
        for key in self.keys:
            bpt.insert(key, key)
        _, peak_bpt = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tracemalloc.start()
        bf = BruteForceIndex()
        for key in self.keys:
            bf.insert(key, key)
        _, peak_bf = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return peak_bpt, peak_bf
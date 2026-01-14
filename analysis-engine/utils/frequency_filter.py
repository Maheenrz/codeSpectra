import hashlib
from collections import Counter

class BatchFrequencyFilter:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.common_hashes = set()

    def train_on_batch(self, all_files_tokens, k=5):
        """Finds hashes that appear in more than 70% of files."""
        if len(all_files_tokens) < 2: return
        
        global_counts = Counter()
        for tokens in all_files_tokens:
            file_hashes = set()
            for i in range(len(tokens) - k + 1):
                window = "|".join(tokens[i:i+k])
                h = int(hashlib.md5(window.encode('utf-8')).hexdigest(), 16)
                file_hashes.add(h)
            global_counts.update(file_hashes)

        cutoff = len(all_files_tokens) * self.threshold
        self.common_hashes = {h for h, count in global_counts.items() if count >= cutoff}
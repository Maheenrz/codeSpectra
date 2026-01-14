import hashlib

class WinnowingDetector:
    def __init__(self, k=5, window_size=4):
        self.k = k # Length of the code snippet
        self.w = window_size # How many hashes per window

    def _get_hashes(self, tokens):
        hashes = []
        # TODO: Implement Step 1
        # Loop through tokens, create k-grams, return list of numbers
        for i in range(len(tokens) - self.k + 1):
            window = "|".join(tokens[i:i+self.k])
            h = int(hashlib.md5(window.encode('utf-8')).hexdigest(), 16)
            hashes.append(h)
        return hashes
            

    def get_fingerprint(self, tokens):
        hashes = self._get_hashes(tokens)
        fingerprints = set()
        
        # TODO: Implement Step 2 & 3
        # 1. Slide a window of size 'self.w' over 'hashes'
        # 2. In each window, find the minimum value
        # 3. Add that minimum value to the 'fingerprints' set
        
        for i in range(len(hashes) - self.w + 1):
            frame = hashes[i : i + self.w]
            min_value = min(frame)
            fingerprints.add(min_value)


        return fingerprints
    
    # Jaccard similarity
    def calculate_similarity(self,set_a,set_b):
        """
        Calculates the Jaccard Similarity between two fingerprint sets.
        Returns a value between 0.0 (no match) and 1.0 (perfect match).
        """ 

        if not set_a or not set_b:
            return 0.0
        

        intersection = set_a.intersection(set_b)
        union = set_a.union(set_b)
        #  Divide shared by total
        return len(intersection)/len(union)
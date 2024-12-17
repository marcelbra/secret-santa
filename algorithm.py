"""
By Claude 3.5 Sonnet - Dec. 2024
Assume an arbitrary number of sets S_1 = {A,B,C}, S_2 = {D,E,F}, ... etc.
The number elements in the sets is arbitrary, too, but typically not very high.
This means an algorithm with a higher time complexity is viable as well.
The algorithm shall assign each element in one set another element in another set.
So the result is basically a directed graph with this constraint.
I need you to design, implement, test and visualize this algorithm for me.
"""
import random
import json

from collections import defaultdict

class Matcher:
    def __init__(self, sets: list[set]):
        self.sets = sets
        self.matches = defaultdict(str)
        
    def generate_matches(self) -> dict[str, str]:
        """Generate matches between elements of different sets."""
        # Create a list of all elements and their set indices
        elements = [(elem, idx) for idx, s in enumerate(self.sets) 
                   for elem in s]
        
        # Shuffle elements to get random matches
        unmatched = elements.copy()
        
        while unmatched:
            current_elem, current_set_idx = unmatched.pop(0)
            
            # Find possible matches (elements from other sets)
            possible_matches = [
                (elem, set_idx) for elem, set_idx in unmatched
                if set_idx != current_set_idx and elem not in self.matches.values()
            ]
            
            # If no possible matches, try elements that are already matched
            if not possible_matches:
                possible_matches = [
                    (elem, set_idx) for elem, set_idx in elements
                    if set_idx != current_set_idx and 
                    elem != current_elem and
                    elem not in self.matches.values()
                ]
            
            if possible_matches:
                # Select a random match
                match_elem, _ = random.choice(possible_matches)
                self.matches[current_elem] = match_elem
            
        return dict(self.matches)

    def verify_matches(self) -> bool:
        """Verify that the matching follows all constraints."""
        if not self.matches:
            return False
            
        # Check if each element has exactly one match
        elements = set().union(*self.sets)
        if len(self.matches) != len(elements):
            return False
            
        # Check if matches are between different sets
        for elem, match in self.matches.items():
            elem_set = next(i for i, s in enumerate(self.sets) if elem in s)
            match_set = next(i for i, s in enumerate(self.sets) if match in s)
            if elem_set == match_set:
                return False
                
        return True

# Test the implementation
def test_matcher(sets):

    matcher = Matcher(sets)
    
    matches = None
    while True:
        matches = matcher.generate_matches()
        is_valid = matcher.verify_matches()
        if is_valid:
            break

    return matches

if __name__ == "__main__":
    email_mapping_path = "email_mapping.json"
    with open(email_mapping_path, "r") as f:
        sets = json.load(f)
    matches = test_matcher(sets)
    with open("matches.json", "w") as f:
        json.dump(matches, f, indent=4, ensure_ascii=False)
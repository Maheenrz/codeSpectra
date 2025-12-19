def calculate_sum(a, b):
    # This calculates sum
    result = a + b
    return result

def different_function(x):
    # This is different
    return x * 2

def find_maximum(numbers):
    # Exact clone of find_maximum from file 1
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val
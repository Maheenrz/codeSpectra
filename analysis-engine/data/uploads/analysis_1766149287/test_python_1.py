def calculate_sum(a, b):
    '''Calculate the sum of two numbers'''
    result = a + b
    return result

def calculate_product(x, y):
    '''Calculate product of two numbers'''
    result = x * y
    return result

def find_maximum(numbers):
    '''Find maximum in a list'''
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val
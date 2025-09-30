def flatten_list(my_list):
    """Flatten a nested list recursively."""
    result = []
    for item in my_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result

# Test cases
print("Original test:")
print(flatten_list(['1', ['4', ['5', ['3']], '2'], '9']))

print("\nAdditional test cases:")
print("Empty list:", flatten_list([]))
print("Single level:", flatten_list([1, 2, 3]))
print("Mixed types:", flatten_list([1, ['a', 'b'], 3.14, ['x', ['y']]]))

# Even more robust version that handles other iterables
def flatten_list_robust(my_list):
    """Flatten a nested structure recursively, handling various iterable types."""
    result = []
    for item in my_list:
        if isinstance(item, (list, tuple)):
            result.extend(flatten_list_robust(item))
        elif item is not None:  # Handle None values
            result.append(item)
    return result

print("\nRobust version with tuples:")
print(flatten_list_robust([1, (2, 3), [4, (5, 6)]]))

# Using built-in alternatives (Python 3.4+)
def flatten_with_itertools(iterable):
    """Flatten using itertools (handles any iterable)."""
    import itertools
    return list(itertools.chain.from_iterable(
        flatten_with_itertools(item) if isinstance(item, (list, tuple)) 
        else [item] for item in iterable
    ))

print("\nUsing itertools:")
print(flatten_with_itertools([1, [2, [3, 4]], 5]))


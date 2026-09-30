"""
Sample Python Application demonstrating Continuous Integration (CI) Workflows.
"""

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def is_palindrome(text: str) -> bool:
    cleaned = ''.join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]

if __name__ == '__main__':
    print("Sample CI Application Running...")
    print(f"2 + 3 = {add(2, 3)}")
    print(f"4 * 5 = {multiply(4, 5)}")
    print(f"Is 'racecar' a palindrome? {is_palindrome('racecar')}")

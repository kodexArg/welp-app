import random

def generate_password(length=10):
    safe_letters = 'abcdefghjkmnpqrstuvwxyz'
    safe_digits = '23456789'
    allowed_chars = safe_letters + safe_digits
    return ''.join(random.choices(allowed_chars, k=length))

print(generate_password())

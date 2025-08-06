import random

def generate_password(length=10):
    # Consonantes y vocales para patrones pronunciables
    consonants = 'bcdfghjkmnpqrstvwxyz'
    vowels = 'aeiou'
    safe_digits = '23456789'
    safe_symbols = '!@#$%'
    
    # Asegurar longitud mínima de 8
    if length < 8:
        length = 8
    
    password = []
    
    # Patrón base: consonante-vocal-consonante + dígito + símbolo
    # Repetir según la longitud solicitada
    while len(password) < length:
        # Agregar patrón consonante-vocal-consonante
        if len(password) < length:
            password.append(random.choice(consonants))
        if len(password) < length:
            password.append(random.choice(vowels))
        if len(password) < length:
            password.append(random.choice(consonants))
        
        # Agregar dígito cada 3-4 caracteres
        if len(password) < length and len(password) % 3 == 0:
            password.append(random.choice(safe_digits))
        
        # Agregar símbolo ocasionalmente
        if len(password) < length and len(password) % 5 == 0:
            password.append(random.choice(safe_symbols))
    
    # Truncar si excede la longitud
    password = password[:length]
    
    # Asegurar que tenga al menos un dígito y un símbolo
    has_digit = any(c in safe_digits for c in password)
    has_symbol = any(c in safe_symbols for c in password)
    
    if not has_digit and length > 4:
        password[3] = random.choice(safe_digits)
    
    if not has_symbol and length > 6:
        password[5] = random.choice(safe_symbols)
    
    return ''.join(password)

print(generate_password())

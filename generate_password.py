#!/usr/bin/env python3
"""
Script pour générer un hash bcrypt du mot de passe admin
"""

import bcrypt

def generate_password_hash(password: str):
    """Génère un hash bcrypt du mot de passe"""
    # Générer le hash
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(12)
    password_hash = bcrypt.hashpw(password_bytes, salt)
    
    print(f"Mot de passe: {password}")
    print(f"Hash bcrypt: {password_hash.decode('utf-8')}")
    
    # Vérifier le hash
    is_valid = bcrypt.checkpw(password_bytes, password_hash)
    print(f"Vérification: {'✅ Valide' if is_valid else '❌ Invalide'}")
    
    return password_hash.decode('utf-8')

if __name__ == "__main__":
    # Générer le hash pour "admin"
    generate_password_hash("admin")

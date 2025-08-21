#!/usr/bin/env python3
"""
Script pour créer un cadre de test PNG avec transparence
"""

from PIL import Image, ImageDraw
import os

def create_test_frame():
    """Crée un cadre de test simple"""
    
    # Créer le dossier frames s'il n'existe pas
    os.makedirs("frames", exist_ok=True)
    
    # Dimensions du cadre
    width, height = 400, 300
    
    # Créer une image avec transparence
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Dessiner un cadre simple avec bordure
    border_width = 20
    
    # Bordure extérieure
    draw.rectangle([0, 0, width-1, height-1], 
                  outline=(255, 215, 0, 255),  # Or
                  width=border_width)
    
    # Bordure intérieure
    draw.rectangle([border_width, border_width, width-border_width-1, height-border_width-1], 
                  outline=(255, 255, 255, 200),  # Blanc semi-transparent
                  width=5)
    
    # Ajouter un coin décoratif
    corner_size = 40
    draw.rectangle([0, 0, corner_size, corner_size], 
                  fill=(255, 215, 0, 180))  # Or semi-transparent
    
    # Sauvegarder le cadre
    frame_path = "frames/test_frame.png"
    image.save(frame_path, "PNG")
    
    print(f"Cadre de test créé : {frame_path}")
    print(f"Dimensions : {width}x{height} pixels")
    print("Format : PNG avec transparence")
    
    return frame_path

if __name__ == "__main__":
    create_test_frame()

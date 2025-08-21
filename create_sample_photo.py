#!/usr/bin/env python3
"""
Script pour créer une photo d'exemple pour la prévisualisation des cadres
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_photo():
    """Crée une photo d'exemple simple"""
    
    # Créer le dossier static/img s'il n'existe pas
    os.makedirs("static/img", exist_ok=True)
    
    # Dimensions de la photo
    width, height = 800, 600
    
    # Créer une image avec un dégradé de fond
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Créer un dégradé de fond
    for y in range(height):
        r = int(100 + (y / height) * 100)  # Rouge de 100 à 200
        g = int(150 + (y / height) * 50)   # Vert de 150 à 200
        b = int(200 + (y / height) * 55)   # Bleu de 200 à 255
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Ajouter un cercle central
    center_x, center_y = width // 2, height // 2
    circle_radius = 150
    draw.ellipse([center_x - circle_radius, center_y - circle_radius,
                  center_x + circle_radius, center_y + circle_radius],
                 fill=(255, 255, 255, 100), outline=(255, 255, 255, 200), width=3)
    
    # Ajouter du texte
    try:
        # Essayer d'utiliser une police système
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        # Fallback vers la police par défaut
        font = ImageFont.load_default()
    
    text = "PHOTO EXEMPLE"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = (width - text_width) // 2
    text_y = center_y + circle_radius + 30
    
    # Ombre du texte
    draw.text((text_x + 2, text_y + 2), text, fill=(0, 0, 0, 150), font=font)
    # Texte principal
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Ajouter quelques éléments décoratifs
    for i in range(5):
        x = 100 + i * 120
        y = 100
        size = 30 + i * 10
        color = (255, 100 + i * 30, 100, 255)
        draw.ellipse([x, y, x + size, y + size], fill=color)
    
    # Sauvegarder la photo
    photo_path = "static/img/sample-photo.jpg"
    image.save(photo_path, "JPEG", quality=90)
    
    print(f"Photo d'exemple créée : {photo_path}")
    print(f"Dimensions : {width}x{height} pixels")
    print("Format : JPEG haute qualité")
    
    return photo_path

if __name__ == "__main__":
    create_sample_photo()

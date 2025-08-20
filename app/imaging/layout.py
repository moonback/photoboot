"""
Module de mise en page d'impression pour le photobooth
Gère la composition des photos avec cadres et texte selon les templates
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)


class PrintLayout:
    """Gestionnaire de mise en page d'impression"""
    
    def __init__(self, templates_dir: str = "app/imaging/printing/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Charge tous les templates disponibles"""
        try:
            for template_file in self.templates_dir.glob("*.json"):
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template_name = template_file.stem
                    self.templates[template_name] = template_data
                    logger.info(f"Template chargé: {template_name}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des templates: {e}")
    
    def get_template(self, template_name: str) -> Optional[Dict]:
        """Récupère un template par son nom"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """Liste tous les templates disponibles"""
        return list(self.templates.keys())
    
    def compose_layout(self, 
                      photos: List[str], 
                      template_name: str, 
                      text_overlay: Optional[str] = None,
                      frame_name: Optional[str] = None) -> Tuple[str, str]:
        """
        Compose une mise en page selon le template
        
        Args:
            photos: Liste des chemins vers les photos
            template_name: Nom du template à utiliser
            text_overlay: Texte à superposer (optionnel)
            frame_name: Nom du cadre à utiliser (optionnel)
        
        Returns:
            Tuple (chemin_canvas_final, chemin_miniature)
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' non trouvé")
        
        # Convertir les dimensions en pixels
        dpi = template['dimensions']['dpi']
        width_mm = template['dimensions']['width_mm']
        height_mm = template['dimensions']['height_mm']
        
        # Conversion mm vers pixels (1 pouce = 25.4 mm)
        width_px = int((width_mm / 25.4) * dpi)
        height_px = int((height_mm / 25.4) * dpi)
        
        # Créer le canvas final
        canvas = Image.new('RGB', (width_px, height_px), 'white')
        
        # Appliquer la mise en page selon le type
        if template['layout']['type'] == 'grid':
            canvas = self._apply_grid_layout(canvas, photos, template, frame_name)
        elif template['layout']['type'] == 'single':
            canvas = self._apply_single_layout(canvas, photos[0] if photos else None, template, frame_name)
        
        # Ajouter le texte si activé
        if text_overlay and template['text_overlay']['enabled']:
            canvas = self._add_text_overlay(canvas, text_overlay, template)
        
        # Sauvegarder le canvas final
        output_dir = Path("data/prints")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        canvas_path = output_dir / f"print_{template_name}_{timestamp}.png"
        canvas.save(canvas_path, 'PNG', dpi=(dpi, dpi))
        
        # Créer la miniature
        thumbnail = canvas.copy()
        thumbnail.thumbnail((300, 300), Image.Resampling.LANCZOS)
        thumb_path = output_dir / f"thumb_{template_name}_{timestamp}.png"
        thumbnail.save(thumb_path, 'PNG')
        
        logger.info(f"Mise en page créée: {canvas_path}")
        return str(canvas_path), str(thumb_path)
    
    def _apply_grid_layout(self, canvas: Image.Image, photos: List[str], template: Dict, frame_name: Optional[str]) -> Image.Image:
        """Applique une mise en page en grille"""
        layout = template['layout']
        margins = template['margins']
        photo_settings = template['photo_settings']
        
        # Calculer les dimensions des cellules
        dpi = template['dimensions']['dpi']
        margin_px = int((margins['top_mm'] / 25.4) * dpi)
        spacing_px = int((layout['spacing_mm'] / 25.4) * dpi)
        
        cell_width = (canvas.width - 2 * margin_px - (layout['columns'] - 1) * spacing_px) // layout['columns']
        cell_height = (canvas.height - 2 * margin_px - (layout['rows'] - 1) * spacing_px) // layout['rows']
        
        # Placer chaque photo
        for i, photo_path in enumerate(photos[:layout['columns'] * layout['rows']]):
            if not os.path.exists(photo_path):
                continue
                
            row = i // layout['columns']
            col = i % layout['columns']
            
            x = margin_px + col * (cell_width + spacing_px)
            y = margin_px + row * (cell_height + spacing_px)
            
            # Charger et redimensionner la photo
            photo = Image.open(photo_path)
            photo = self._resize_photo(photo, cell_width, cell_height, photo_settings)
            
            # Appliquer le cadre si spécifié
            if frame_name:
                photo = self._apply_frame(photo, frame_name, template)
            
            # Placer la photo sur le canvas
            canvas.paste(photo, (x, y))
        
        return canvas
    
    def _apply_single_layout(self, canvas: Image.Image, photo_path: Optional[str], template: Dict, frame_name: Optional[str]) -> Image.Image:
        """Applique une mise en page simple (une seule photo)"""
        if not photo_path or not os.path.exists(photo_path):
            return canvas
        
        margins = template['margins']
        photo_settings = template['photo_settings']
        
        # Calculer les dimensions disponibles
        dpi = template['dimensions']['dpi']
        margin_px = int((margins['top_mm'] / 25.4) * dpi)
        
        available_width = canvas.width - 2 * margin_px
        available_height = canvas.height - 2 * margin_px
        
        # Charger et redimensionner la photo
        photo = Image.open(photo_path)
        photo = self._resize_photo(photo, available_width, available_height, photo_settings)
        
        # Appliquer le cadre si spécifié
        if frame_name:
            photo = self._apply_frame(photo, frame_name, template)
        
        # Centrer la photo
        x = (canvas.width - photo.width) // 2
        y = (canvas.height - photo.height) // 2
        
        canvas.paste(photo, (x, y))
        return canvas
    
    def _resize_photo(self, photo: Image.Image, target_width: int, target_height: int, settings: Dict) -> Image.Image:
        """Redimensionne une photo selon les paramètres"""
        # Calculer le ratio d'aspect cible
        target_ratio = target_width / target_height
        
        # Redimensionner en conservant le ratio
        photo.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Créer un nouveau canvas avec la taille cible
        result = Image.new('RGBA', (target_width, target_height), (255, 255, 255, 0))
        
        # Centrer la photo
        x = (target_width - photo.width) // 2
        y = (target_height - photo.height) // 2
        
        result.paste(photo, (x, y))
        
        # Appliquer les bordures et coins arrondis si configurés
        if settings.get('border_mm', 0) > 0:
            result = self._add_border(result, settings)
        
        return result
    
    def _add_border(self, image: Image.Image, settings: Dict) -> Image.Image:
        """Ajoute une bordure à l'image"""
        border_mm = settings.get('border_mm', 0)
        if border_mm <= 0:
            return image
        
        # Convertir en pixels (approximatif)
        border_px = max(1, int(border_mm))
        
        # Créer une nouvelle image avec bordure
        new_width = image.width + 2 * border_px
        new_height = image.height + 2 * border_px
        
        bordered = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 255))
        bordered.paste(image, (border_px, border_px))
        
        return bordered
    
    def _apply_frame(self, photo: Image.Image, frame_name: str, template: Dict) -> Image.Image:
        """Applique un cadre à la photo"""
        try:
            frame_path = Path("app/imaging/frames") / frame_name
            if not frame_path.exists():
                logger.warning(f"Cadre non trouvé: {frame_name}")
                return photo
            
            frame = Image.open(frame_path).convert('RGBA')
            
            # Redimensionner le cadre à la taille de la photo
            frame = frame.resize(photo.size, Image.Resampling.LANCZOS)
            
            # Appliquer l'opacité si configurée
            opacity = template.get('frame_settings', {}).get('opacity', 1.0)
            if opacity != 1.0:
                frame.putalpha(int(255 * opacity))
            
            # Superposer le cadre sur la photo
            result = Image.alpha_composite(photo.convert('RGBA'), frame)
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'application du cadre {frame_name}: {e}")
            return photo
    
    def _add_text_overlay(self, canvas: Image.Image, text: str, template: Dict) -> Image.Image:
        """Ajoute un texte superposé sur le canvas"""
        text_settings = template['text_overlay']
        
        # Créer un objet de dessin
        draw = ImageDraw.Draw(canvas)
        
        # Essayer de charger une police libre
        try:
            font_size = text_settings['font_size_pt']
            # Essayer plusieurs polices communes
            font = None
            for font_name in ['arial.ttf', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf']:
                try:
                    font = ImageFont.truetype(font_name, font_size)
                    break
                except:
                    continue
            
            if not font:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Calculer la position du texte
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Positionner le texte selon la configuration
        if text_settings['position'] == 'bottom':
            x = (canvas.width - text_width) // 2
            y = canvas.height - text_height - 20
        elif text_settings['position'] == 'top':
            x = (canvas.width - text_width) // 2
            y = 20
        else:  # center
            x = (canvas.width - text_width) // 2
            y = (canvas.height - text_height) // 2
        
        # Ajouter un fond si configuré
        if text_settings.get('background_color'):
            padding = int((text_settings.get('padding_mm', 1) / 25.4) * template['dimensions']['dpi'])
            bg_x1 = x - padding
            bg_y1 = y - padding
            bg_x2 = x + text_width + padding
            bg_y2 = y + text_height + padding
            
            draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], 
                         fill=text_settings['background_color'])
        
        # Dessiner le texte
        draw.text((x, y), text, 
                 font=font, 
                 fill=text_settings['font_color'])
        
        return canvas


# Instance globale
layout_manager = PrintLayout()

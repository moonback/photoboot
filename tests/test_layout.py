"""
Tests pour le module de mise en page d'impression
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from PIL import Image
import os

from app.imaging.layout import PrintLayout


class TestPrintLayout:
    """Tests pour la classe PrintLayout"""
    
    @pytest.fixture
    def temp_dir(self):
        """Créer un répertoire temporaire pour les tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_photos(self, temp_dir):
        """Créer des photos de test"""
        photos = []
        for i in range(4):
            # Créer une image de test
            img = Image.new('RGB', (640, 480), color=(100 + i * 50, 150, 200))
            photo_path = Path(temp_dir) / f"test_photo_{i}.jpg"
            img.save(photo_path, 'JPEG')
            photos.append(str(photo_path))
        return photos
    
    @pytest.fixture
    def layout_manager(self, temp_dir):
        """Créer une instance de PrintLayout avec un répertoire temporaire"""
        # Créer des templates de test
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Template strip_2x6
        strip_template = {
            "name": "Strip 2x6",
            "description": "Bande de photos 2x6 pouces",
            "dimensions": {
                "width_mm": 152.4,
                "height_mm": 50.8,
                "dpi": 300
            },
            "layout": {
                "type": "grid",
                "columns": 2,
                "rows": 1,
                "spacing_mm": 2.0
            },
            "margins": {
                "top_mm": 3.0,
                "bottom_mm": 3.0,
                "left_mm": 3.0,
                "right_mm": 3.0
            },
            "photo_settings": {
                "aspect_ratio": "4:3",
                "border_mm": 1.0,
                "corner_radius_mm": 2.0
            },
            "text_overlay": {
                "enabled": True,
                "position": "bottom",
                "font_size_pt": 12,
                "font_color": "#000000",
                "background_color": "#FFFFFF",
                "padding_mm": 1.0
            }
        }
        
        import json
        with open(templates_dir / "strip_2x6.json", 'w') as f:
            json.dump(strip_template, f)
        
        return PrintLayout(str(templates_dir))
    
    def test_load_templates(self, layout_manager):
        """Test du chargement des templates"""
        templates = layout_manager.list_templates()
        assert "strip_2x6" in templates
        assert len(templates) == 1
    
    def test_get_template(self, layout_manager):
        """Test de la récupération d'un template"""
        template = layout_manager.get_template("strip_2x6")
        assert template is not None
        assert template["name"] == "Strip 2x6"
        assert template["dimensions"]["dpi"] == 300
    
    def test_get_nonexistent_template(self, layout_manager):
        """Test de la récupération d'un template inexistant"""
        template = layout_manager.get_template("nonexistent")
        assert template is None
    
    def test_compose_layout_single_photo(self, layout_manager, sample_photos, temp_dir):
        """Test de la composition avec une seule photo"""
        # Créer le dossier de sortie
        output_dir = Path(temp_dir) / "output"
        output_dir.mkdir()
        
        # Modifier le chemin de sortie pour le test
        original_output_dir = layout_manager.output_dir
        layout_manager.output_dir = output_dir
        
        try:
            canvas_path, thumb_path = layout_manager.compose_layout(
                photos=[sample_photos[0]],
                template_name="strip_2x6",
                text_overlay="Test Photo"
            )
            
            # Vérifier que les fichiers ont été créés
            assert Path(canvas_path).exists()
            assert Path(thumb_path).exists()
            
            # Vérifier que ce sont des images valides
            canvas_img = Image.open(canvas_path)
            thumb_img = Image.open(thumb_path)
            
            assert canvas_img.size[0] > 0
            assert canvas_img.size[1] > 0
            assert thumb_img.size[0] > 0
            assert thumb_img.size[1] > 0
            
        finally:
            # Restaurer le chemin original
            layout_manager.output_dir = original_output_dir
    
    def test_compose_layout_multiple_photos(self, layout_manager, sample_photos, temp_dir):
        """Test de la composition avec plusieurs photos"""
        # Créer le dossier de sortie
        output_dir = Path(temp_dir) / "output"
        output_dir.mkdir()
        
        # Modifier le chemin de sortie pour le test
        original_output_dir = layout_manager.output_dir
        layout_manager.output_dir = output_dir
        
        try:
            canvas_path, thumb_path = layout_manager.compose_layout(
                photos=sample_photos[:2],  # Utiliser 2 photos
                template_name="strip_2x6"
            )
            
            # Vérifier que les fichiers ont été créés
            assert Path(canvas_path).exists()
            assert Path(thumb_path).exists()
            
        finally:
            # Restaurer le chemin original
            layout_manager.output_dir = original_output_dir
    
    def test_compose_layout_with_text(self, layout_manager, sample_photos, temp_dir):
        """Test de la composition avec du texte superposé"""
        # Créer le dossier de sortie
        output_dir = Path(temp_dir) / "output"
        output_dir.mkdir()
        
        # Modifier le chemin de sortie pour le test
        original_output_dir = layout_manager.output_dir
        layout_manager.output_dir = output_dir
        
        try:
            canvas_path, thumb_path = layout_manager.compose_layout(
                photos=[sample_photos[0]],
                template_name="strip_2x6",
                text_overlay="Photo avec texte"
            )
            
            # Vérifier que les fichiers ont été créés
            assert Path(canvas_path).exists()
            assert Path(thumb_path).exists()
            
        finally:
            # Restaurer le chemin original
            layout_manager.output_dir = original_output_dir
    
    def test_invalid_template(self, layout_manager, sample_photos):
        """Test avec un template invalide"""
        with pytest.raises(ValueError, match="Template 'invalid' non trouvé"):
            layout_manager.compose_layout(
                photos=sample_photos,
                template_name="invalid"
            )
    
    def test_no_photos(self, layout_manager):
        """Test sans photos"""
        with pytest.raises(ValueError, match="Aucune photo fournie"):
            layout_manager.compose_layout(
                photos=[],
                template_name="strip_2x6"
            )


if __name__ == "__main__":
    pytest.main([__file__])

# ============================================
# FICHIER 1: src/app/infrastructure/pdf_converter.py
# ============================================
"""
Infrastructure : Convertisseur PDF vers Markdown
Ce module gère la conversion technique des PDFs.
"""
import pytesseract
import cv2
import os
import tempfile
import shutil
from pdf2image import convert_from_path
from PIL import Image
import numpy as np
from typing import Optional
import sys
import shutil
from datetime import datetime


class PDFToMarkdownConverter:
    """
    Convertit un PDF en Markdown via OCR.
    Pipeline: PDF -> Images -> Preprocessing -> OCR -> Markdown
    """
    
    def __init__(
        self,
        dpi: int = 300,
        left_margin_ratio: float = 0.26,
        lang: str = "fra",
        temp_dir: Optional[str] = None
    ):
        self.dpi = dpi
        self.left_margin_ratio = left_margin_ratio
        self.lang = lang
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        
    def convert(self, pdf_path: str, output_md_path: Optional[str] = None) -> str:
        """
        Convertit un PDF en Markdown.
        
        Args:
            pdf_path: Chemin vers le PDF
            output_md_path: Chemin de sortie (None = auto)
            
        Returns:
            str: Chemin du fichier Markdown créé
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Le fichier PDF '{pdf_path}' n'existe pas")
        
        if output_md_path is None:
            output_md_path = pdf_path.replace('.pdf', '.md')
        
        try:
            # Étape 1: PDF -> Images
            pages = convert_from_path(pdf_path, dpi=self.dpi)
            
            # Étape 2 & 3: Traitement + OCR
            page_texts = []
            page_counter = 1
            
            for i, img in enumerate(pages):
                # Rotation 90° sens horaire
                img = img.rotate(-90, expand=True)
                
                # Suppression marge gauche
                width, height = img.size
                left_crop = int(width * self.left_margin_ratio)
                img = img.crop((left_crop, 0, width, height))
                
                # Découpage en deux pages
                width, height = img.size
                middle = width // 2
                
                left_page = img.crop((0, 0, middle, height))
                right_page = img.crop((middle, 0, width, height))
                
                # OCR sur chaque demi-page
                for page_img in [left_page, right_page]:
                    text = self._ocr_image(page_img, page_counter)
                    if text.strip():
                        page_texts.append((page_counter, text))
                    page_counter += 1
            
            # Étape 4: Génération Markdown
            self._generate_markdown(page_texts, output_md_path)
            
            return output_md_path
            
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la conversion PDF: {e}")
    
    def _ocr_image(self, pil_image: Image.Image, page_num: int) -> str:
        """Applique l'OCR sur une image PIL."""
        img_array = np.array(pil_image.convert('L'))
        
        _, img_binary = cv2.threshold(
            img_array, 
            0, 
            255, 
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        text = pytesseract.image_to_string(img_binary, lang=self.lang)
        return text
    
    def _generate_markdown(self, page_texts: list, output_path: str):
        """Génère le fichier Markdown stylisé."""
        with open(output_path, "w", encoding="utf-8") as md:
            for page_num, text in page_texts:
                md.write(f"<hr style='border:1px solid #ccc; margin:40px 0;'>\n")
                md.write(f"<div style='border: 1px solid #ddd; box-shadow: 2px 2px 12px rgba(0,0,0,0.1); padding: 20px; margin: 20px auto; max-width: 800px; background-color: #fafafa;'>\n")
                md.write(f"<h2 style='text-align:center;'>Page {page_num}</h2>\n")
                
                text_html = text.strip().replace("\n", "<br>")
                md.write(f"<p style='line-height:1.6; font-family:Georgia, serif;'>{text_html}</p>\n")
                md.write("</div>\n\n")
    
    def cleanup(self):
        """Nettoie le dossier temporaire."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

import fitz  # PyMuPDF
import re
import logging
from typing import Dict, List

def extract_paragraphs_by_page(
    pdf_path: str,
    threshold: int = 10,
    enable_logging: bool = False
) -> Dict[int, List[str]]:
    """
    Extrait les paragraphes d'un PDF en excluant les pages d'index selon un seuil.

    :param pdf_path: Chemin du fichier PDF.
    :param threshold: Seuil de motifs pour exclure les pages d’index.
    :param enable_logging: Active la journalisation des pages ignorées.
    :return: Dictionnaire {numéro_page: [paragraphes]}
    """
    paragraphs_by_page = {}

    if enable_logging:
        logging.basicConfig(level=logging.INFO)

    try:
        with fitz.open(pdf_path) as pdf_file:
            for page_index, page in enumerate(pdf_file):
                text = page.get_text("text")

                # Compter les motifs semblant indiquer une page d’index
                pattern_count = len(re.findall(r'\b\w+,\s*\d+', text))
                if pattern_count > threshold:
                    if enable_logging:
                        logging.info(f"[⏩ Skipped] Page {page_index + 1} identifiée comme index (motifs: {pattern_count})")
                    continue

                # Nettoyage du texte : suppression des lignes vides et des numéros de ligne
                paragraphs = [
                    line.strip()
                    for line in text.split('\n')
                    if line.strip() and not re.match(r'^\d+\w*[\s\W]+\d+$', line)
                ]

                if paragraphs:
                    paragraphs_by_page[page_index] = paragraphs

    except Exception as e:
        logging.error(f"[❌ Erreur] Impossible d’ouvrir ou analyser le PDF: {e}")

    return paragraphs_by_page

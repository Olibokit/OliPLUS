import pytest
from cockpit_ui.builder.builder_engine import BuilderEngine

def test_blocks_loaded():
    engine = BuilderEngine()
    blocks = engine.list_blocks()

    assert isinstance(blocks, list), "🧩 'blocks' doit être une liste cockpitifiée"
    assert "header" in blocks, "❌ Bloc 'header' manquant dans BuilderEngine"
    assert "paragraph" in blocks, "❌ Bloc 'paragraph' manquant dans BuilderEngine"

    # 🔍 Optionnel : affichage cockpit pour debug
    print(f"✅ Blocs disponibles : {blocks}")

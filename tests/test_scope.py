# Lightweight contract tests for the adviser scope terminology.
from pathlib import Path


def test_skill_file_exists():
    skill = Path(__file__).parents[1] / "prompts" / "agri_farmer_adviser.md"
    assert skill.exists()
    text = skill.read_text(encoding="utf-8").lower()
    assert "farmer" in text
    assert "out of scope" in text

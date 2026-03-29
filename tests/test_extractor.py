import pytest
import os
from src.extractor import extract_text, UnsupportedFormatError

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def test_extract_markdown():
    path = os.path.join(FIXTURES, "sample.md")
    text = extract_text(path)
    assert "performatividade" in text.lower()
    assert "blockchain" in text.lower()


def test_unsupported_format(tmp_path):
    f = tmp_path / "file.xyz"
    f.write_text("conteudo")
    with pytest.raises(UnsupportedFormatError):
        extract_text(str(f))


def test_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        extract_text("/nonexistent/file.md")

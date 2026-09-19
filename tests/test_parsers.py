import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from parsers.txt_parser import TextDocumentParser

def test_txt_parser():
    sample_text = "Hello World! This is a test document for intelligence extraction."
    parser = TextDocumentParser()
    extracted, metadata = parser.parse(sample_text.encode("utf-8"), "test.txt")
    
    assert extracted == sample_text
    assert metadata["word_count"] == 10
    assert metadata["detected_encoding"].lower() in ("utf-8", "ascii")

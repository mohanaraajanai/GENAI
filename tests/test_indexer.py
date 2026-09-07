from pathlib import Path

import pytest

from rag.indexer import FAISSIndexer


def test_splitter_rejects_invalid_overlap(tmp_path):
    indexer = FAISSIndexer(tmp_path / "downloads", tmp_path / "index")
    with pytest.raises(ValueError):
        indexer.build(chunk_size=500, chunk_overlap=500)


def test_safe_index_exists_false(tmp_path):
    indexer = FAISSIndexer(tmp_path / "downloads", tmp_path / "index")
    assert indexer.exists() is False

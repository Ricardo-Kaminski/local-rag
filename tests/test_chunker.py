from local_rag.chunker import chunk_text


def test_short_text_single_chunk():
    chunks = chunk_text("Texto curto.", "fonte.md", chunk_size=2000, overlap=200)
    assert len(chunks) == 1
    assert chunks[0]["text"] == "Texto curto."
    assert chunks[0]["source"] == "fonte.md"
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["total_chunks"] == 1


def test_long_text_multiple_chunks():
    text = "palavra " * 500  # ~4000 chars
    chunks = chunk_text(text, "longo.md", chunk_size=2000, overlap=200)
    assert len(chunks) >= 2
    for i, chunk in enumerate(chunks):
        assert chunk["chunk_index"] == i
        assert chunk["total_chunks"] == len(chunks)
        assert chunk["source"] == "longo.md"
        assert len(chunk["text"]) <= 2000 + 200


def test_overlap_shares_content():
    text = "a" * 4000
    chunks = chunk_text(text, "overlap.md", chunk_size=2000, overlap=200)
    end_of_first = chunks[0]["text"][-200:]
    start_of_second = chunks[1]["text"][:200]
    assert end_of_first == start_of_second


def test_metadata_preserved():
    chunks = chunk_text("texto", "D:/Obsidian/vault/tese.md", chunk_size=2000, overlap=200)
    assert chunks[0]["source"] == "D:/Obsidian/vault/tese.md"

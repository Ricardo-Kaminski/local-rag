from typing import List


def chunk_text(text: str, source: str, chunk_size: int = 2000, overlap: int = 200) -> List[dict]:
    if len(text) <= chunk_size:
        return [{"text": text, "source": source, "chunk_index": 0, "total_chunks": 1}]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    result = []
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        result.append({
            "text": chunk,
            "source": source,
            "chunk_index": i,
            "total_chunks": total
        })
    return result

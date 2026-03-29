import json
import os


class Checkpoint:
    def __init__(self, path: str):
        self.path = path
        self._data: dict = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self._data = json.load(f)

    def is_processed(self, file_path: str, mtime: float) -> bool:
        return self._data.get(file_path) == mtime

    def mark_processed(self, file_path: str, mtime: float) -> None:
        self._data[file_path] = mtime

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

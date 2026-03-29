import requests


class LightRAGError(Exception):
    pass


class LightRAGClient:
    def __init__(self, host: str = "localhost", port: int = 9621):
        self.base_url = f"http://{host}:{port}"

    def health_check(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def insert_text(self, text: str, description: str = "") -> None:
        r = requests.post(
            f"{self.base_url}/documents/text",
            json={"input_text": text, "description": description},
            timeout=120
        )
        if r.status_code != 200:
            raise LightRAGError(f"Insert failed [{r.status_code}]: {r.text}")

    def query(self, question: str, mode: str = "hybrid") -> str:
        r = requests.post(
            f"{self.base_url}/query",
            json={"query": question, "mode": mode},
            timeout=60
        )
        if r.status_code != 200:
            raise LightRAGError(f"Query failed [{r.status_code}]: {r.text}")
        return r.json()["response"]

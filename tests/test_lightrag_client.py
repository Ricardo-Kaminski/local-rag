import pytest
from unittest.mock import patch
from src.lightrag_client import LightRAGClient, LightRAGError


@pytest.fixture
def client():
    return LightRAGClient(host="localhost", port=9621)


def test_health_check_ok(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "ok"}
        assert client.health_check() is True


def test_health_check_fail(client):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("connection refused")
        assert client.health_check() is False


def test_insert_document(client):
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "ok"}
        client.insert_text("Texto de teste", description="test.md chunk 0/1")
        mock_post.assert_called_once()
        call_json = mock_post.call_args[1]["json"]
        assert "input_text" in call_json


def test_query(client):
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": "resultado da busca"}
        result = client.query("O que é performatividade?", mode="hybrid")
        assert result == "resultado da busca"


def test_query_raises_on_error(client):
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"
        with pytest.raises(LightRAGError):
            client.query("pergunta", mode="hybrid")

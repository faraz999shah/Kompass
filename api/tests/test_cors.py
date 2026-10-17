"""The browser build of the app may call the API from its dev origins, and nothing else may."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

UNLISTED_ORIGIN = "https://unknown.example"


@pytest.mark.parametrize(
    ("origin", "method", "path"),
    [
        ("http://localhost:8081", "POST", "/v1/bonus-lessons"),
        ("http://127.0.0.1:8081", "PATCH", "/v1/profile/u_test/language"),
        ("http://localhost:8081", "GET", "/v1/voice/speak"),
    ],
)
def test_expo_web_origins_may_call_the_api(origin: str, method: str, path: str) -> None:
    response = TestClient(app).options(
        path,
        headers={"Origin": origin, "Access-Control-Request-Method": method},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


def test_unlisted_origins_are_not_allowed() -> None:
    response = TestClient(app).options(
        "/v1/voice/intent",
        headers={"Origin": UNLISTED_ORIGIN, "Access-Control-Request-Method": "POST"},
    )

    assert response.headers.get("access-control-allow-origin") not in {
        UNLISTED_ORIGIN,
        "*",
    }


def test_native_requests_without_an_origin_are_unaffected() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers

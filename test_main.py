import pytest

from main import app
from sanic_testing.testing import SanicTestClient

test_client = SanicTestClient(app)


def test_get_root():
    _, response = test_client.get("/")
    assert response.json == {
        "statusText": "Root Endpoint of BG-Remove-API",
    }
    assert response.status_code == 200


@pytest.mark.parametrize(
    ["model_type", "rtype"],
    [("n", "file"), ("lw", "file"), ("n", "json"), ("lw", "json")],
)
def test_get_remove_correct(model_type: str, rtype: str):
    _, response = test_client.get(f"/remove/{model_type}?rtype={rtype}")
    assert response.json == {
        "statusText": f"Background Removal Endpoint (Return Type : {rtype})",
    }
    assert response.status_code == 200

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


# @pytest.mark.parametrize(
#     ["model_type", "rtype"],
#     [("n", "file"), ("lw", "file"), ("n", "json"), ("lw", "json")],
# )
# def test_get_remove_correct(model_type: str, rtype: str):
#     _, response = test_client.get(f"/remove/{model_type}?rtype={rtype}")
#     assert response.json == {
#         "statusText": f"Background Removal Endpoint (Return Type : {rtype})",
#     }
#     assert response.status_code == 200


# @pytest.mark.parametrize(
#     ["model_type", "rtype"],
#     [("no", "file"), ("li", "file"), ("normal", "json"), ("lweight", "json")],
# )
# def test_get_remove_incorrect_path(model_type: str, rtype: str):
#     _, response = test_client.get(f"/remove/{model_type}?rtype={rtype}")
#     assert response.json == {
#         "statusText":  "Invalid Model Type Specified. Only supports 'n' and 'lw'",
#     }
#     assert response.status_code == 400


# @pytest.mark.parametrize(
#     ["model_type", "rtype"],
#     [("n", "image"), ("lw", "image"), ("n", "jsn"), ("lw", "jsn")],
# )
# def test_get_remove_incorrect_query(model_type: str, rtype: str):
#     _, response = test_client.get(f"/remove/{model_type}?rtype={rtype}")
#     assert response.json == {
#         "statusText": "Invalid Return Type Specified",
#     }
#     assert response.status_code == 400


# @pytest.mark.parametrize(
#     ["model_type", "fill", "rtype"],
#     [("n", "164,5,99,255", "file"), ("lw", "127", "file"), ("n", "200, 0, 200, 255", "json"), ("lw", "164,5,99,255", "json")],
# )
# def test_get_replace_color_correct(model_type: str, fill: str, rtype: str):
#     _, response = test_client.get(f"/replace/color/{model_type}?fill={fill}&rtype={rtype}")
#     assert response.json == {
#         "statusText": f"Background Replacement Endpoint [Color] (Return Type : {rtype}, Color : {fill})",
#     }
#     assert response.status_code == 200


# @pytest.mark.parametrize(
#     ["model_type", "fill", "rtype"],
#     [("no", "164,5,99,255", "file"), ("li", "127", "file"), ("normal", "200, 0, 200, 255", "json"), ("lweight", "165,5,99,255", "json")],
# )
# def test_get_replace_incorrect_path(model_type: str, fill: str, rtype: str):
#     _, response = test_client.get(f"/replace/color/{model_type}?fill={fill}&rtype={rtype}")
#     assert response.json == {
#         "statusText":  "Invalid Model Type Specified. Only supports 'n' and 'lw'",
#     }
#     assert response.status_code == 400


# @pytest.mark.parametrize(
#     ["model_type", "fill", "rtype"],
#     [("n", "164,5,99,255", "image"), ("lw", "127", "img"), ("n", "200, 0, 200, 255", "jsn"), ("lw", "165,5,99,255", "js")],
# )
# def test_get_replace_incorrect_rtype(model_type: str, fill: str, rtype: str):
#     _, response = test_client.get(f"/replace/color/{model_type}?fill={fill}&rtype={rtype}")
#     assert response.json == {
#         "statusText":  "Invalid Return Type Specified",
#     }
#     assert response.status_code == 400


# @pytest.mark.parametrize(
#     ["model_type", "fill", "rtype"],
#     [("n", "164,5,99", "file"), ("lw", "127,127", "file"), ("n", "200, 0, 200", "json"), ("lw", "165,5", "json")],
# )
# def test_get_replace_incorrect_fill(model_type: str, fill: str, rtype: str):
#     _, response = test_client.get(f"/replace/color/{model_type}?fill={fill}&rtype={rtype}")
#     assert response.json == {
#         "statusText":  "Invalid Fill Format Type",
#     }
#     assert response.status_code == 400

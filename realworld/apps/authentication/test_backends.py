from datetime import datetime

from rest_framework.test import APITestCase, APIClient, APIRequestFactory

from realworld.apps.authentication.models import JwtUser
from realworld.apps.authentication.renderers import JwtUserJSONRenderer

EXPECTED_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6bnVsbC"
dt = datetime(2021, 1, 16, 13, 43, 39, 452056)
user = JwtUser(
    username='stelo',
    email='twinstae@gmail.com'
)
renderer = JwtUserJSONRenderer()
EXPECTED_JSON = '{"user": {"username": "stelo", "email": "twinstae@gmail.com", "token": ' \
+ '"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6bnVsbC"}}'


def test_json_renderer():
    rendered_json = renderer.render(data={
        "username": 'stelo',
        "email": 'twinstae@gmail.com',
        "token": EXPECTED_TOKEN
    })
    assert rendered_json == EXPECTED_JSON


def test_get_token():
    assert user.get_token(user.pk, dt)[:50] == EXPECTED_TOKEN[:50]

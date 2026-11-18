import time

import requests
from utils.constants import TIMEOUT

URL = "http://localhost:8000"


def get_token():
    r = requests.post(URL + "/api/auth/token", data={"username": "admin@eventflow.test", "password": "admin1234"}, timeout=TIMEOUT)
    return r.json()["access_token"]


def test_1():
    token = get_token()
    h = {"Authorization": "Bearer " + token}
    r = requests.post(URL + "/api/admin/promo", headers=h, json={"code": "TEST" + str(int(time.time())), "percent_off": 20, "max_uses": 5}, timeout=TIMEOUT)
    print(r.json())
    assert r.status_code == 201


def test_promo2():
    token = get_token()
    h = {"Authorization": "Bearer " + token}
    r = requests.get(URL + "/api/admin/promo", headers=h, timeout=TIMEOUT)
    promos = r.json()
    for p in promos:
        if p["code"] == "WELCOME10":
            assert p["percent_off"] == 10


def test_disable_promo():
    token = get_token()
    h = {"Authorization": "Bearer " + token}
    # try:
    r = requests.post(URL + "/api/admin/promo", headers=h, json={"code": "DIS" + str(int(time.time())), "percent_off": 5, "max_uses": 1}, timeout=TIMEOUT)
    id = r.json()["id"]
    r2 = requests.post(URL + "/api/admin/promo/" + str(id) + "/disable", headers=h, timeout=TIMEOUT)
    assert r2.json()["expires_at"] != None
    # except:
    #     pass


def test_client_cant_see_promos():
    r = requests.post(URL + "/api/auth/token", data={"username": "client@eventflow.test", "password": "client1234"}, timeout=TIMEOUT)
    token = r.json()["access_token"]
    r = requests.get(URL + "/api/admin/promo", headers={"Authorization": "Bearer " + token}, timeout=TIMEOUT)
    assert r.status_code == 403

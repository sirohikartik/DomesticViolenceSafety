import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

# generate unique user every run (avoids signup conflicts)
TEST_USER = {
    "username": f"kartik_{uuid.uuid4().hex[:6]}",
    "password": "password123",
    "email": f"kartik_{uuid.uuid4().hex[:6]}@test.com"
}


def print_result(name, res):
    print(f"\n==== {name} ====")
    print("Status:", res.status_code)
    try:
        print("Response:", res.json())
    except:
        print("Response:", res.text)


# ------------------ SIGNUP ------------------

def test_signup():
    res = requests.post(f"{BASE_URL}/auth/signup", json=TEST_USER)
    print_result("SIGNUP", res)
    assert res.status_code == 200
    return res.json()


def test_duplicate_signup():
    res = requests.post(f"{BASE_URL}/auth/signup", json=TEST_USER)
    print_result("DUPLICATE SIGNUP", res)
    assert res.status_code == 400


# ------------------ LOGIN ------------------

def test_login():
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    })
    print_result("LOGIN", res)
    assert res.status_code == 200

    data = res.json()
    return data["access_token"], data["refresh_token"]


def test_wrong_password():
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "username": TEST_USER["username"],
        "password": "wrongpassword"
    })
    print_result("WRONG PASSWORD", res)
    assert res.status_code == 401


def test_nonexistent_user():
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "ghost_user",
        "password": "password"
    })
    print_result("NON EXISTENT USER", res)
    assert res.status_code == 404


# ------------------ REFRESH ------------------

def test_refresh(refresh_token):
    res = requests.post(f"{BASE_URL}/auth/refresh", json={
        "refresh_token": refresh_token
    })
    print_result("REFRESH", res)

    if res.status_code == 200:
        data = res.json()
        return data["access_token"], data["refresh_token"]
    return None, None


def test_invalid_refresh():
    res = requests.post(f"{BASE_URL}/auth/refresh", json={
        "refresh_token": "invalid.token.value"
    })
    print_result("INVALID REFRESH TOKEN", res)
    assert res.status_code == 401


def test_access_token_as_refresh(access_token):
    res = requests.post(f"{BASE_URL}/auth/refresh", json={
        "refresh_token": access_token
    })
    print_result("ACCESS TOKEN USED AS REFRESH", res)
    assert res.status_code == 401


# ------------------ LOGOUT ------------------

def test_logout(refresh_token):
    res = requests.post(f"{BASE_URL}/auth/logout", json={
        "refresh_token": refresh_token
    })
    print_result("LOGOUT", res)
    assert res.status_code == 200


# ------------------ MAIN FLOW ------------------

if __name__ == "__main__":
    print("\n🚀 STARTING COMPREHENSIVE AUTH TEST\n")

    # ---- Signup ----
    signup_data = test_signup()
    test_duplicate_signup()

    # ---- Login ----
    access_token, refresh_token = test_login()
    test_wrong_password()
    test_nonexistent_user()

    # ---- Refresh Valid ----
    new_access, new_refresh = test_refresh(refresh_token)
    assert new_refresh is not None

    # ---- Reuse Old Token (should fail) ----
    print("\n🚨 TEST: reuse old refresh token")
    res = requests.post(f"{BASE_URL}/auth/refresh", json={
        "refresh_token": refresh_token
    })
    print_result("REUSE OLD REFRESH", res)
    assert res.status_code == 401

    # ---- Use New Token (should work) ----
    print("\n✅ TEST: use new refresh token")
    latest_access, latest_refresh = test_refresh(new_refresh)
    assert latest_refresh is not None

    # ---- Invalid Token ----
    test_invalid_refresh()

    # ---- Using access token as refresh ----
    test_access_token_as_refresh(access_token)

    # ---- Logout ----
    test_logout(latest_refresh)

    # ---- Refresh after logout (should fail) ----
    print("\n🚨 TEST: refresh after logout")
    res = requests.post(f"{BASE_URL}/auth/refresh", json={
        "refresh_token": latest_refresh
    })
    print_result("POST LOGOUT REFRESH", res)
    assert res.status_code == 401

    print("\n🎯 ALL TESTS PASSED SUCCESSFULLY\n")

# test_customer.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_customer_flow():
    print("\n========== CUSTOMER TEST ==========\n")

    # ------------------ SIGNUP ------------------
    print("[Signup]")
    res = requests.post(f"{BASE_URL}/auth/signup", json={
        "username": "cust_test",
        "password": "pass123",
        "email": "cust@test.com",
        "role": "customer"
    })
    print(res.status_code, res.text)

    # ------------------ LOGIN ------------------
    print("\n[Login]")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "cust_test",
        "password": "pass123"
    })
    print(res.status_code, res.text)

    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ------------------ GET PROFILE ------------------
    print("\n[Get Profile]")
    res = requests.get(f"{BASE_URL}/customer/me", headers=headers)
    print(res.status_code, res.text)

    # ------------------ UPDATE PROFILE ------------------
    print("\n[Update Profile]")
    res = requests.put(
        f"{BASE_URL}/customer/me",
        json={"phone": "9999999999", "address": "Punjab"},
        headers=headers
    )
    print(res.status_code, res.text)

    # ------------------ ANALYZE TEXT ------------------
    print("\n[Analyze Text]")
    res = requests.post(
        f"{BASE_URL}/customer/analyze",
        json={"text": "he tried to hit me"},
        headers=headers
    )
    print(res.status_code, res.text)

    # ------------------ CREATE INCIDENT ------------------
    print("\n[Create Alert]")
    res = requests.post(
        f"{BASE_URL}/customer/alert",
        headers=headers
    )
    print(res.status_code, res.text)

    print("\n========== DONE ==========\n")


if __name__ == "__main__":
    test_customer_flow()

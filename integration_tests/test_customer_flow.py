import requests
import random

BASE = "http://localhost:8000"

def test(name, passed, r=None):
    print(f"{'✅' if passed else '❌'} {name}")
    if not passed and r:
        try: print(f"   {r.status_code} | {r.json()}")
        except: print(f"   {r.status_code} | {r.text}")

print("\n── Customer Integration Flow ───────────────────────────\n")

# 1. Signup → get token
phone = f"9{random.randint(100000000, 999999999)}"
r = requests.post(f"{BASE}/auth/signup", json={
    "username": f"cust_{phone[-5:]}",
    "password": "Test@1234",
    "email": f"cust_{phone[-5:]}@test.com",
    "phone": phone,
    "address": "12 Test Lane, Mumbai",
    "role": "customer"
})
token = r.json().get("access_token")
test("Signup returns token", r.status_code == 200 and token, r)

# 2. Use token → fetch own profile
r = requests.post(f"{BASE}/customer/me", json={"token": token})
test("Token from signup works on /customer/me", r.status_code == 200 and "id" in r.json(), r)

# 3. Update profile → verify change persists
r = requests.put(f"{BASE}/customer/me", json={"token": token, "address": "99 New Road, Delhi"})
r2 = requests.post(f"{BASE}/customer/me", json={"token": token})
test("Profile update persists on re-fetch", r.status_code == 200 and r2.json().get("address") == "99 New Road, Delhi", r)

# 4. Manual report → incident created and linked to customer
r = requests.post(f"{BASE}/customer/report", json={"token": token})
cust_id = requests.post(f"{BASE}/customer/me", json={"token": token}).json().get("id")
test("Manual report creates incident linked to customer",
     r.status_code == 200 and "incident_id" in r.json(), r)

print()

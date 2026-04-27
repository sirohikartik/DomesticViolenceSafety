import requests
import random

BASE = "http://localhost:8000"

def test(name, passed, r=None):
    print(f"{'✅' if passed else '❌'} {name}")
    if not passed and r:
        try: print(f"   {r.status_code} | {r.json()}")
        except: print(f"   {r.status_code} | {r.text}")

print("\n── Admin Integration Flow ──────────────────────────────\n")

# Setup: create customer + officer + incident
ph_c = f"85{random.randint(10000000, 99999999)}"
cust_token = requests.post(f"{BASE}/auth/signup", json={
    "username": f"ac_{ph_c[-5:]}", "password": "Test@1234",
    "email": f"ac_{ph_c[-5:]}@test.com", "phone": ph_c,
    "address": "1 Admin Test Road", "role": "customer"
}).json().get("access_token")

ph_o = f"84{random.randint(10000000, 99999999)}"
off_token = requests.post(f"{BASE}/auth/signup", json={
    "username": f"ao_{ph_o[-5:]}", "password": "Off@5678",
    "email": f"ao_{ph_o[-5:]}@pd.gov", "phone": ph_o,
    "address": "Precinct Admin", "role": "officer",
    "badge_num": f"ADM{random.randint(10,99)}", "dept": "Admin Test"
}).json().get("access_token")

incident_id = requests.post(f"{BASE}/customer/report", json={"token": cust_token}).json().get("incident_id")
officer_id  = requests.post(f"{BASE}/officer/me",      json={"token": off_token}).json().get("id")
customer_id = requests.post(f"{BASE}/customer/me",     json={"token": cust_token}).json().get("id")

admin_token = requests.post(f"{BASE}/admin/login", json={"username": "admin", "password": "1234"}).json().get("access_token")

# 1. Admin can see the customer that just signed up
r = requests.post(f"{BASE}/admin/customers", json={"token": admin_token})
ids = [c["id"] for c in r.json()] if r.status_code == 200 else []
test("Newly signed-up customer visible to admin", customer_id in ids, r)

# 2. Admin assigns officer to incident → verify officer_id updated
r = requests.put(f"{BASE}/admin/incidents", json={
    "token": admin_token, "incident_id": incident_id, "officer_id": officer_id
})
test("Admin can assign officer to incident",
     r.status_code == 200 and r.json().get("officer_id") == officer_id, r)

# 3. After admin assigns, incident appears in officer's list
r = requests.post(f"{BASE}/officer/incidents", json={"token": off_token})
my_ids = [i["id"] for i in r.json()] if r.status_code == 200 else []
test("Admin-assigned incident appears in officer's list", incident_id in my_ids, r)

# 4. Admin resolves incident → status reflects across the board
r = requests.put(f"{BASE}/admin/incidents", json={
    "token": admin_token, "incident_id": incident_id, "status": "resolved"
})
r2 = requests.post(f"{BASE}/admin/incidents", json={"token": admin_token})
resolved = next((i for i in r2.json() if i["id"] == incident_id), None)
test("Admin-resolved status persists on re-fetch",
     resolved and resolved.get("status") == "resolved", r)

print()

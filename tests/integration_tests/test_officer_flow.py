import requests
import random

BASE = "http://localhost:8000"

def test(name, passed, r=None):
    print(f"{'✅' if passed else '❌'} {name}")
    if not passed and r:
        try: print(f"   {r.status_code} | {r.json()}")
        except: print(f"   {r.status_code} | {r.text}")

print("\n── Officer Integration Flow ────────────────────────────\n")

# Setup: create a customer and file a report to generate an incident
ph_c = f"7{random.randint(100000000, 999999999)}"
r = requests.post(f"{BASE}/auth/signup", json={
    "username": f"cust_{ph_c[-5:]}",
    "password": "Test@1234",
    "email": f"cust_{ph_c[-5:]}@test.com",
    "phone": ph_c,
    "address": "5 Incident Street, Chennai",
    "role": "customer"
})
cust_token = r.json().get("access_token")
incident_id = requests.post(f"{BASE}/customer/report", json={"token": cust_token}).json().get("incident_id")

# Signup as officer
ph_o = f"6{random.randint(100000000, 999999999)}"
r = requests.post(f"{BASE}/auth/signup", json={
    "username": f"off_{ph_o[-5:]}",
    "password": "Off@5678",
    "email": f"off_{ph_o[-5:]}@pd.gov",
    "phone": ph_o,
    "address": "Precinct 7, Chennai",
    "role": "officer",
    "badge_num": f"B{random.randint(100,999)}",
    "dept": "Patrol"
})
off_token = r.json().get("access_token")

# 1. Officer login → profile accessible
r = requests.post(f"{BASE}/officer/me", json={"token": off_token})
test("Officer token works on /officer/me", r.status_code == 200 and "id" in r.json(), r)

# 2. Unassigned incident visible to officer
r = requests.post(f"{BASE}/officer/incidents/all", json={"token": off_token})
ids = [i["id"] for i in r.json()] if r.status_code == 200 else []
test("Customer's incident visible in officer unassigned list", incident_id in ids, r)

# 3. Officer accepts incident → status becomes assigned
r = requests.post(f"{BASE}/officer/incidents/accept", json={"token": off_token, "incident_id": incident_id})
test("Officer can accept incident", r.status_code == 200 and r.json().get("status") == "assigned", r)

# 4. Accepted incident appears in officer's own list
r = requests.post(f"{BASE}/officer/incidents", json={"token": off_token})
my_ids = [i["id"] for i in r.json()] if r.status_code == 200 else []
test("Accepted incident appears in officer's assigned list", incident_id in my_ids, r)

print()

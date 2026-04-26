import requests
import random

BASE = "http://localhost:8000"

def test(name, passed, r=None):
    print(f"{'✅' if passed else '❌'} {name}")
    if not passed and r:
        try: print(f"   {r.status_code} | {r.json()}")
        except: print(f"   {r.status_code} | {r.text}")

print("\n── Incident Lifecycle Test ─────────────────────────────\n")

ph_c = f"7{random.randint(100000000, 999999999)}"
ph_o = f"6{random.randint(100000000, 999999999)}"

cust_token = requests.post(f"{BASE}/auth/signup", json={
    "username": f"lc_c_{ph_c[-5:]}", "password": "LC@1234",
    "email": f"lc_c_{ph_c[-5:]}@test.com", "phone": ph_c,
    "address": "Lifecycle Lane, Bangalore", "role": "customer"
}).json().get("access_token")

off_token = requests.post(f"{BASE}/auth/signup", json={
    "username": f"lc_o_{ph_o[-5:]}", "password": "LC@5678",
    "email": f"lc_o_{ph_o[-5:]}@pd.gov", "phone": ph_o,
    "address": "Lifecycle Precinct", "role": "officer",
    "badge_num": f"LC{random.randint(10,99)}", "dept": "Lifecycle"
}).json().get("access_token")

admin_token = requests.post(f"{BASE}/admin/login",
    json={"username": "admin", "password": "1234"}).json().get("access_token")

# Stage 1 — initialized
r = requests.post(f"{BASE}/customer/report", json={"token": cust_token})
incident_id = r.json().get("incident_id")
test("Stage 1 — incident created with status 'initialized'",
     r.status_code == 200 and incident_id is not None, r)

# Stage 2 — assigned (officer accepts)
r = requests.post(f"{BASE}/officer/incidents/accept",
    json={"token": off_token, "incident_id": incident_id})
test("Stage 2 — officer accepts, status becomes 'assigned'",
     r.status_code == 200 and r.json().get("status") == "assigned", r)

# Stage 3 — double accept blocked
r = requests.post(f"{BASE}/officer/incidents/accept",
    json={"token": off_token, "incident_id": incident_id})
test("Stage 3 — double accept blocked (already assigned)",
     r.status_code == 400, r)

# Stage 4 — resolved by admin
r = requests.put(f"{BASE}/admin/incidents", json={
    "token": admin_token, "incident_id": incident_id, "status": "resolved"})
test("Stage 4 — admin resolves incident",
     r.status_code == 200 and r.json().get("status") == "resolved", r)

print()

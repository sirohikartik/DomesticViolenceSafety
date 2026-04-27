import requests
import random

BASE = "http://localhost:8000"

def test(name, passed, r=None):
    print(f"{'✅' if passed else '❌'} {name}")
    if not passed and r:
        try: print(f"   {r.status_code} | {r.json()}")
        except: print(f"   {r.status_code} | {r.text}")

print("\n── Full System Test ────────────────────────────────────\n")

ph_c = f"9{random.randint(100000000, 999999999)}"
ph_o = f"8{random.randint(100000000, 999999999)}"

# 1. All three roles can sign up and log in
cust_token = requests.post(f"{BASE}/auth/signup", json={
    "username": f"sys_c_{ph_c[-5:]}", "password": "Sys@1234",
    "email": f"sys_c_{ph_c[-5:]}@test.com", "phone": ph_c,
    "address": "System Test Street", "role": "customer"
}).json().get("access_token")

off_token = requests.post(f"{BASE}/auth/signup", json={
    "username": f"sys_o_{ph_o[-5:]}", "password": "Sys@5678",
    "email": f"sys_o_{ph_o[-5:]}@pd.gov", "phone": ph_o,
    "address": "System Precinct", "role": "officer",
    "badge_num": f"SYS{random.randint(10,99)}", "dept": "System"
}).json().get("access_token")

admin_token = requests.post(f"{BASE}/admin/login",
    json={"username": "admin", "password": "1234"}).json().get("access_token")

test("All three roles authenticated",
     all([cust_token, off_token, admin_token]))

# 2. Customer files report → admin sees it
incident_id = requests.post(f"{BASE}/customer/report",
    json={"token": cust_token}).json().get("incident_id")
incidents = requests.post(f"{BASE}/admin/incidents",
    json={"token": admin_token}).json()
test("Customer report visible to admin",
     isinstance(incidents, list) and any(i["id"] == incident_id for i in incidents))

# 3. Officer accepts → customer's incident now has officer assigned
off_id = requests.post(f"{BASE}/officer/me", json={"token": off_token}).json().get("id")
requests.post(f"{BASE}/officer/incidents/accept",
    json={"token": off_token, "incident_id": incident_id})
incidents = requests.post(f"{BASE}/admin/incidents", json={"token": admin_token}).json()
matched = next((i for i in incidents if i["id"] == incident_id), None)
test("Officer acceptance reflected in admin view",
     matched and matched.get("officer_id") == off_id)

# 4. Admin resolves → status final across system
requests.put(f"{BASE}/admin/incidents", json={
    "token": admin_token, "incident_id": incident_id, "status": "resolved"})
incidents = requests.post(f"{BASE}/admin/incidents", json={"token": admin_token}).json()
final = next((i for i in incidents if i["id"] == incident_id), None)
test("Admin resolution is final system state",
     final and final.get("status") == "resolved")

print()

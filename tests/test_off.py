import requests
import random
import string

BASE_URL = "http://localhost:8000"
OFFICER_URL = f"{BASE_URL}/officer"
AUTH_URL = f"{BASE_URL}/auth"
CUSTOMER_URL = f"{BASE_URL}/customer"

def print_result(test_name, passed, response=None, note=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if note:
        print(f"       Note: {note}")
    if not passed and response is not None:
        try:
            print(f"       Status: {response.status_code} | Body: {response.json()}")
        except:
            print(f"       Status: {response.status_code} | Body: {response.text}")
    print()

# ─── Setup: Login ─────────────────────────────────────────────────────────────

print("=" * 55)
print("  OFFICER ROUTE TEST SUITE")
print("=" * 55)
print()
print("── SETUP: LOGIN ────────────────────────────────────────")
print()

# Change these to an officer that already exists in your DB
OFFICER_USERNAME = "officer"
OFFICER_PASSWORD = "officer"

# Also need a customer token to create incidents to test against
CUSTOMER_USERNAME = "string"
CUSTOMER_PASSWORD = "string"

# Officer login
r = requests.post(f"{AUTH_URL}/login", json={
    "username": OFFICER_USERNAME,
    "password": OFFICER_PASSWORD
})
if r.status_code != 200 or "access_token" not in r.json():
    print(f"❌ Officer login failed — cannot proceed. Response: {r.json()}")
    exit(1)

OFFICER_TOKEN = r.json()["access_token"]
print(f"✅ Logged in as officer '{OFFICER_USERNAME}'")
print(f"   Token prefix: {OFFICER_TOKEN[:30]}...")
print()

# Customer login (to create a test incident)
r = requests.post(f"{AUTH_URL}/login", json={
    "username": CUSTOMER_USERNAME,
    "password": CUSTOMER_PASSWORD
})
if r.status_code != 200 or "access_token" not in r.json():
    print(f"⚠️  Customer login failed — accept incident test will be skipped")
    CUSTOMER_TOKEN = None
else:
    CUSTOMER_TOKEN = r.json()["access_token"]
    print(f"✅ Logged in as customer '{CUSTOMER_USERNAME}' (for creating test incident)")
    print()

# ─── GET /me ──────────────────────────────────────────────────────────────────

print("── POST /me ────────────────────────────────────────────")
print()

# 1. Valid token
r = requests.post(f"{OFFICER_URL}/me", json={"token": OFFICER_TOKEN})
passed = r.status_code == 200 and "id" in r.json() and "password" not in r.json()
print_result("Fetch officer details", passed, r)
if passed:
    print(f"       Officer: {r.json()}")
    print()

# 2. Customer token on officer route
if CUSTOMER_TOKEN:
    r = requests.post(f"{OFFICER_URL}/me", json={"token": CUSTOMER_TOKEN})
    passed = r.status_code == 403
    print_result("Customer token rejected on officer route", passed, r,
                 note="Expects 403 Incorrect route")

# 3. Invalid token
r = requests.post(f"{OFFICER_URL}/me", json={"token": "badtoken"})
passed = r.status_code == 401
print_result("Invalid token rejected", passed, r)

# ─── PUT /me ──────────────────────────────────────────────────────────────────

print("── PUT /me ─────────────────────────────────────────────")
print()

suffix = ''.join(random.choices(string.digits, k=4))

# 4. Update location
r = requests.put(f"{OFFICER_URL}/me", json={
    "token": OFFICER_TOKEN,
    "location": f"Precinct {suffix}, Downtown"
})
passed = r.status_code == 200 and r.json().get("location") == f"Precinct {suffix}, Downtown"
print_result("Update location", passed, r)

# 5. Update department
r = requests.put(f"{OFFICER_URL}/me", json={
    "token": OFFICER_TOKEN,
    "department": "Cybercrime"
})
passed = r.status_code == 200 and r.json().get("department") == "Cybercrime"
print_result("Update department", passed, r)

# 6. Update with invalid token
r = requests.put(f"{OFFICER_URL}/me", json={
    "token": "faketoken",
    "location": "Hacker Lane"
})
passed = r.status_code == 401
print_result("Update with invalid token rejected", passed, r)

# ─── Create a test incident via customer ──────────────────────────────────────

INCIDENT_ID = None
if CUSTOMER_TOKEN:
    r = requests.post(f"{CUSTOMER_URL}/report", json={"token": CUSTOMER_TOKEN})
    if r.status_code == 200 and "incident_id" in r.json():
        INCIDENT_ID = r.json()["incident_id"]
        print(f"── TEST INCIDENT CREATED (ID: {INCIDENT_ID}) ──────────────")
        print()

# ─── GET /incidents/all ───────────────────────────────────────────────────────

print("── POST /incidents/all ─────────────────────────────────")
print()

# 7. Get all unassigned incidents
r = requests.post(f"{OFFICER_URL}/incidents/all", json={"token": OFFICER_TOKEN})
passed = r.status_code == 200 and isinstance(r.json(), list)
print_result("Fetch all unassigned incidents", passed, r,
             note=f"Found {len(r.json())} unassigned incidents" if passed else "")

# 8. Invalid token
r = requests.post(f"{OFFICER_URL}/incidents/all", json={"token": "badtoken"})
passed = r.status_code == 401
print_result("Invalid token rejected on /incidents/all", passed, r)

# ─── POST /incidents/accept ───────────────────────────────────────────────────

print("── POST /incidents/accept ──────────────────────────────")
print()

if INCIDENT_ID:
    # 9. Accept a valid incident
    r = requests.post(f"{OFFICER_URL}/incidents/accept", json={
        "token": OFFICER_TOKEN,
        "incident_id": INCIDENT_ID
    })
    passed = r.status_code == 200 and r.json().get("status") == "assigned"
    print_result("Accept incident", passed, r,
                 note=f"Incident {INCIDENT_ID} should now be assigned")

    # 10. Try to accept the same incident again
    r = requests.post(f"{OFFICER_URL}/incidents/accept", json={
        "token": OFFICER_TOKEN,
        "incident_id": INCIDENT_ID
    })
    passed = r.status_code == 400
    print_result("Double-accept rejected", passed, r,
                 note="Expects 400 already assigned")
else:
    print("⚠️  Skipping accept tests — no test incident available")
    print()

# 11. Accept non-existent incident
r = requests.post(f"{OFFICER_URL}/incidents/accept", json={
    "token": OFFICER_TOKEN,
    "incident_id": 999999
})
passed = r.status_code == 404
print_result("Accept non-existent incident rejected", passed, r,
             note="Expects 404 Incident not found")

# ─── GET /incidents (my assigned incidents) ───────────────────────────────────

print("── POST /incidents ─────────────────────────────────────")
print()

# 12. Get this officer's assigned incidents
r = requests.post(f"{OFFICER_URL}/incidents", json={"token": OFFICER_TOKEN})
passed = r.status_code == 200 and isinstance(r.json(), list)
print_result("Fetch my assigned incidents", passed, r,
             note=f"Found {len(r.json())} assigned incidents" if passed else "")
if passed and INCIDENT_ID:
    ids = [i["id"] for i in r.json()]
    accepted = INCIDENT_ID in ids
    print_result("Accepted incident appears in my list", accepted,
                 note=f"Looking for incident {INCIDENT_ID} in {ids}")

# 13. Invalid token
r = requests.post(f"{OFFICER_URL}/incidents", json={"token": "badtoken"})
passed = r.status_code == 401
print_result("Invalid token rejected on /incidents", passed, r)


print("── POST /incidents/nearby ─────────────────────────────")
print()

# 14. Get nearby incidents (basic test)
r = requests.post(f"{OFFICER_URL}/incidents/nearby", json={
    "token": OFFICER_TOKEN,
    "radius_km": 10
})

passed = r.status_code == 200 and isinstance(r.json(), list)

print_result("Fetch nearby incidents", passed, r,
             note=f"Found {len(r.json())} nearby incidents" if passed else "")


# 15. Invalid token
r = requests.post(f"{OFFICER_URL}/incidents/nearby", json={
    "token": "badtoken",
    "radius_km": 10
})

passed = r.status_code == 401
print_result("Invalid token rejected on /incidents/nearby", passed, r)


# 16. Missing officer location (edge case)
# First clear location
requests.put(f"{OFFICER_URL}/me", json={
    "token": OFFICER_TOKEN,
    "location": None
})

r = requests.post(f"{OFFICER_URL}/incidents/nearby", json={
    "token": OFFICER_TOKEN,
    "radius_km": 10
})

passed = r.status_code == 400
print_result("Nearby incidents fails without officer location", passed, r,
             note="Expects 400 Officer location not set")

print("=" * 55)
print("  Done.")
print("=" * 55)

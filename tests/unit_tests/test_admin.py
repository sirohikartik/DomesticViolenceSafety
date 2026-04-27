import requests
import random
import string

BASE_URL = "http://localhost:8000"
ADMIN_URL = f"{BASE_URL}/admin"
AUTH_URL  = f"{BASE_URL}/auth"

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

def suffix(n=5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

# ─── Setup ────────────────────────────────────────────────────────────────────

print("=" * 55)
print("  ADMIN ROUTE TEST SUITE")
print("=" * 55)
print()
print("── SETUP ───────────────────────────────────────────────")
print()

ADMIN_TOKEN = None
CUSTOMER_TOKEN = None
OFFICER_TOKEN  = None

# ─── Admin Login ──────────────────────────────────────────────────────────────

print("── POST /admin/login ───────────────────────────────────")
print()

# 1. Valid login
r = requests.post(f"{ADMIN_URL}/login", json={"username": "admin", "password": "1234"})
passed = r.status_code == 200 and "access_token" in r.json()
print_result("Valid admin login", passed, r)
if passed:
    ADMIN_TOKEN = r.json()["access_token"]
    print(f"       Token prefix: {ADMIN_TOKEN[:30]}...")
    print()

# 2. Wrong password
r = requests.post(f"{ADMIN_URL}/login", json={"username": "admin", "password": "wrongpass"})
passed = r.status_code == 401
print_result("Wrong password rejected", passed, r, note="Expects 401")

# 3. Wrong username
r = requests.post(f"{ADMIN_URL}/login", json={"username": "notadmin", "password": "1234"})
passed = r.status_code == 401
print_result("Wrong username rejected", passed, r, note="Expects 401")

# 4. Missing fields
r = requests.post(f"{ADMIN_URL}/login", json={"username": "admin"})
passed = r.status_code == 422
print_result("Missing password field rejected", passed, r, note="Expects 422")

if not ADMIN_TOKEN:
    print("❌ Cannot proceed — admin login failed.")
    exit(1)

# ─── Setup: create a customer and officer to work with ────────────────────────

s = suffix()
CUSTOMER_USERNAME = f"testcust_{s}"
OFFICER_USERNAME  = f"testofficer_{s}"

r = requests.post(f"{AUTH_URL}/signup", json={
    "username": CUSTOMER_USERNAME,
    "password": "TestPass@123",
    "email": f"{CUSTOMER_USERNAME}@test.com",
    "phone": f"9{random.randint(100000000,999999999)}",
    "address": "123 Test Street, Testville",
    "role": "customer"
})
CUSTOMER_ID = None
if r.status_code == 200:
    CUSTOMER_TOKEN = r.json().get("access_token")
    # fetch customer id via /customer/me
    me = requests.post(f"{BASE_URL}/customer/me", json={"token": CUSTOMER_TOKEN})
    if me.status_code == 200:
        CUSTOMER_ID = me.json().get("id")
print(f"{'✅' if CUSTOMER_ID else '❌'} Test customer created (ID: {CUSTOMER_ID})")

r = requests.post(f"{AUTH_URL}/signup", json={
    "username": OFFICER_USERNAME,
    "password": "TestOff@456",
    "email": f"{OFFICER_USERNAME}@pd.gov",
    "phone": f"8{random.randint(100000000,999999999)}",
    "address": "Precinct 99, Testville",
    "role": "officer",
    "badge_num": f"B-{random.randint(1000,9999)}",
    "dept": "Testing"
})
OFFICER_ID = None
if r.status_code == 200:
    OFFICER_TOKEN = r.json().get("access_token")
    me = requests.post(f"{BASE_URL}/officer/me", json={"token": OFFICER_TOKEN})
    if me.status_code == 200:
        OFFICER_ID = me.json().get("id")
print(f"{'✅' if OFFICER_ID else '❌'} Test officer created (ID: {OFFICER_ID})")

# create a test incident via customer manual report
INCIDENT_ID = None
if CUSTOMER_TOKEN:
    r = requests.post(f"{BASE_URL}/customer/report", json={"token": CUSTOMER_TOKEN})
    if r.status_code == 200:
        INCIDENT_ID = r.json().get("incident_id")
print(f"{'✅' if INCIDENT_ID else '❌'} Test incident created (ID: {INCIDENT_ID})")
print()

# ─── GET /admin/customers ─────────────────────────────────────────────────────

print("── POST /admin/customers ───────────────────────────────")
print()

# 5. Valid
r = requests.post(f"{ADMIN_URL}/customers", json={"token": ADMIN_TOKEN})
passed = r.status_code == 200 and isinstance(r.json(), list)
print_result("Fetch all customers", passed, r,
             note=f"Found {len(r.json())} customers" if passed else "")

# 6. No passwords exposed
if passed:
    has_pw = any("password" in c for c in r.json())
    print_result("No passwords in customer list", not has_pw,
                 note="Passwords must be stripped from response")

# 7. Non-admin token rejected
if CUSTOMER_TOKEN:
    r = requests.post(f"{ADMIN_URL}/customers", json={"token": CUSTOMER_TOKEN})
    passed = r.status_code == 403
    print_result("Non-admin token rejected on /customers", passed, r, note="Expects 403")

# 8. Invalid token
r = requests.post(f"{ADMIN_URL}/customers", json={"token": "faketoken"})
passed = r.status_code == 401
print_result("Invalid token rejected on /customers", passed, r, note="Expects 401")

# ─── PUT /admin/customers ─────────────────────────────────────────────────────

print("── PUT /admin/customers ────────────────────────────────")
print()

if CUSTOMER_ID:
    # 9. Valid update
    r = requests.put(f"{ADMIN_URL}/customers", json={
        "token": ADMIN_TOKEN,
        "customer_id": CUSTOMER_ID,
        "address": "999 Updated Ave, Newcity"
    })
    passed = r.status_code == 200 and r.json().get("address") == "999 Updated Ave, Newcity"
    print_result("Update customer address", passed, r)

    # 10. Update non-existent customer
    r = requests.put(f"{ADMIN_URL}/customers", json={
        "token": ADMIN_TOKEN,
        "customer_id": 999999,
        "address": "Ghost Street"
    })
    passed = r.status_code == 404
    print_result("Update non-existent customer rejected", passed, r, note="Expects 404")

# 11. Non-admin token
r = requests.put(f"{ADMIN_URL}/customers", json={
    "token": "badtoken",
    "customer_id": 1,
    "address": "Hacker Lane"
})
passed = r.status_code == 401
print_result("Invalid token rejected on PUT /customers", passed, r, note="Expects 401")

# ─── GET /admin/officers ──────────────────────────────────────────────────────

print("── POST /admin/officers ────────────────────────────────")
print()

# 12. Valid
r = requests.post(f"{ADMIN_URL}/officers", json={"token": ADMIN_TOKEN})
passed = r.status_code == 200 and isinstance(r.json(), list)
print_result("Fetch all officers", passed, r,
             note=f"Found {len(r.json())} officers" if passed else "")

# 13. No passwords exposed
if passed:
    has_pw = any("password" in o for o in r.json())
    print_result("No passwords in officer list", not has_pw,
                 note="Passwords must be stripped from response")

# 14. Invalid token
r = requests.post(f"{ADMIN_URL}/officers", json={"token": "faketoken"})
passed = r.status_code == 401
print_result("Invalid token rejected on /officers", passed, r, note="Expects 401")

# ─── PUT /admin/officers ──────────────────────────────────────────────────────

print("── PUT /admin/officers ─────────────────────────────────")
print()

if OFFICER_ID:
    # 15. Valid update
    r = requests.put(f"{ADMIN_URL}/officers", json={
        "token": ADMIN_TOKEN,
        "officer_id": OFFICER_ID,
        "department": "Homicide"
    })
    passed = r.status_code == 200 and r.json().get("department") == "Homicide"
    print_result("Update officer department", passed, r)

    # 16. Update location
    r = requests.put(f"{ADMIN_URL}/officers", json={
        "token": ADMIN_TOKEN,
        "officer_id": OFFICER_ID,
        "location": "Precinct 1, Downtown"
    })
    passed = r.status_code == 200 and r.json().get("location") == "Precinct 1, Downtown"
    print_result("Update officer location", passed, r)

    # 17. Non-existent officer
    r = requests.put(f"{ADMIN_URL}/officers", json={
        "token": ADMIN_TOKEN,
        "officer_id": 999999,
        "department": "Ghost Dept"
    })
    passed = r.status_code == 404
    print_result("Update non-existent officer rejected", passed, r, note="Expects 404")

# 18. Invalid token
r = requests.put(f"{ADMIN_URL}/officers", json={
    "token": "badtoken",
    "officer_id": 1,
    "department": "Hackers"
})
passed = r.status_code == 401
print_result("Invalid token rejected on PUT /officers", passed, r, note="Expects 401")

# ─── GET /admin/incidents ─────────────────────────────────────────────────────

print("── POST /admin/incidents ───────────────────────────────")
print()

# 19. Valid
r = requests.post(f"{ADMIN_URL}/incidents", json={"token": ADMIN_TOKEN})
passed = r.status_code == 200 and isinstance(r.json(), list)
print_result("Fetch all incidents", passed, r,
             note=f"Found {len(r.json())} incidents" if passed else "")

# 20. Invalid token
r = requests.post(f"{ADMIN_URL}/incidents", json={"token": "faketoken"})
passed = r.status_code == 401
print_result("Invalid token rejected on /incidents", passed, r, note="Expects 401")

# ─── PUT /admin/incidents ─────────────────────────────────────────────────────

print("── PUT /admin/incidents ────────────────────────────────")
print()

if INCIDENT_ID:
    # 21. Update status
    r = requests.put(f"{ADMIN_URL}/incidents", json={
        "token": ADMIN_TOKEN,
        "incident_id": INCIDENT_ID,
        "status": "assigned"
    })
    passed = r.status_code == 200 and r.json().get("status") == "assigned"
    print_result("Update incident status", passed, r)

    # 22. Assign officer
    if OFFICER_ID:
        r = requests.put(f"{ADMIN_URL}/incidents", json={
            "token": ADMIN_TOKEN,
            "incident_id": INCIDENT_ID,
            "officer_id": OFFICER_ID
        })
        passed = r.status_code == 200 and r.json().get("officer_id") == OFFICER_ID
        print_result("Assign officer to incident", passed, r)

    # 23. Update description and location
    r = requests.put(f"{ADMIN_URL}/incidents", json={
        "token": ADMIN_TOKEN,
        "incident_id": INCIDENT_ID,
        "description": "Admin updated description",
        "location": "Admin Updated Location"
    })
    passed = r.status_code == 200 and r.json().get("description") == "Admin updated description"
    print_result("Update incident description and location", passed, r)

    # 24. Assign non-existent officer
    r = requests.put(f"{ADMIN_URL}/incidents", json={
        "token": ADMIN_TOKEN,
        "incident_id": INCIDENT_ID,
        "officer_id": 999999
    })
    passed = r.status_code == 404
    print_result("Assign non-existent officer rejected", passed, r, note="Expects 404")

# 25. Update non-existent incident
r = requests.put(f"{ADMIN_URL}/incidents", json={
    "token": ADMIN_TOKEN,
    "incident_id": 999999,
    "status": "resolved"
})
passed = r.status_code == 404
print_result("Update non-existent incident rejected", passed, r, note="Expects 404")

# 26. Invalid token
r = requests.put(f"{ADMIN_URL}/incidents", json={
    "token": "badtoken",
    "incident_id": 1,
    "status": "resolved"
})
passed = r.status_code == 401
print_result("Invalid token rejected on PUT /incidents", passed, r, note="Expects 401")

print("=" * 55)
print("  Done.")
print("=" * 55)

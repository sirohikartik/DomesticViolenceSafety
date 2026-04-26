import requests
import random
import string

BASE_URL = "http://localhost:8000/auth"

def random_suffix(n=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def print_result(test_name, passed, response=None, note=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if note:
        print(f"       Note: {note}")
    if response is not None and not passed:
        print(f"       Status: {response.status_code} | Body: {response.json()}")
    print()

# ─── Test Data ───────────────────────────────────────────────────────────────

suffix = random_suffix()

CUSTOMER = {
    "username": f"customer_{suffix}",
    "password": "SecurePass@123",
    "email": f"customer_{suffix}@example.com",
    "phone": f"98{random.randint(10000000, 99999999)}",
    "address": "123 Main Street, Springfield",
    "role": "customer"
}

OFFICER = {
    "username": f"officer_{suffix}",
    "password": "OfficerPass@456",
    "email": f"officer_{suffix}@pd.gov",
    "phone": f"91{random.randint(10000000, 99999999)}",
    "address": "456 Precinct Ave, Shelbyville",
    "role": "officer",
    "badge_num": f"B-{random.randint(1000, 9999)}",
    "dept": "Homicide"
}

# ─── Signup Tests ─────────────────────────────────────────────────────────────

print("=" * 55)
print("  AUTH ROUTE TEST SUITE")
print("=" * 55)
print()
print("── SIGNUP ──────────────────────────────────────────────")
print()

# 1. Valid customer signup
r = requests.post(f"{BASE_URL}/signup", json=CUSTOMER)
passed = r.status_code == 200 and "access_token" in r.json()
print_result("Valid customer signup", passed, r)
customer_token = r.json().get("access_token") if passed else None

# 2. Valid officer signup
r = requests.post(f"{BASE_URL}/signup", json=OFFICER)
passed = r.status_code == 200 and "access_token" in r.json()
print_result("Valid officer signup", passed, r)
officer_token = r.json().get("access_token") if passed else None

# 3. Duplicate username (same customer again)
r = requests.post(f"{BASE_URL}/signup", json=CUSTOMER)
passed = r.status_code == 400
print_result("Duplicate signup rejected", passed, r,
             note="Expects 400 User already exists")

# 4. Duplicate email only (different username/phone)
dup_email = {**CUSTOMER,
             "username": f"new_{suffix}",
             "phone": f"70{random.randint(10000000, 99999999)}"}
r = requests.post(f"{BASE_URL}/signup", json=dup_email)
passed = r.status_code == 400
print_result("Duplicate email rejected", passed, r,
             note="Expects 400 User already exists")

# 5. Invalid role
bad_role = {**CUSTOMER,
            "username": f"badrole_{suffix}",
            "email": f"badrole_{suffix}@x.com",
            "phone": f"60{random.randint(10000000, 99999999)}",
            "role": "admin"}
r = requests.post(f"{BASE_URL}/signup", json=bad_role)
passed = r.status_code == 400
print_result("Invalid role rejected", passed, r,
             note="Expects 400 Role must be customer or officer")

# 6. Missing required field (no email)
missing_field = {k: v for k, v in CUSTOMER.items() if k != "email"}
missing_field["username"] = f"noemail_{suffix}"
r = requests.post(f"{BASE_URL}/signup", json=missing_field)
passed = r.status_code == 422
print_result("Missing required field rejected", passed, r,
             note="Expects 422 Unprocessable Entity from Pydantic")

# ─── Login Tests ──────────────────────────────────────────────────────────────

print("── LOGIN ───────────────────────────────────────────────")
print()

# 7. Valid customer login
r = requests.post(f"{BASE_URL}/login", json={
    "username": CUSTOMER["username"],
    "password": CUSTOMER["password"]
})
passed = r.status_code == 200 and "access_token" in r.json()
print_result("Valid customer login", passed, r)

# 8. Valid officer login
r = requests.post(f"{BASE_URL}/login", json={
    "username": OFFICER["username"],
    "password": OFFICER["password"]
})
passed = r.status_code == 200 and "access_token" in r.json()
print_result("Valid officer login", passed, r)

# 9. Wrong password
r = requests.post(f"{BASE_URL}/login", json={
    "username": CUSTOMER["username"],
    "password": "WrongPassword!"
})
passed = r.status_code == 401
print_result("Wrong password rejected", passed, r,
             note="Expects 401 Invalid password")

# 10. Non-existent user
r = requests.post(f"{BASE_URL}/login", json={
    "username": "ghost_user_xyz",
    "password": "anything"
})
passed = r.status_code == 404
print_result("Non-existent user rejected", passed, r,
             note="Expects 404 User not found")

# ─── Token Sanity Check ───────────────────────────────────────────────────────

print("── TOKEN ───────────────────────────────────────────────")
print()

# 11. Token is a non-empty string
passed = isinstance(customer_token, str) and len(customer_token) > 20
print_result("Customer token is valid JWT string", passed,
             note=f"Token prefix: {customer_token[:30]}..." if customer_token else "No token")

passed = isinstance(officer_token, str) and len(officer_token) > 20
print_result("Officer token is valid JWT string", passed,
             note=f"Token prefix: {officer_token[:30]}..." if officer_token else "No token")

print("=" * 55)
print("  Done.")
print("=" * 55)

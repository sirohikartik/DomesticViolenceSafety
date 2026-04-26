import requests
import random
import string

BASE_URL = "http://localhost:8000"
CUSTOMER_URL = f"{BASE_URL}/customer"
AUTH_URL = f"{BASE_URL}/auth"

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

# ─── Setup: Login to get token ────────────────────────────────────────────────

print("=" * 55)
print("  CUSTOMER ROUTE TEST SUITE")
print("=" * 55)
print()
print("── SETUP: LOGIN ────────────────────────────────────────")
print()

# Change these to a customer that already exists in your DB
USERNAME = "string"
PASSWORD = "string"

r = requests.post(f"{AUTH_URL}/login", json={
    "username": USERNAME,
    "password": PASSWORD
})

if r.status_code != 200 or "access_token" not in r.json():
    print(f"❌ Login failed — cannot proceed. Response: {r.json()}")
    exit(1)

TOKEN = r.json()["access_token"]
print(f"✅ Logged in as '{USERNAME}'")
print(f"   Token prefix: {TOKEN[:30]}...")
print()

# ─── /me GET (POST) ───────────────────────────────────────────────────────────

print("── GET /me ─────────────────────────────────────────────")
print()

# 1. Valid token
r = requests.post(f"{CUSTOMER_URL}/me", json={"token": TOKEN})
passed = r.status_code == 200 and "id" in r.json() and "password" not in r.json()
print_result("Fetch customer details", passed, r)
if passed:
    print(f"       User: {r.json()}")
    print()

# 2. Invalid token
r = requests.post(f"{CUSTOMER_URL}/me", json={"token": "invalidtoken123"})
passed = r.status_code == 401
print_result("Invalid token rejected", passed, r)

# ─── /me PUT ─────────────────────────────────────────────────────────────────

print("── PUT /me ─────────────────────────────────────────────")
print()

suffix = ''.join(random.choices(string.digits, k=4))

# 3. Update address only
r = requests.put(f"{CUSTOMER_URL}/me", json={
    "token": TOKEN,
    "address": f"456 Updated Street #{suffix}"
})
passed = r.status_code == 200 and r.json().get("address") == f"456 Updated Street #{suffix}"
print_result("Update address", passed, r)

# 4. Update phone only
new_phone = f"9{random.randint(100000000, 999999999)}"
r = requests.put(f"{CUSTOMER_URL}/me", json={
    "token": TOKEN,
    "phone": new_phone
})
passed = r.status_code == 200 and r.json().get("phone") == new_phone
print_result("Update phone", passed, r)

# 5. Update with invalid token
r = requests.put(f"{CUSTOMER_URL}/me", json={
    "token": "badtoken",
    "address": "Hacker Lane"
})
passed = r.status_code == 401
print_result("Update with invalid token rejected", passed, r)

# ─── /report ─────────────────────────────────────────────────────────────────

print("── POST /report ────────────────────────────────────────")
print()

# 6. Valid manual report
r = requests.post(f"{CUSTOMER_URL}/report", json={"token": TOKEN})
passed = r.status_code == 200 and "incident_id" in r.json()
print_result("Manual report created", passed, r)
if passed:
    print(f"       Incident ID: {r.json()['incident_id']}")
    print()

# 7. Manual report with bad token
r = requests.post(f"{CUSTOMER_URL}/report", json={"token": "faketoken"})
passed = r.status_code == 401
print_result("Manual report with invalid token rejected", passed, r)

# ─── /analyze ────────────────────────────────────────────────────────────────

print("── POST /analyze ───────────────────────────────────────")
print()

# 8. Conversation with clear aggression (should flag True)
aggressive_text = "I will hurt you if you don't listen to me. You better do what I say or I'll make you regret it."
r = requests.post(f"{CUSTOMER_URL}/analyze", json={
    "token": TOKEN,
    "conversation": aggressive_text
}, timeout=90)
passed = r.status_code == 200 and r.json().get("flagged") == True
print_result("Aggressive conversation flagged", passed, r,
             note="Ollama should return True and create incident")
if r.status_code == 200:
    print(f"       Result: {r.json()}")
    print()

# 9. Safe conversation (should not flag)
safe_text = "Hey, how was your day? I made pasta for dinner, hope you like it!"
r = requests.post(f"{CUSTOMER_URL}/analyze", json={
    "token": TOKEN,
    "conversation": safe_text
}, timeout=90)
passed = r.status_code == 200 and r.json().get("flagged") == False
print_result("Safe conversation not flagged", passed, r,
             note="Ollama should return False, no incident created")
if r.status_code == 200:
    print(f"       Result: {r.json()}")
    print()

# 10. Analyze with invalid token
r = requests.post(f"{CUSTOMER_URL}/analyze", json={
    "token": "badtoken",
    "conversation": "test"
}, timeout=90)
passed = r.status_code == 401
print_result("Analyze with invalid token rejected", passed, r)

print("=" * 55)
print("  Done.")
print("=" * 55)

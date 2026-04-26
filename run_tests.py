import subprocess
import sys
import os

TEST_FOLDERS = ["unit_tests", "integration_tests", "system_tests"]

def run_file(path):
    print(f"\n{'='*55}")
    print(f"  Running: {path}")
    print(f"{'='*55}")
    result = subprocess.run([sys.executable, path], capture_output=False)
    return result.returncode == 0

passed_files = []
failed_files = []

for folder in TEST_FOLDERS:
    if not os.path.exists(folder):
        print(f"\n⚠️  Folder not found, skipping: {folder}")
        continue

    files = sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.startswith("test_") and f.endswith(".py")
    ])

    if not files:
        print(f"\n⚠️  No test files found in: {folder}")
        continue

    print(f"\n{'#'*55}")
    print(f"  📁 {folder.upper()} ({len(files)} file(s))")
    print(f"{'#'*55}")

    for f in files:
        ok = run_file(f)
        if ok:
            passed_files.append(f)
        else:
            failed_files.append(f)

# ── Summary ───────────────────────────────────────────────
total = len(passed_files) + len(failed_files)
print(f"\n{'='*55}")
print(f"  RESULTS — {total} file(s) ran")
print(f"{'='*55}")
for f in passed_files:
    print(f"  ✅ {f}")
for f in failed_files:
    print(f"  ❌ {f}")
print(f"\n  Passed: {len(passed_files)} / {total}")
if failed_files:
    print("  Some tests failed — check output above.")
    sys.exit(1)
else:
    print("  All test files completed.")

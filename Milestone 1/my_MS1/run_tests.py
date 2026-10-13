import subprocess
import sys
from pathlib import Path

BENCHMARKS_DIR = Path("/Users/2headaxe/Desktop/CS Fall 2026/comp520_compilers/Milestone 1/benchmarks")
COMPILER_DIR = Path(__file__).resolve().parent

def run_all_tests():
    mini_files = list(BENCHMARKS_DIR.rglob("*.mini"))

    print(f"==================================================")
    print(f" Running Milestone 1 Tests on {len(mini_files)} .mini files")
    print(f"==================================================\n")

    passed = 0
    failed = 0

    for mini_file in sorted(mini_files):
        print(f"Testing: {mini_file.relative_to(BENCHMARKS_DIR)}")

        try:
            result = subprocess.run(
                [sys.executable, "mini_compiler.py", str(mini_file)],
                capture_output=True,
                text=True,
                check=True,
                cwd=COMPILER_DIR
            )

            stdout_lines = result.stdout.strip().splitlines()

            # mini_compiler.py prints "ERRORS FOUND <n>" after semantic analysis
            error_count = None
            for line in stdout_lines:
                if line.startswith("ERRORS FOUND "):
                    try:
                        error_count = int(line.split()[-1])
                    except ValueError:
                        pass

            if error_count is None:
                print("  [FAIL] No 'ERRORS FOUND <n>' line in the output (syntax error?)")
                failed += 1
                print("-" * 50)
                continue

            # Benchmarks are valid programs, so they should have 0 semantic errors
            if error_count == 0:
                print("  [PASS] Clean semantic analysis (0 errors).")
                passed += 1
            else:
                print(f"  [FAIL] Detected {error_count} semantic error(s) in a valid benchmark!")
                print("  --- Error Log ---")
                for line in stdout_lines:
                    if line.startswith("ERROR."):
                        print(f"    {line}")
                failed += 1

        except subprocess.CalledProcessError as e:
            print("  [FAIL] Compiler crashed during execution!")
            print(f"  stderr:\n{e.stderr}")
            failed += 1

        print("-" * 50)

    print(f"\nTest Summary: {passed} passed, {failed} failed out of {len(mini_files)} total.")

if __name__ == "__main__":
    run_all_tests()
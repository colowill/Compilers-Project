import os
import subprocess
from pathlib import Path

BENCHMARKS_DIR = Path("/Users/2headaxe/Desktop/CS Fall 2026/comp520_compilers/Milestone 1/benchmarks")

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
            # Runs compiler with --no-pp to only get semantic analysis error count
            result = subprocess.run(
                ["python3", "mini_compiler.py", "--no-pp", str(mini_file)],
                capture_output=True,
                text=True,
                check=True
            )
            
            stdout_lines = result.stdout.strip().splitlines()
            
            if not stdout_lines:
                print("  [FAIL] No output produced from mini_compiler.py")
                failed += 1
                continue

            # The last line printed by mini_compiler.py is the error count
            last_line = stdout_lines[-1].strip()
            
            try:
                error_count = int(last_line)
            except ValueError:
                print(f"  [FAIL] Expected last line to be integer error count, got: '{last_line}'")
                failed += 1
                continue

            # Check if this benchmark is a valid program (e.g. standard benchmark folder)
            # Valid benchmark programs should compile with 0 semantic errors
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
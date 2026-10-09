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
        print(f"Testing: {mini_file}")
        
        try:
            # Executes python3 mini_compiler.py <path/to/file.mini>
            result = subprocess.run(
                ["python3", "mini_compiler.py", str(mini_file)],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout.strip()
            
            # Look for an output.expected file in the same directory
            expected_file = mini_file.parent / "output.expected"
            
            if expected_file.exists():
                expected_text = expected_file.read_text().strip()
                
                # Check if output matches expected benchmark output
                if actual_matches_expected(output, expected_text):
                    print("  [PASS] Output matches expected benchmark.")
                    passed += 1
                else:
                    print("  [FAIL] Output mismatch!")
                    print("--- Actual Output ---")
                    print(output)
                    print("--- Expected Output ---")
                    print(expected_text)
                    failed += 1
            else:
                # If no .expected file exists, check if execution succeeded without crashing
                print("  [PASS] Executed successfully (No .expected file found).")
                passed += 1

        except subprocess.CalledProcessError as e:
            print("  [FAIL] Compiler crashed with an unhandled exception!")
            print(f"  Error Output:\n{e.stderr}")
            failed += 1
            
        print("-" * 50)

    print(f"\nTest Summary: {passed} passed, {failed} failed out of {len(mini_files)} total.")

def actual_matches_expected(actual: str, expected: str) -> bool:
    """
    Normalizes whitespace and checks if actual compiler output matches expected output.
    """
    actual_lines = [line.strip() for line in actual.splitlines() if line.strip()]
    expected_lines = [line.strip() for line in expected.splitlines() if line.strip()]
    
    return actual_lines == expected_lines

if __name__ == "__main__":
    run_all_tests()
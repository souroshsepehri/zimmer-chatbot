#!/usr/bin/env python3
"""
Health Check System for Persian Chatbot
Runs all tests and generates a comprehensive health report
"""
import subprocess
import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class HealthChecker:
    """Health check system for chatbot"""
    
    def __init__(self):
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        self.failures_log = self.logs_dir / "health_failures.log"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "failed_tests": [],
            "modules": {}
        }
    
    def run_tests(self) -> Tuple[int, int, int, int, List[Dict]]:
        """Run pytest and collect results"""
        print("Running tests...")
        print("=" * 60)
        
        # Run pytest
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--maxfail=100",  # Don't stop on first failure
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            
            # Parse pytest output - combine stdout and stderr
            output_text = result.stdout + "\n" + result.stderr
            output_lines = output_text.split('\n')
            failed_tests = []
            
            # Parse text output
            total = 0
            passed = 0
            failed = 0
            skipped = 0
            errors = 0
            
            # Look for summary line - can be in different formats:
            # "======= 1 failed, 21 passed, 3 skipped, 17 errors in 1.93s ========"
            # "============ 10 failed, 29 passed, 3 skipped, 9 warnings in 5.61s ============="
            summary_line = None
            for line in output_lines:
                line_lower = line.lower()
                # Look for lines with test counts - must have "passed" or "failed" and numbers
                if (("passed" in line_lower or "failed" in line_lower) and
                    any(char.isdigit() for char in line) and
                    ("in" in line_lower or "=" in line)):
                    summary_line = line
                    # Prefer lines that have more detail (contain "=" at start/end)
                    if "=" in line and line.strip().startswith("="):
                        break
            
            if summary_line:
                import re
                # Match patterns like "21 passed", "1 failed", "3 skipped", "17 errors"
                passed_match = re.search(r'(\d+)\s+passed', summary_line, re.IGNORECASE)
                failed_match = re.search(r'(\d+)\s+failed', summary_line, re.IGNORECASE)
                skipped_match = re.search(r'(\d+)\s+skipped', summary_line, re.IGNORECASE)
                error_match = re.search(r'(\d+)\s+error', summary_line, re.IGNORECASE)
                
                if passed_match:
                    passed = int(passed_match.group(1))
                if failed_match:
                    failed = int(failed_match.group(1))
                if skipped_match:
                    skipped = int(skipped_match.group(1))
                if error_match:
                    errors = int(error_match.group(1))
                
                total = passed + failed + skipped + errors
            
            # Extract failed tests from output
            current_failed_test = None
            collecting_error = False
            
            for i, line in enumerate(output_lines):
                if "FAILED" in line or "ERROR" in line:
                    parts = line.split()
                    test_name = None
                    for j, part in enumerate(parts):
                        if "FAILED" in part or "ERROR" in part:
                            if j > 0:
                                test_name = "::".join(parts[:j])
                            break
                    
                    if not test_name:
                        test_name = line.strip()
                    
                    current_failed_test = {
                        "name": test_name,
                        "file": test_name.split("::")[0] if "::" in test_name else "unknown",
                        "error": line + "\n",
                        "message": line.strip()[:100]
                    }
                    collecting_error = True
                elif collecting_error and current_failed_test:
                    if line.strip() and not line.strip().startswith("="):
                        current_failed_test["error"] += line + "\n"
                        if len(current_failed_test["error"]) < 500:  # Limit error size
                            pass
                    elif "PASSED" in line or ("=" in line and len(line.strip()) > 10):
                        if current_failed_test:
                            failed_tests.append(current_failed_test)
                        current_failed_test = None
                        collecting_error = False
            
            if current_failed_test:
                failed_tests.append(current_failed_test)
            
            return total, passed, failed, skipped + errors, failed_tests
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return 0, 0, 0, 0, []
    
    def analyze_modules(self, failed_tests: List[Dict]) -> Dict[str, Dict]:
        """Analyze which modules have failures"""
        modules = {}
        
        for test in failed_tests:
            file_path = test.get("file", "unknown")
            module_name = Path(file_path).stem.replace("test_", "")
            
            if module_name not in modules:
                modules[module_name] = {
                    "status": "[FAIL]",
                    "failed_count": 0,
                    "tests": []
                }
            
            modules[module_name]["failed_count"] += 1
            modules[module_name]["tests"].append(test.get("name", "unknown"))
        
        # Add passing modules
        test_files = list(Path("tests").glob("test_*.py"))
        for test_file in test_files:
            module_name = test_file.stem.replace("test_", "")
            if module_name not in modules:
                modules[module_name] = {
                    "status": "[OK]",
                    "failed_count": 0,
                    "tests": []
                }
        
        return modules
    
    def write_failures_log(self, failed_tests: List[Dict]):
        """Write detailed failures to log file"""
        with open(self.failures_log, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"Health Check Failures Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            if not failed_tests:
                f.write("[OK] No test failures!\n")
                return
            
            for i, test in enumerate(failed_tests, 1):
                f.write(f"\n[{i}] Test: {test.get('name', 'unknown')}\n")
                f.write(f"    File: {test.get('file', 'unknown')}\n")
                f.write(f"    Error: {test.get('message', 'No error message')}\n")
                
                error_detail = test.get('error', '')
                if error_detail and len(error_detail) > 200:
                    # Truncate long errors, keep first and last parts
                    error_detail = error_detail[:200] + "\n    ... (truncated) ...\n    " + error_detail[-200:]
                f.write(f"    Details:\n{error_detail}\n")
                f.write("-" * 80 + "\n")
    
    def generate_report(self):
        """Generate and display health report"""
        total, passed, failed, skipped, failed_tests = self.run_tests()
        
        self.results["total_tests"] = total
        self.results["passed"] = passed
        self.results["failed"] = failed
        self.results["skipped"] = skipped
        self.results["failed_tests"] = failed_tests
        self.results["modules"] = self.analyze_modules(failed_tests)
        
        # Write failures log
        self.write_failures_log(failed_tests)
        
        # Calculate percentage
        if total > 0:
            percentage = (passed / total) * 100
        else:
            percentage = 0
        
        # Display report
        print("\n" + "=" * 60)
        print("HEALTH CHECK REPORT")
        print("=" * 60)
        print(f"\n[PASS] Tests Passed: {passed}")
        print(f"[FAIL] Tests Failed: {failed}")
        print(f"[SKIP] Tests Skipped: {skipped}")
        print(f"[TOTAL] Total Tests: {total}")
        print(f"\nSuccess Rate: {percentage:.1f}%")
        
        # Module status
        print("\nModule Status:")
        print("-" * 60)
        modules = self.results["modules"]
        healthy_modules = [m for m, data in modules.items() if data["status"] == "[OK]"]
        unhealthy_modules = [m for m, data in modules.items() if data["status"] == "[FAIL]"]
        
        for module, data in sorted(modules.items()):
            status = data["status"]
            count = data["failed_count"]
            print(f"  {status} {module:20s} ({count} failures)")
        
        # Overall status
        print("\n" + "=" * 60)
        if failed == 0 and total > 0:
            print("[OK] All core chatbot components are healthy!")
        elif percentage >= 80:
            print(f"[WARN] {len(unhealthy_modules)} modules have issues. See logs/health_failures.log for details.")
        else:
            print(f"[FAIL] {len(unhealthy_modules)} modules have failing tests. See logs/health_failures.log for details.")
        
        if failed > 0:
            print(f"\nDetailed failure log: {self.failures_log}")
        
        print("=" * 60 + "\n")
        
        return percentage, failed == 0


def main():
    """Main entry point"""
    # Set UTF-8 encoding for Windows
    import sys
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("Starting Health Check System...")
    print("=" * 60)
    
    checker = HealthChecker()
    percentage, all_passed = checker.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()


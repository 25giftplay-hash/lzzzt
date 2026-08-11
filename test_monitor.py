import time
from datetime import datetime, timedelta
from monitor import parse_spamblock

def run_tests():
    print("Running Spamblock Parsing Tests...")
    
    current_time = time.time()
    
    tests = [
        # (value, max_wait_hours, expected_result, test_name)
        (None, 72, True, "No spamblock (None)"),
        (0, 72, True, "No spamblock (0)"),
        ("no", 72, True, "No spamblock ('no')"),
        ("None", 72, True, "No spamblock ('None')"),
        
        # Temporary spamblocks (timestamps)
        (current_time + 3600 * 24, 72, True, "24 hours remaining (accepted)"),
        (current_time + 3600 * 70, 72, True, "70 hours remaining (accepted)"),
        (current_time + 3600 * 73, 72, False, "73 hours remaining (rejected)"),
        (current_time - 3600, 72, True, "Expired block in past (accepted)"),
        
        # String numeric timestamps
        (str(int(current_time + 3600 * 12)), 72, True, "String timestamp 12h (accepted)"),
        (str(int(current_time + 3600 * 96)), 72, False, "String timestamp 96h (rejected)"),
        
        # String Date Formats
        ((datetime.now() + timedelta(hours=36)).strftime('%d.%m.%Y %H:%M'), 72, True, "Date string 36h (accepted)"),
        ((datetime.now() + timedelta(hours=100)).strftime('%d.%m.%Y %H:%M'), 72, False, "Date string 100h (rejected)"),
        
        # Permanent bans
        ("Permanent", 72, False, "Permanent ban string (rejected)"),
        ("Вечный", 72, False, "Russian eternal ban string (rejected)"),
        (1, 72, False, "Boolean true integer (rejected)"),
    ]
    
    passed = 0
    for val, max_hours, expected, name in tests:
        res, msg = parse_spamblock(val, max_hours)
        if res == expected:
            print(f"[PASS] {name} -> Got {res} ({msg})")
            passed += 1
        else:
            print(f"[FAIL] {name} -> Expected {expected}, Got {res} ({msg})")
            
    print("--------------------------------------------------")
    print(f"Tests complete: {passed}/{len(tests)} passed.")
    print("--------------------------------------------------")

if __name__ == "__main__":
    run_tests()

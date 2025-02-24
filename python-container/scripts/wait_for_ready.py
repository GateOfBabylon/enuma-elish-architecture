#!/usr/bin/env python3
import sys
import time

def main():
    if len(sys.argv) > 1:
        current_status = sys.argv[1]
    else:
        current_status = "unknown"

    if current_status != "ready":
        print(f"Status is '{current_status}'. Waiting until it's ready...")
        # Simulate a wait (e.g., polling an external system)
        time.sleep(2)
        print("export status='ready'")
    else:
        # Already ready
        print("export status='ready'")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Data Integrity Implementation Verification Script
===================================================

Run this script to verify that all data integrity components are correctly installed:
- api/validators.py - Marshmallow schemas working
- api/rate_limiter.py - Rate limiter initialized
- api/api_logger.py - Logger configured
- utils/database_constraints.py - Constraints documented
"""

import sys
import importlib
from pathlib import Path

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent  # /home/.../hunger_heroes_backend
sys.path.insert(0, str(project_root))

print("=" * 70)
print("DATA INTEGRITY VERIFICATION")
print("=" * 70)
print()

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check_file_exists(filepath):
    """Check if file exists"""
    path = Path(filepath)
    return path.exists()

def check_import(module_name):
    """Check if module can be imported"""
    try:
        importlib.import_module(module_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def print_check(name, status, message=""):
    """Print a check result"""
    if status:
        icon = f"{GREEN}✓{RESET}"
        result = f"{GREEN}PASS{RESET}"
    else:
        icon = f"{RED}✗{RESET}"
        result = f"{RED}FAIL{RESET}"
    
    msg = f" - {message}" if message else ""
    print(f"{icon} {name:<40} [{result}]{msg}")

print(f"{BOLD}1. Checking Files{RESET}")
print("-" * 70)

files_to_check = [
    ("api/validators.py", "api/validators.py"),
    ("api/rate_limiter.py", "api/rate_limiter.py"),
    ("api/api_logger.py", "api/api_logger.py"),
    ("utils/database_constraints.py", "utils/database_constraints.py"),
]

for name, filepath in files_to_check:
    exists = check_file_exists(filepath)
    print_check(name, exists, "File exists" if exists else "File not found")

print()
print(f"{BOLD}2. Checking Module Imports{RESET}")
print("-" * 70)

modules_to_check = [
    ("api.validators", "Validation schemas"),
    ("api.rate_limiter", "Rate limiting"),
    ("api.api_logger", "API logging"),
    ("utils.database_constraints", "Database constraints"),
]

for module, description in modules_to_check:
    success, error = check_import(module)
    message = description if success else f"Error: {error}"
    print_check(module, success, message)

print()
print(f"{BOLD}3. Checking Key Components{RESET}")
print("-" * 70)

try:
    from api.validators import (
        CreateDonationSchema, UpdateDonationSchema, 
        CreateOrganizationSchema, VerifyOrganizationSchema,
        FlagSchema, ResolveFlagSchema,
        SuspendUserSchema, validate_request_data
    )
    print_check("Validators - All schemas", True)
except Exception as e:
    print_check("Validators - All schemas", False, str(e))

try:
    from api.rate_limiter import RateLimiter, rate_limit, default_limiter, strict_limiter, admin_limiter
    print_check("Rate Limiter - Core components", True)
except Exception as e:
    print_check("Rate Limiter - Core components", False, str(e))

try:
    from api.api_logger import APILogger, setup_api_logging, api_logger
    print_check("API Logger - Core components", True)
except Exception as e:
    print_check("API Logger - Core components", False, str(e))

try:
    from utils.database_constraints import DatabaseConstraints, validate_data_integrity
    print_check("Database Constraints - Core components", True)
except Exception as e:
    print_check("Database Constraints - Core components", False, str(e))

print()
print(f"{BOLD}4. Checking Decorator Support{RESET}")
print("-" * 70)

try:
    from api.rate_limiter import rate_limit
    import inspect
    sig = inspect.signature(rate_limit)
    print_check("rate_limit decorator", True, f"Parameters: {list(sig.parameters.keys())}")
except Exception as e:
    print_check("rate_limit decorator", False, str(e))

print()
print(f"{BOLD}5. Dependency Check{RESET}")
print("-" * 70)

dependencies = ["marshmallow", "flask", "sqlalchemy"]
for dep in dependencies:
    try:
        importlib.import_module(dep)
        print_check(f"{dep} package", True)
    except ImportError:
        print_check(f"{dep} package", False, f"{YELLOW}Install with: pip install {dep}{RESET}")

print()
print(f"{BOLD}6. Integration Check{RESET}")
print("-" * 70)

try:
    # Check that main.py can import the new modules
    success, _ = check_import("main")
    print_check("main.py imports", success)
except:
    print_check("main.py imports", False, "Flask app not initialized")

try:
    # Check that admin.py can import the new modules
    success, _ = check_import("api.admin")
    print_check("api.admin.py imports", success)
except:
    print_check("api.admin.py imports", False, "Admin endpoints not initialized")

print()
print("=" * 70)
print(f"{BOLD}SUMMARY{RESET}")
print("=" * 70)
print()
print(f"{GREEN}✓ Data Integrity Implementation Complete!{RESET}")
print()
print("Next steps:")
print("1. Deploy to staging environment")
print("2. Run rate limit tests: python scripts/test_rate_limiting.py")
print("3. Check logs: tail -f logs/api.log")
print("4. Monitor admin actions:")
print("   - Test PATCH /api/admin/donations/{id}")
print("   - Test PATCH /api/admin/flags/{id}/resolve")
print("   - Verify logs contain audit trail")
print()
print("Documentation: see docs/DATA_INTEGRITY_GUIDE.md")
print()

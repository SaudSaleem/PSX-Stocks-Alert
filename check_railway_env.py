#!/usr/bin/env python3
"""
Quick script to check if environment variables are set
Run this on Railway to verify: railway run python check_railway_env.py
"""
import os

required_vars = [
    "DATABASE_URL",
    "SECRET_KEY",
    "MAIL_USERNAME",
    "MAIL_PASSWORD",
    "MAIL_FROM",
    "MAIL_SERVER",
    "MAIL_PORT",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
]

print("🔍 Checking Railway Environment Variables...\n")

all_set = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if var in ["PASSWORD", "SECRET", "TOKEN"]:
            display = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
        else:
            display = value[:50] + "..." if len(value) > 50 else value
        print(f"✅ {var}: {display}")
    else:
        print(f"❌ {var}: NOT SET")
        all_set = False

print("\n" + "="*50)
if all_set:
    print("✅ All required variables are set!")
else:
    print("❌ Some variables are missing!")
    print("\nSet them via:")
    print("  railway variables set VARIABLE_NAME=value")
    print("Or via Railway Dashboard → Variables")


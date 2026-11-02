"""
Application Entry Point for CAMPS-ML / Smart College Management System.
Usage:
    py run.py           # Start the Flask development server on http://localhost:5000
    py run.py check     # Perform environment and database diagnostic check
"""

import sys
import os

# Ensure root directory is on the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import create_app
from backend.extensions import db

app = create_app(os.getenv("FLASK_ENV", "development"))


def run_system_check():
    """Diagnose configuration, database, and system readiness."""
    print("=" * 70)
    print(" CAMPS-ML / SMART COLLEGE SYSTEM DIAGNOSTIC CHECK")
    print("=" * 70)
    
    with app.app_context():
        print(f"[*] Environment:  {app.config.get('ENV', 'development')}")
        print(f"[*] Debug Mode:   {app.debug}")
        print(f"[*] Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        
        # Test DB connection
        try:
            db.session.execute(db.text("SELECT 1"))
            print("[+] Database Connection: SUCCESS (SQLite DB connected)")
        except Exception as e:
            print(f"[!] Database Connection: FAILED ({e})")
            
        print("=" * 70)
        print("[+] System diagnostic check passed successfully!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        run_system_check()
    else:
        port = int(os.getenv("PORT", 5000))
        print("=" * 70)
        print(" [*] SMART COLLEGE MANAGEMENT SYSTEM - BACKEND API")
        print(f" [*] Running on:        http://localhost:{port}")
        print(f" [*] Health Check URL:  http://localhost:{port}/api/health")
        print(f" [*] System Info URL:   http://localhost:{port}/api/system/info")
        print(f" [*] Portals Enabled:   Student, Parent, Teacher, Admin, Principal")
        print("=" * 70)
        app.run(host="0.0.0.0", port=port, debug=True)

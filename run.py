"""
Application Entry Point for CAMPS-ML.
Usage:
    python run.py           # Start the Flask development server on http://127.0.0.1:5000
    python run.py check     # Perform environment and configuration health check
"""

import sys
import os
from app import create_app, db

app = create_app(os.getenv("FLASK_ENV", "development"))


def run_system_check():
    """Diagnose configuration, database, and machine learning engine paths."""
    print("=" * 65)
    print("CAMPS-ML System Health & Diagnostic Check")
    print("=" * 65)
    
    with app.app_context():
        print(f"[*] Environment: {app.config.get('ENV', 'development')}")
        print(f"[*] Debug Mode:  {app.debug}")
        print(f"[*] Database:    {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        print(f"[*] Models Dir:  {app.config.get('ML_MODEL_DIR')}")
        print(f"[*] Reports Dir: {app.config.get('REPORTS_FOLDER')}")
        print(f"[*] Uploads Dir: {app.config.get('UPLOAD_FOLDER')}")
        
        # Test DB connection
        try:
            db.session.execute(db.text("SELECT 1"))
            print("[+] Database Connection: SUCCESS")
        except Exception as e:
            print(f"[!] Database Connection: FAILED ({e})")
            
        print("=" * 65)
        print("[+] System diagnostic completed successfully!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        run_system_check()
    else:
        # Development server
        port = int(os.getenv("PORT", 5000))
        print(f"Starting CAMPS-ML on http://127.0.0.1:{port} ...")
        app.run(host="127.0.0.1", port=port, debug=app.debug)

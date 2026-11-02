import os
import sys

# Ensure root directory is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 70)
    print(" [*] SMART COLLEGE MANAGEMENT SYSTEM - BACKEND API")
    print(f" [*] Running on:        http://localhost:{port}")
    print(f" [*] Health Check URL:  http://localhost:{port}/api/health")
    print(f" [*] System Info URL:   http://localhost:{port}/api/system/info")
    print(f" [*] Portals Enabled:   Student, Parent, Teacher, Admin, Principal")
    print(f" [*] Database URI:      {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("=" * 70)
    app.run(host='0.0.0.0', port=port, debug=True)

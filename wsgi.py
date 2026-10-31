"""
Production WSGI Entry Point for CAMPS-ML.
Suitable for Gunicorn, uWSGI, Render, and PythonAnywhere deployments.
"""

import os
from app import create_app

# Default to production if environment variable set, else development
env = os.getenv("FLASK_ENV", "production")
app = create_app(env)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

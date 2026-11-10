import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Force SQLite mode
os.environ['USE_MYSQL'] = 'false'
os.environ['DATABASE_URL'] = ''

from scripts.ingest_all_pesitm_batches import run_ingestion

if __name__ == "__main__":
    print("[*] Running ingestion into SQLite fallback database...")
    run_ingestion()

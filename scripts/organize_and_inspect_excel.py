import os
import shutil
import glob
import pandas as pd
import xlrd

UPLOAD_DIR = r"C:\Users\vinay\.gemini\antigravity\brain\0e99bc08-15d8-4aba-a665-c3e609c00cdc\.user_uploaded"
BATCH_22_DIR = os.path.join("data", "college_batches", "22-26-Batch")
BATCH_23_DIR = os.path.join("data", "college_batches", "23-27-Batch")

os.makedirs(BATCH_22_DIR, exist_ok=True)
os.makedirs(BATCH_23_DIR, exist_ok=True)

FILE_MAP = {
    # 2022-2026 Batch
    "media_1794327623976_e6951488.xls": (BATCH_22_DIR, "1CS-1-sem.xls"),
    "media_1794327623978_f9cc1e1e.xls": (BATCH_22_DIR, "2CS-2-sem.xls"),
    "media_1794327623980_dd56c68f.xls": (BATCH_22_DIR, "3CS-3-sem.xls"),
    "media_1794327623977_ee3727e0.xls": (BATCH_22_DIR, "4CS-4-sem.xls"),
    "media_1794327623978_13c244aa.xls": (BATCH_22_DIR, "5CS-5-sem.xls"),
    "media_1794327623979_7796eb36.xls": (BATCH_22_DIR, "6CS-6-sem.xls"),
    "media_1794327623980_b5420e31.xls": (BATCH_22_DIR, "7CS-7-sem.xls"),
    "media_1794327623978_176137b3.xls": (BATCH_22_DIR, "8CS-8-sem.xls"),
    # 2023-2027 Batch
    "media_1794327634833_e9e3efbf.xls": (BATCH_23_DIR, "1-sem.xls"),
    "media_1794327634835_ae0d3bc5.xls": (BATCH_23_DIR, "2-sem.xls"),
    "media_1794327634835_0d22f383.xls": (BATCH_23_DIR, "3-sem.xls"),
    "media_1794327634836_a82c661f.xls": (BATCH_23_DIR, "4-sem.xls"),
    "media_1794327634836_206a95f6.xls": (BATCH_23_DIR, "5-sem.xls"),
    "media_1794327634837_68455a90.xls": (BATCH_23_DIR, "6-sem.xls"),
}

for src_name, (dst_dir, dst_name) in FILE_MAP.items():
    src_path = os.path.join(UPLOAD_DIR, src_name)
    dst_path = os.path.join(dst_dir, dst_name)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"[COPIED] {src_name} -> {dst_path}")
    else:
        print(f"[MISSING] {src_path}")

print("\n--- Inspecting 2022-26 Batch Files ---")
for f in sorted(glob.glob(os.path.join(BATCH_22_DIR, "*.xls"))):
    book = xlrd.open_workbook(f)
    print(f"\nFile: {os.path.basename(f)} | Sheets: {book.sheet_names()}")
    sheet0 = book.sheet_by_index(0)
    print(f"  Sheet 0 ({sheet0.name}): {sheet0.nrows} rows x {sheet0.ncols} cols")
    for r in range(min(5, sheet0.nrows)):
        print(f"    Row {r}: {sheet0.row_values(r)[:8]}")

print("\n--- Inspecting 2023-27 Batch Files ---")
for f in sorted(glob.glob(os.path.join(BATCH_23_DIR, "*.xls"))):
    book = xlrd.open_workbook(f)
    print(f"\nFile: {os.path.basename(f)} | Sheets: {book.sheet_names()}")
    sheet0 = book.sheet_by_index(0)
    print(f"  Sheet 0 ({sheet0.name}): {sheet0.nrows} rows x {sheet0.ncols} cols")
    for r in range(min(5, sheet0.nrows)):
        print(f"    Row {r}: {sheet0.row_values(r)[:8]}")

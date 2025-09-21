import sqlite3
import os

# --- Configuration ---
DB_FILE = "hexagonal_kb.db"
PRAGMAS = {
    "journal_mode": "WAL",
    "synchronous": "NORMAL",
    "cache_size": -64000,  # 64MB cache
    "temp_store": "MEMORY",
    "busy_timeout": 5000,
}

# --- Main Execution ---
def tune_database():
    """Connects to the SQLite database and applies performance pragmas."""
    db_path = os.path.join(os.getcwd(), DB_FILE)
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at '{db_path}'")
        return

    print(f"Connecting to database: {db_path}")
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        print("--- Applying PRAGMA settings ---")
        for key, value in PRAGMAS.items():
            print(f"Setting {key.upper()} = {value}")
            cur.execute(f"PRAGMA {key}={value};")
        
        print("\n--- Verifying PRAGMA settings ---")
        for key in PRAGMAS.keys():
            cur.execute(f"PRAGMA {key};")
            result = cur.fetchone()
            print(f"Verified {key.upper()}: {result[0]}")

        con.close()
        print("\nDatabase tuning complete. Settings applied and verified.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    tune_database()

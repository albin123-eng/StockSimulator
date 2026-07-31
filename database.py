import sqlite3
import os

db_p = os.path.join(os.path.dirname(__file__), 'stocksimulator.db')

def get_connection():# connect to sqlite and enable foreign keys
    conn = sqlite3.connect(db_p)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")  
    return conn

def initialize_database():
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usersTbl (
                    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Username TEXT UNIQUE NOT NULL,
                    HashedPassword TEXT NOT NULL,
                    Balance REAL NOT NULL DEFAULT 100000.00 CHECK(Balance >= 0.00)
                );
            """)

            # Portfolio table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS PortTbl (
                    HOLDID INTEGER PRIMARY KEY AUTOINCREMENT,
                    UserID INTEGER NOT NULL,
                    TickerSymbol TEXT NOT NULL, 
                    Quantity INTEGER NOT NULL CHECK(Quantity > 0),
                    FOREIGN KEY(UserID) REFERENCES usersTbl(UserID) ON DELETE CASCADE
                );
            """)

            # Transactions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS TransactionsTbl (
                    TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                    UserID INTEGER NOT NULL,
                    TickerSymbol TEXT NOT NULL,
                    Quantity INTEGER NOT NULL CHECK(Quantity > 0),
                    PriceBought REAL NOT NULL CHECK(PriceBought > 0.00),
                    TotalCost REAL NOT NULL CHECK(TotalCost > 0.00),
                    TradeType TEXT NOT NULL CHECK(TradeType IN ('BUY', 'SELL')),
                    TimeStamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(UserID) REFERENCES usersTbl(UserID) ON DELETE CASCADE
                );
            """)
            
            conn.commit()
            print("[INFO] Database initialized.")

    except sqlite3.Error as e:# handle db error
        print(f"[ERROR] DB init failed: {e}")

if __name__ == "__main__":
    initialize_database()
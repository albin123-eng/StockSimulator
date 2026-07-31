import hashlib
import secrets
import sqlite3
import database

def hash_pass(p_str):
    salt = secrets.token_hex(16)
    h_pass = hashlib.pbkdf2_hmac('sha256', p_str.encode('utf-8'), salt.encode('utf-8'), 100000)# sha256 hashing with 100k iterations
    return f"{salt}${h_pass.hex()}"

def register(usr, p_str):
    if not usr.strip():
        print("[ERROR] Blank username.")
        return False

    pass_hash = hash_pass(p_str)

    try:
        with database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO UsersTbl (Username, HashedPassword) VALUES (?, ?)", (usr, pass_hash))
            conn.commit()
            return True
    except sqlite3.IntegrityError:# User already exists in db
        print(f"[ERROR] User '{usr}' already exists.")
        return False
    except sqlite3.Error as e:
        print(f"[ERROR] DB fail on reg: {e}")
        return False

def login(usr, p_str):
    if not usr.strip() or not p_str.strip():
        return False, "Inputs cannot be empty."

    try:
        with database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT UserID, Username, HashedPassword, Balance FROM UsersTbl WHERE Username = ?", (usr,))
            row = cur.fetchone()
            
            if not row:
                return False, "User not found."

            db_pass = row['HashedPassword']
            salt, stored_h = db_pass.split('$')

            # check input against salt
            inp_h = hashlib.pbkdf2_hmac('sha256', p_str.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

            if inp_h == stored_h:
                s_info = {
                    'user_id': row['UserID'],
                    'username': row['Username'],
                    'balance': row['Balance']
                }
                return True, s_info
            else:
                return False, "Wrong password."

    except sqlite3.Error as e:
        print(f"[ERROR] DB error on login: {e}")
        return False, "DB error occurred."

def check_pass_str(p_str):
    if len(p_str) < 8:
        return False, "Min 8 characters needed."
    if not any(c.isdigit() for c in p_str):
        return False, "Need at least 1 number."
    if not any(c.isupper() for c in p_str):
        return False, "Need at least 1 capital letter."
    if not any(c.islower() for c in p_str):
        return False, "Need at least 1 lowercase letter."
    if not any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for c in p_str):
        return False, "Need at least 1 special character."
    
    return True, "Strong password."

def main():
    while True:
        print("\n--- AUTH TEST MENU ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        c = input("Choice: ").strip()

        if c == '1':
            usr = input("Username: ").strip()
            p_str = input("Password: ").strip()
            
            ok, msg = check_pass_str(p_str)
            if not ok:
                print(f"[VAL ERROR] {msg}")
                continue

            if register(usr, p_str):
                print("[SUCCESS] Registered!")
            else:
                print("[FAILED] Registration failed.")

        elif c == '2':
            usr = input("Username: ").strip()
            p_str = input("Password: ").strip()
            
            ok, res = login(usr, p_str)
            if ok:
                print(f"[SUCCESS] Welcome {res['username']}! Bal: £{res['balance']:.2f}")
            else:
                print(f"[FAILED] {res}")

        elif c == '3':
            print("Exiting...")
            break
        else:
            print("Invalid input.")

if __name__ == "__main__":
    main()
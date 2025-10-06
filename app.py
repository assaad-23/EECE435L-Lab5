from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

DB_PATH = "database.db"

def connect_to_db():
    return sqlite3.connect(DB_PATH)

def create_db_table():
    conn = None
    try:
        conn = connect_to_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                email   TEXT NOT NULL,
                phone   TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            );
        """)
        conn.commit()
        print("User table ready")
    except Exception as e:
        print("Table creation failed:", e)
    finally:
        if conn:
            conn.close()

def row_to_user(row):
    return {
        "user_id": row["user_id"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "address": row["address"],
        "country": row["country"],
    }

def get_users():
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        return [row_to_user(r) for r in rows]
    except Exception as e:
        print("get_users error:", e)
        return []
    finally:
        conn.close()

def get_user_by_id(user_id):
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row_to_user(row) if row else {}
    except Exception as e:
        print("get_user_by_id error:", e)
        return {}
    finally:
        conn.close()

def insert_user(user):
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)",
            (user["name"], user["email"], user["phone"], user["address"], user["country"]),
        )
        conn.commit()
        return get_user_by_id(cur.lastrowid)
    except Exception as e:
        if conn: conn.rollback()
        print("insert_user error:", e)
        return {}
    finally:
        if conn: conn.close()

def update_user(user):
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET name = ?, email = ?, phone = ?, address = ?, country = ? WHERE user_id = ?",
            (user["name"], user["email"], user["phone"], user["address"], user["country"], user["user_id"]),
        )
        conn.commit()
        return get_user_by_id(user["user_id"])
    except Exception as e:
        if conn: conn.rollback()
        print("update_user error:", e)
        return {}
    finally:
        if conn: conn.close()

def delete_user(user_id):
    conn = None
    try:
        conn = connect_to_db()
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return {"status": "User deleted successfully"}
    except Exception as e:
        if conn: conn.rollback()
        print("delete_user error:", e)
        return {"status": "Cannot delete user"}
    finally:
        if conn: conn.close()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/api/users", methods=["GET"])
def api_get_users():
    return jsonify(get_users())

@app.route("/api/users/<int:user_id>", methods=["GET"])
def api_get_user(user_id):
    return jsonify(get_user_by_id(user_id))

@app.route("/api/users/add", methods=["POST"])
def api_add_user():
    user = request.get_json(force=True)
    return jsonify(insert_user(user))

@app.route("/api/users/update", methods=["PUT"])
def api_update_user():
    user = request.get_json(force=True)
    return jsonify(update_user(user))

@app.route("/api/users/delete/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    return jsonify(delete_user(user_id))

if __name__ == "__main__":
    print("Flask API running...") 
    create_db_table()             
    app.run(debug=True)           

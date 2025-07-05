from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv 

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin requests
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# DB connection using environment variables
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

# ✅ Home route to test in browser
@app.route("/")
def home():
    return "✅ Flask backend is running!"

# Input validation function
def validate_input(data):
    if not all(data.values()):
        return "All fields are required."
    if not data["Phone_no"].isdigit() or len(data["Phone_no"]) != 10:
        return "Phone number must be 10 digits."
    if "@" not in data["Email"] or "." not in data["Email"]:
        return "Invalid email address."
    return None

# Duplicate check function
def check_duplicates(cursor, reg_no, email, phone):
    cursor.execute("SELECT * FROM Studentnew WHERE Reg_no = %s", (reg_no,))
    if cursor.fetchone():
        return "RegDuplicate"

    cursor.execute("SELECT * FROM Studentnew WHERE Email = %s AND Phone_no = %s", (email, phone))
    if cursor.fetchone():
        return "FalsePositive"

    cursor.execute("SELECT * FROM Studentnew WHERE Email = %s", (email,))
    if cursor.fetchone():
        return "EmailDuplicate"

    return "Unique"

@app.route("/add", methods=["POST"])
def add_user():
    data = request.get_json()

    reg_no = data.get("Reg_no")
    name = data.get("Name")
    dept = data.get("Department")
    phone = data.get("Phone_no")
    email = data.get("Email")

    form_data = {
        "Reg_no": reg_no,
        "Name": name,
        "Department": dept,
        "Phone_no": phone,
        "Email": email
    }

    validation_error = validate_input(form_data)
    if validation_error:
        return jsonify({"status": "error", "message": validation_error})

    cursor = db.cursor()
    status = check_duplicates(cursor, reg_no, email, phone)

    if status == "RegDuplicate":
        return jsonify({"status": "warning", "message": "Student already exists (Registration number is duplicate)."})
    elif status == "FalsePositive":
        return jsonify({"status": "warning", "message": "Phone number and email already exist in the same record."})
    elif status == "EmailDuplicate":
        return jsonify({"status": "warning", "message": "Email already exists."})
    elif status == "Unique":
        insert_query = """
            INSERT INTO Studentnew (Reg_no, Name, Department, Phone_no, Email)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (reg_no, name, dept, phone, email))
        db.commit()
        return jsonify({"status": "success", "message": "Student added successfully!"})

    return jsonify({"status": "error", "message": "Unknown error occurred."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import os
from fastapi.responses import JSONResponse
from flask import Flask, request, render_template, jsonify, url_for


# Initialize Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# MongoDB Connection
try:
    app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
    mongo = PyMongo(app)

    # Test connection
    mongo.db.command("ping")
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")
    exit(1)  # Stop the app if MongoDB is not connected

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.json
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "Missing data"}), 400

    # Add the user to MongoDB
    user_id = mongo.db.users.insert_one({
        "name": data["name"],
        "email": data["email"]
    }).inserted_id

    return jsonify({"redirect": url_for('welcome', name=data["name"])})

@app.route("/welcome")
def welcome():
    name = request.args.get("name", "Guest")
    return render_template("welcome.html", name=name)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)

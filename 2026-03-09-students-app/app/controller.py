from app import service
from flask import Flask, jsonify, request


# internal function to make sure id and age are int and not string
def normalize_student(student):
    if "id" in student:
        student["id"] = int(student["id"])
    if "age" in student:
        student["age"] = int(student["age"])


students_app = Flask(__name__)


@students_app.route("/")
def home():
    return students_app.send_static_file("index.html")


@students_app.route("/students", methods=["GET"])
def get_students():
    return jsonify(service.get_students())


@students_app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    try:
        student = service.get_student(student_id)
        return jsonify(student)
    except KeyError as e:
        return jsonify({"message": str(e)}), 404


@students_app.route("/students", methods=["POST"])
def add_student():
    student = request.get_json()
    normalize_student(student)
    try:
        student = service.add_student(student)
        return jsonify(student), 201
    except service.ServiceError as e:
        return jsonify({"message": str(e)}), 400


@students_app.put("/students")
def update_student():
    student = request.get_json()
    normalize_student(student)
    try:
        student = service.update_student(student)
        return jsonify(student), 200
    except KeyError as e:
        return jsonify({"message": str(e)}), 404


@students_app.delete("/students/<int:student_id>")
def delete_student(student_id):
    try:
        student = service.delete_student(student_id)
        return jsonify(student)
    except KeyError as e:
        return jsonify({"message": str(e)}), 404


# start the server
if __name__ == "__main__":
    students_app.run(debug=True)

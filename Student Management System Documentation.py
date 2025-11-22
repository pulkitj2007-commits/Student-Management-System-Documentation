import json
import os
import tempfile
from typing import List, Dict, Optional

DATA_FILE = "students.json"
BACKUP_FILE = "students_backup.json"

# -------------------- Helper functions --------------------
def load_data() -> List[Dict]:
    """Load student list from JSON file. Return empty list if file not found or invalid."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, IOError):
        return []

def save_data(students: List[Dict]) -> None:
    """Write students list to file atomically and create a backup copy."""
    # atomic write
    fd, tmp_path = tempfile.mkstemp(prefix="students_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
            json.dump(students, tmpf, indent=2, ensure_ascii=False)
        os.replace(tmp_path, DATA_FILE)
        # create a simple backup as well
        try:
            with open(BACKUP_FILE, "w", encoding="utf-8") as b:
                json.dump(students, b, indent=2, ensure_ascii=False)
        except Exception:
            pass
    except Exception as e:
        print("Error saving data:", e)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def find_by_roll(students: List[Dict], roll: str) -> Optional[Dict]:
    """Return student dict if roll matches, else None."""
    for s in students:
        if s.get("roll") == roll:
            return s
    return None

def input_nonempty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Input cannot be empty. Try again.")

def input_int(prompt: str, allow_blank=False) -> Optional[int]:
    while True:
        val = input(prompt).strip()
        if val == "" and allow_blank:
            return None
        try:
            return int(val)
        except ValueError:
            print("Enter a valid integer.")

def input_float(prompt: str, allow_blank=False) -> Optional[float]:
    while True:
        val = input(prompt).strip()
        if val == "" and allow_blank:
            return None
        try:
            return float(val)
        except ValueError:
            print("Enter a valid number.")

# -------------------- CRUD operations --------------------
def add_student(students: List[Dict]) -> None:
    print("\n--- Add New Student ---")
    roll = input_nonempty("Enter Roll Number: ")
    if find_by_roll(students, roll):
        print(f"A student with roll '{roll}' already exists. Use update instead.")
        return
    name = input_nonempty("Enter Name: ")
    sclass = input_nonempty("Enter Class/Course: ")
    age = input_int("Enter Age: ")
    phone = input_nonempty("Enter Phone Number: ")
    marks = input_float("Enter Marks (e.g. 78.5): ")
    student = {
        "roll": roll,
        "name": name,
        "class": sclass,
        "age": age,
        "phone": phone,
        "marks": marks
    }
    students.append(student)
    print("Student added successfully.")

def display_students(students: List[Dict]) -> None:
    print("\n--- All Students ---")
    if not students:
        print("No student records found.")
        return
    # sort by roll (numeric if possible)
    try:
        sorted_students = sorted(students, key=lambda x: int(x["roll"]))
    except Exception:
        sorted_students = sorted(students, key=lambda x: x["roll"])
    # print table-like view
    print(f"{'Roll':<8}{'Name':<20}{'Class':<10}{'Age':<5}{'Phone':<15}{'Marks':<7}")
    print("-"*65)
    for s in sorted_students:
        print(f"{s.get('roll',''):<8}{s.get('name',''):<20}{s.get('class',''):<10}{str(s.get('age','')):<5}{s.get('phone',''):<15}{str(s.get('marks','')):<7}")
    print("-"*65)
    print(f"Total records: {len(students)}")

def search_student(students: List[Dict]) -> None:
    print("\n--- Search Student ---")
    roll = input_nonempty("Enter Roll Number to search: ")
    s = find_by_roll(students, roll)
    if not s:
        print("Student not found.")
        return
    print("Student Details:")
    for k, v in s.items():
        print(f"  {k.title()}: {v}")

def update_student(students: List[Dict]) -> None:
    print("\n--- Update Student ---")
    roll = input_nonempty("Enter Roll Number to update: ")
    s = find_by_roll(students, roll)
    if not s:
        print("Student not found.")
        return
    print("Press Enter to keep existing value.")
    new_name = input("Name [{}]: ".format(s.get("name"))).strip()
    new_class = input("Class [{}]: ".format(s.get("class"))).strip()
    new_age = input_int("Age [{}]: ".format(s.get("age")), allow_blank=True)
    new_phone = input("Phone [{}]: ".format(s.get("phone"))).strip()
    new_marks = input_float("Marks [{}]: ".format(s.get("marks")), allow_blank=True)

    if new_name:
        s["name"] = new_name
    if new_class:
        s["class"] = new_class
    if new_age is not None:
        s["age"] = new_age
    if new_phone:
        s["phone"] = new_phone
    if new_marks is not None:
        s["marks"] = new_marks

    print("Record updated successfully.")

def delete_student(students: List[Dict]) -> None:
    print("\n--- Delete Student ---")
    roll = input_nonempty("Enter Roll Number to delete: ")
    s = find_by_roll(students, roll)
    if not s:
        print("Student not found.")
        return
    confirm = input(f"Are you sure you want to delete {s.get('name')} (roll {roll})? (y/N): ").strip().lower()
    if confirm == "y":
        students.remove(s)
        print("Student deleted.")
    else:
        print("Deletion canceled.")

# -------------------- Main loop --------------------
def main():
    students = load_data()
    while True:
        print("\n===== Student Management System =====")
        print("1. Add Student")
        print("2. Display Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Exit")
        choice = input("Enter choice (1-6): ").strip()
        if choice == "1":
            add_student(students)
            save_data(students)
        elif choice == "2":
            display_students(students)
        elif choice == "3":
            search_student(students)
        elif choice == "4":
            update_student(students)
            save_data(students)
        elif choice == "5":
            delete_student(students)
            save_data(students)
        elif choice == "6":
            save_data(students)
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Enter 1-6.")

if __name__ == "__main__":
    main()

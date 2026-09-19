import os
import sys

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "student_grades.txt")


class Student:
    """Store a student's information and calculate grade details."""

    def __init__(self, name, student_id, test1, test2, test3):
        if not name or not name.strip():
            raise ValueError("Student name cannot be empty.")
        if not student_id or not student_id.strip():
            raise ValueError("Student ID cannot be empty.")

        self.name = name.strip()
        self.id = student_id.strip()
        self.test_scores = [
            self._validate_score(test1, "Test 1"),
            self._validate_score(test2, "Test 2"),
            self._validate_score(test3, "Test 3"),
        ]
        self.average = self.calculate_average()
        self.grade = self.calculate_letter_grade()

    def _validate_score(self, score, test_name):
        try:
            score_value = float(score)
        except (TypeError, ValueError):
            raise ValueError(f"{test_name} must be a valid number.")

        if score_value < 0 or score_value > 100:
            raise ValueError(f"{test_name} must be between 0 and 100.")
        return score_value

    def calculate_average(self):
        return sum(self.test_scores) / len(self.test_scores)

    def calculate_letter_grade(self):
        average = self.calculate_average()

        if average >= 90:
            return "A"
        if average >= 80:
            return "B"
        if average >= 70:
            return "C"
        if average >= 60:
            return "D"
        return "F"

    def to_file_line(self):
        return (
            f"{self.name}|{self.id}|{self.test_scores[0]:.2f}|{self.test_scores[1]:.2f}|{self.test_scores[2]:.2f}|"
            f"{self.average:.2f}|{self.grade}"
        )

    @classmethod
    def from_file_line(cls, line):
        parts = line.strip().split("|")
        if len(parts) != 7:
            raise ValueError("Invalid student record format.")

        name, student_id, test1, test2, test3, average, grade = parts
        student = cls(name, student_id, float(test1), float(test2), float(test3))
        student.average = float(average)
        student.grade = grade
        return student

    def __str__(self):
        return (
            f"{self.name:<20} | {self.id:<10} | {self.test_scores[0]:>7.2f} | {self.test_scores[1]:>7.2f} | "
            f"{self.test_scores[2]:>7.2f} | {self.average:>8.2f} | {self.grade}"
        )


def load_students():
    records = []
    if not os.path.exists(DATA_FILE):
        print("No saved student file found. Starting with an empty list.")
        return records

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(Student.from_file_line(line))
                except ValueError as error:
                    print(f"Warning: line {line_number} was skipped because it was invalid ({error}).")
    except OSError as error:
        print(f"Error reading file: {error}")
        return []

    return records


def save_students(records):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            for record in records:
                file.write(record.to_file_line() + "\n")
        print(f"Student records saved to {os.path.basename(DATA_FILE)}.")
    except OSError as error:
        print(f"Error saving file: {error}")


def display_all_students(records):
    if not records:
        print("No student records found.")
        return

    ordered_records = sorted(records, key=lambda record: record.name.lower())
    headers = ["Name", "ID", "Test 1", "Test 2", "Test 3", "Average", "Grade"]
    rows = [
        [
            record.name,
            record.id,
            f"{record.test_scores[0]:.2f}",
            f"{record.test_scores[1]:.2f}",
            f"{record.test_scores[2]:.2f}",
            f"{record.average:.2f}",
            record.grade,
        ]
        for record in ordered_records
    ]

    widths = [len(str(header)) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def format_row(values):
        return " | ".join(str(value).ljust(widths[index]) for index, value in enumerate(values))

    border = "-+-".join("-" * width for width in widths)
    print("\nStudent Grade Records")
    print(format_row(headers))
    print(border)
    for row in rows:
        print(format_row(row))


def search_student(records, name):
    search_name = name.strip().lower()
    matches = [record for record in records if record.name.lower() == search_name]

    if not matches:
        print(f"No student named '{name}' was found.")
        return

    print(f"\nSearch results for '{name}':")
    display_all_students(matches)


def class_statistics(records):
    if not records:
        print("No student records available for class statistics.")
        return

    highest_record = max(records, key=lambda record: record.average)
    lowest_record = min(records, key=lambda record: record.average)
    class_average = sum(record.average for record in records) / len(records)

    print("\nClass Statistics")
    print(f"Highest Average: {highest_record.name} ({highest_record.id}) - {highest_record.average:.2f} ({highest_record.grade})")
    print(f"Lowest Average: {lowest_record.name} ({lowest_record.id}) - {lowest_record.average:.2f} ({lowest_record.grade})")
    print(f"Class Average: {class_average:.2f}")


def add_student(records):
    try:
        name = input("Enter student name: ").strip()
        student_id = input("Enter student ID: ").strip()

        while True:
            try:
                test1 = float(input("Enter Test 1 score (0-100): "))
                test2 = float(input("Enter Test 2 score (0-100): "))
                test3 = float(input("Enter Test 3 score (0-100): "))
                break
            except ValueError:
                print("Please enter valid numeric scores for all tests.")

        student = Student(name, student_id, test1, test2, test3)
        records.append(student)
        save_students(records)

        print("\nStudent added successfully.")
        print(f"Name: {student.name}")
        print(f"ID: {student.id}")
        print(f"Average: {student.average:.2f}")
        print(f"Grade: {student.grade}")
        print(f"Saved to {os.path.basename(DATA_FILE)}.")
    except ValueError as error:
        print(f"Error: {error}")


def get_menu_choice():
    choice = input("Select an option (1-7, or type ESC): ").strip()
    if choice.upper() == "ESC" or choice == "\x1b":
        return "ESC"
    return choice


def print_menu():
    print("\n=== Student Grade Manager ===")
    print("1. Add new student record")
    print("2. Display all students")
    print("3. Search student")
    print("4. Class statistics")
    print("5. Save records")
    print("6. Load records")
    print("7. Exit (ESC)")


def main():
    students = load_students()
    print(f"Loaded {len(students)} student record(s) from {os.path.basename(DATA_FILE)}.")

    while True:
        print_menu()
        choice = get_menu_choice()

        if choice == "ESC":
            print("Exiting program...")
            save_students(students)
            break

        if choice == "":
            print("Please enter a valid option.")
            continue

        try:
            if choice == "1":
                add_student(students)
            elif choice == "2":
                display_all_students(students)
            elif choice == "3":
                name = input("Enter student name to search: ").strip()
                search_student(students, name)
            elif choice == "4":
                class_statistics(students)
            elif choice == "5":
                save_students(students)
            elif choice == "6":
                students = load_students()
                print(f"Loaded {len(students)} student record(s) from {os.path.basename(DATA_FILE)}.")
            elif choice == "7":
                save_students(students)
                print("Goodbye!")
                break
            else:
                print("Invalid selection. Please choose a number from 1 to 7.")
        except Exception as error:
            print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()
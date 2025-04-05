import json
import random
from random import choice, choices
from itertools import permutations


def classes():
    return {"Algebra 1": 1, "Algebra 2": 1, "Precalculus": 1,
            "Algebra 1 H": 1, "Algebra 2 H": 1, "Precalculus H": 1,
            "English 1": 1, "English 2": 1, "English 3": 1,
            "English 1 H": 1, "English 2 H": 1, "English 3 H": 1,
            "ESS": 1, "Bio": 1, "Chem": 1,
            "ESS H": 1, "Bio H": 1, "Chem H": 1,
            "American Perspectives 1": 1, "CWS": 1, "Civics": 1,
            "American Perspectives 1 H": 1, "CWS H": 1, "Civics H": 1,
            "Spanish 1": 1, "Spanish 1 H": 1,
            "Statistics": 0.5, "Accounting": 1, "Accounting H": 1,
            "Creative Writing": 0.5, "AP Seminar": 1,
            "Gym": 0.5, "Health": 0.5, "FCS": 0.5, "PGP": 0.5,
            "CTC": 1, "Lunch": 1,
            "Engineering": 1, "Computer Science": 1, "Spanish 1": 1, "Spanish 1 H": 1
            }


def random_courses():
    classes = {"Algebra 1": 1, "Algebra 2": 1, "Precalculus": 1,
               "Algebra 1 H": 1, "Algebra 2 H": 1, "Precalculus H": 1,
               "English 1": 1, "English 2": 1, "English 3": 1,
               "English 1 H": 1, "English 2 H": 1, "English 3 H": 1,
               "ESS": 1, "Bio": 1, "Chem": 1,
               "ESS H": 1, "Bio H": 1, "Chem H": 1,
               "American Perspectives 1": 1, "CWS": 1, "Civics": 1,
               "American Perspectives 1 H": 1, "CWS H": 1, "Civics H": 1,
               "Spanish 1": 1, "Spanish 1 H": 1,
               "Statistics": 0.5, "Accounting": 1, "Accounting H": 1,
               "Creative Writing": 0.5, "AP Seminar": 1,
               "Gym": 0.5, "Health": 0.5, "FCS": 0.5, "PGP": 0.5,
               "CTC": 1, "Lunch": 1}

    required_courses = []
    grade = random.randint(9, 11)
    if random.randint(0, 5) == 5:
        required_courses.append("CTC")
        match grade:
            case 9:
                required_courses.append(choice(["English 1", "English 1 H"]))
            case 10:
                required_courses.append(choice(["English 2", "English 2 H"]))
            case 11:
                required_courses.append(choice(["English 3", "English 3 H"]))
    else:
        match grade:
            case 9:
                required_courses.append(choice(["Algebra 1", "Algebra 1 H"]))
                required_courses.append(choice(["English 1", "English 1 H"]))
                required_courses.append(choice(["ESS", "ESS H"]))
                required_courses.append(choice(["American Perspectives 1", "American Perspectives 1 H"]))
                required_courses.append("Health")
            case 10:
                required_courses.append(choice(["Algebra 2", "Algebra 2 H"]))
                required_courses.append(choice(["English 2", "English 2 H"]))
                required_courses.append(choice(["Bio", "Bio H"]))
                required_courses.append(choice(["CWS", "CWS H"]))
                required_courses.append("FCS")
            case 11:
                required_courses.append(choice(["Precalculus H", "Precalculus H"]))
                required_courses.append(choice(["English 3", "English 3 H"]))
                required_courses.append(choice(["Chem", "Chem H"]))
                required_courses.append(choice(["Civics", "Civics H"]))
                required_courses.append("PGP")

    elective_courses = ["Creative Writing", "AP Seminar", choice(["Accounting", "Accounting H"]),
                        "Engineering", "Computer Science", choice(["Spanish 1", "Spanish 1 H"])]

    elective_courses = random.sample(elective_courses, 4)
    elective_courses += [choice(["Statistics", "Creative Writing", "Gym"])]
    elective_courses = dict(zip(elective_courses, [5, 4, 3, 2]))

    return (required_courses, elective_courses)


def create_students(alphabet: str, file: str):
    students = ["".join(p) for p in permutations(alphabet)]
    required_courses = []
    elective_courses = []
    for s in students:
        requireds, electives = random_courses()
        required_courses.append(requireds)
        elective_courses.append(electives)

    course_dict = list(
        {"required": required_courses[i], "elective": elective_courses[i]} for i in range(len(students)))
    data = dict(zip(students, course_dict))

    with open("student_test.json", "w") as file:
        json.dump(data, file)


if __name__ == "__main__":
    create_students("abcde", "student_test.json")

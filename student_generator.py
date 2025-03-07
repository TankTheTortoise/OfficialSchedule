import json
import random
from random import choice, choices
from itertools import permutations


def classes():
    return ["Algebra 1", "Algebra 2", "Precalculus",
            "Algebra 1 H", "Algebra 2 H", "Precalculus H",
            "English 1", "English 2", "English 3",
            "English 1 H", "English 2 H", "English 3 H",
            "ESS", "Bio", "Chem",
            "ESS H", "Bio H", "Chem H",
            "American Perspectives 1", "CWS", "Civics",
            "American Perspectives 1 H", "CWS H", "Civics H",
            "Spanish 1", "Spanish 1 H",
            "Statistics", "Accounting", "Accounting H",
            "Creative Writing", "AP Seminar",
            "CTC", "Lunch",

            "Accounting", "Accounting H",
            "Engineering", "Computer Science", "Spanish 1", "Spanish 1 H"
            ]



def random_courses():
    classes = ["Algebra 1", "Algebra 2", "Precalculus",
               "Algebra 1 H", "Algebra 2 H", "Precalculus H",
               "English 1", "English 2", "English 3",
               "English 1 H", "English 2 H", "English 3 H",
               "ESS", "Bio", "Chem",
               "ESS H", "Bio H", "Chem H",
               "American Perspectives 1", "CWS", "Civics",
               "American Perspectives 1 H", "CWS H", "Civics H",
               "Spanish 1", "Spanish 1 H",
               "Statistics", "Accounting", "Accounting H",
               "Creative Writing", "AP Seminar",
               "CTC", "Lunch"]

    required_courses = []
    elective_courses = []
    grade = random.randint(9, 11)

    match grade:
        case 9:
            required_courses.append(choice(["Algebra 1", "Algebra 1 H"]))
            required_courses.append(choice(["English 1", "English 1 H"]))
            required_courses.append(choice(["ESS", "ESS H"]))
            required_courses.append(choice(["American Perspectives 1", "American Perspectives 1 H"]))
        case 10:
            required_courses.append(choice(["Algebra 2", "Algebra 2 H"]))
            required_courses.append(choice(["English 2", "English 2 H"]))
            required_courses.append(choice(["Bio", "Bio H"]))
            required_courses.append(choice(["CWS", "CWS H"]))
        case 11:
            required_courses.append(choice(["Precalculus H", "Precalculus H"]))
            required_courses.append(choice(["English 3", "English 3 H"]))
            required_courses.append(choice(["Chem", "Chem H"]))
            required_courses.append(choice(["Civics", "Civics H"]))
    if random.randint(0, 1) == 1:
        required_courses.append("CTC")

    elective_courses = ["Statistics", "Creative Writing", "AP Seminar", choice(["Accounting", "Accounting H"]),
                        "Engineering", "Computer Science", choice(["Spanish 1", "Spanish 1 H"])]

    elective_courses = random.sample(elective_courses, 4)
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

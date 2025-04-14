import numpy as np


def get_courses(students: [str], students_classes, periods, classes, quarters) -> np.ndarray:
    schedule = np.full((8, 2*len(students)), "", dtype="U20")
    for i in range(len(students)):
        for p in periods:
            for c in classes:
                for q in quarters:
                    if students_classes[students[i]][c][p][q].value() == 1:
                        schedule[p - 1][q - 1 + i*2] = c

    return schedule


def student_keys(students: [str]):
    total = []
    for i in range(len(students)):
        for q in ["1", "2"]:
            total.append(f"Q{q}: {students[i]}")
    return total
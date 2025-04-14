import copy
import sys

import time
from tkinter.font import names

import networkx as nx
import grinpy
import pulp
from pulp import *
import pandas as pd
import numpy as np
import json

from student_generator import classes
from display import *

pd.set_option('display.max_columns', None)

max_students = 50
num_of_classes = 8

prob = LpProblem("Scheduling", LpMaximize)

with open("student_test.json") as f:
    student_choice = json.load(f)

with open("teacher_preference.json") as f:
    teacher_preference = json.load(f)

student_choice = pd.DataFrame.from_dict(student_choice)
teacher_preference = pd.DataFrame.from_dict(teacher_preference)

# Get numbered list of classes teacher can teach. Find the disjunct of that and 1...10
students = student_choice.keys().tolist()
teachers = teacher_preference.keys().tolist()

# Common Variables
periods = [i for i in range(1, 8 + 1)]
classes_with_credits = classes()
half_credit = [c for c in classes_with_credits.keys() if classes_with_credits[c] < 1]

classes = list(classes_with_credits.keys())
print(classes_with_credits["Algebra 1"])
quarters = [1, 2]

student_preference = [[0 for i in range(num_of_classes)] for student in students]
students_required = [[] for student in students]
teacher_desirability = [[0 for i in range(num_of_classes)] for teacher in teachers]
for i in range(len(students)):
    students_required[i] = student_choice[students[i]]["required"]

teacher_able = []
teacher_unable = []
for i in range(teacher_preference.shape[1]):
    teacher_able.append(teacher_preference.loc["able"].iloc[i])
    # Teacher unable kept overwriting teacher_able, so I deep coppied it
    deep_copy = copy.deepcopy(teacher_able)
    teacher_unable.append(list(set(classes).difference(set(deep_copy[i]))))

# inverse Set.intersection
for i in range(len(teachers)):
    for j in range(len(teacher_preference[teachers[i]]["desired"])):
        # teacher_desirability[i][teacher_preference[teachers[i]]["desired"][j] - 1] = 4 - j
        ...

students_classes = LpVariable.dicts("Student's_classes", (students, classes, periods, quarters), cat=LpBinary)

teachers_classes = LpVariable.dicts("Teacher's_classes", (teachers, classes, periods, quarters), cat=LpBinary)

student_desirability = makeDict([students, ], student_preference)

# teacher_desirability = makeDict([teachers, classes], teacher_desirability)
students_required = makeDict([students], students_required)
teacher_unable = makeDict([teachers], teacher_unable)
teacher_able = makeDict([teachers], teacher_able)

CTC_students = []
for s in students:
    if "CTC" in students_required[s]:
        CTC_students.append(s)

AM_CTC = LpVariable.dicts("AM_CTC", indices=CTC_students, cat=LpBinary)

for t in teachers:
    for p in periods:
        prob += lpSum(
            [teachers_classes[t][c][p][q] * classes_with_credits[c] for c in teacher_able[t] for q in quarters]) <= 1
        # I removed this line that was making teachers not always assigned
        # The other two constraints are equivalent to what I mean
        # prob += lpSum([teachers_classes[t][str(c)][p] for c in classes]) == 1
        for q in quarters:
            prob += lpSum([teachers_classes[t][c][p][q] for c in teacher_unable[t]]) == 0

for s in students:
    for p in periods:
        prob += lpSum([students_classes[s][c][p][1] for c in classes]) >= lpSum(
            [students_classes[s][c][p][2] for c in classes])

        prob += lpSum([students_classes[s][c][p][q] * classes_with_credits[c] for q in quarters for c in classes]) == 1
        for q in quarters:
            prob += lpSum([students_classes[s][c][p][q] for c in classes]) <= 1
            match student_choice[s]["grade"]:
                case 9:
                    prob += lpSum([students_classes[s][c][p][q] for c in ["FCS", "PGP"]]) == 0
                case 10:
                    prob += lpSum([students_classes[s][c][p][q] for c in ["Health", "PGP"]]) == 0
                case 11:
                    prob += lpSum([students_classes[s][c][p][q] for c in ["FCS", "Health"]]) == 0

    for c in classes:
        if c in students_required[s]:
            if c == "CTC":
                # There is no half year CTC, so Q1 is used. Only Q1 means full year.
                prob += lpSum([students_classes[s][c][p][1] for p in [1, 2, 3, 4]]) == 4 * AM_CTC[s]
                prob += lpSum([students_classes[s][c][p][1] for p in [5, 6, 7, 8]]) == 4 * (1 - AM_CTC[s])
            else:
                prob += lpSum([students_classes[s][c][p][q] for p in periods for q in quarters]) == 1

        else:
            prob += lpSum([students_classes[s][c][p][q] for p in periods for q in quarters]) <= 1

    if s not in CTC_students:
        prob += lpSum([students_classes[s]["Lunch"][p][1] for p in [4, 5, 6, 7]]) == 1

for p in periods:
    for c in classes:
        if c == "CTC":
            continue
        elif c == "Lunch":
            prob += lpSum([students_classes[s][c][p][1] for s in students]) <= 350
        else:
            for q in quarters:
                prob += lpSum([students_classes[s][c][p][q] for s in students]) <= max_students * lpSum(
                    [teachers_classes[t][c][p][q] for t in teachers])
                # Only one teacher per class
                prob += lpSum([teachers_classes[t][c][p][q] for t in teachers]) <= 1

# Must take class algebra 2 if you want to take stat
for s in students:
    # prob += lpSum(students_classes[s][8][p] for p in periods) >= lpSum(students_classes[s]["6"][p] for p in periods)
    ...

# New constraint
# Teacher either has class or prep period


## Objective ##

teacher_happiness = []
for t in teachers:
    for c in teacher_preference[t]["desired"]:
        teacher_happiness.append(lpSum([teachers_classes[t][c][p][q] for p in periods for q in quarters]))

prob += lpSum(
    [students_classes[s][c][p][q] * student_choice[s]["elective"][c] for
     s in students for c in student_choice[s]["elective"] for p in periods for q in quarters]) + lpSum(
    teacher_happiness)

start = time()
prob.solve(getSolver("HiGHS"))
print(f"Finished in {time() - start:.2f}s")

print(f"There are {len(students)} students")
print(f"There are {len(teachers)} teachers")
print(f"The happiness per student is {value(prob.objective) / len(students):.2f}")




headers = student_keys(students)
courses = pd.DataFrame(get_courses(students, students_classes, periods, classes, quarters), columns=headers, index = periods)



courses.to_csv("schedule.csv")


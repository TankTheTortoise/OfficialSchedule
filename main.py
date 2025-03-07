import copy
import sys

import time

import networkx as nx
import grinpy
import pulp
from pulp import *
import pandas as pd
import numpy as np
import json

from student_generator import classes

max_students = 140
num_of_classes = 10

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

periods = [i for i in range(1, 8)]
classes = classes()


students_required = [[] for student in students]
for i in range(len(students)):
    students_required[i] = student_choice[students[i]]["required"]

teacher_able = []
teacher_unable = []
for i in range(teacher_preference.shape[1]):
    teacher_able.append(teacher_preference.loc["able"].iloc[i])
    # Teacher unable kept overwriting teacher_able, so I deep coppied it
    deep_copy = copy.deepcopy(teacher_able)
    teacher_unable.append(list(set(classes).difference(set(deep_copy[i]))))

students_classes = LpVariable.dicts("Student's_classes", (students, classes, periods), cat=LpBinary)
teachers_classes = LpVariable.dicts("Teacher's_classes", (teachers, classes, periods), cat=LpBinary)

students_required = makeDict([students], students_required)
teacher_unable = makeDict([teachers], teacher_unable)
teacher_able = makeDict([teachers], teacher_able)

for t in teachers:
    for p in periods:
        prob += lpSum([teachers_classes[t][c][p] for c in teacher_able[t]]) <= 1
        # I removed this line that was making teachers not always assigned
        # The other two constraints are equivalent to what I mean
        # prob += lpSum([teachers_classes[t][str(c)][p] for c in classes]) == 1
        prob += lpSum([teachers_classes[t][c][p] for c in teacher_unable[t]]) == 0

for s in students:
    for p in periods:
        prob += lpSum([students_classes[s][c][p] for c in classes]) == 1
    for c in classes:
        prob += lpSum([students_classes[s][c][p] for p in periods]) <= 1

for s in students:
    for r in students_required[s]:
        prob += lpSum([students_classes[s][r][p] for p in periods]) == 1

for p in periods:
    for c in classes:
        if c == "CTC" or c == "Lunch":
            continue
        prob += lpSum([students_classes[s][c][p] for s in students]) <= max_students * lpSum(
            [teachers_classes[t][c][p] for t in teachers])
        # Only one teacher per class
        prob += lpSum([teachers_classes[t][c][p] for t in teachers]) <= 1

# Must take class algebra 2 if you want to take stat
for s in students:
    # prob += lpSum(students_classes[s][8][p] for p in periods) >= lpSum(students_classes[s]["6"][p] for p in periods)
    ...

# New constraint
# Teacher either has class or prep period


teacher_happiness = []
for t in teachers:
    for c in teacher_preference[t]["desired"]:
        teacher_happiness.append(lpSum([teachers_classes[t][c][p] for p in periods]))

prob += lpSum(
    [students_classes[s][c][p] * student_choice[s]["elective"][c] for
     s in students for c in student_choice[s]["elective"] for p in periods]) + lpSum(teacher_happiness)

start = time()
prob.solve(getSolver("HiGHS"))
print(f"Finished in {time() - start:.2f}s")

trues = 0
falses = 0
is_teacher = False
with open("schedule.csv", "w") as file:
    for s in students:
        if s != students[-1]:
            file.write(f"{s},")
        else:
            file.write(f"{s}")

    file.write("\n")
    for p in periods:
        for s in students:
            for c in classes:
                if students_classes[s][c][p].value() == 1:

                    if c == "CTC" or c == "Lunch":
                        trues += 1
                        if s == students[-1]:
                            file.write(f"{c}")
                        else:
                            file.write(f"{c},")
                    else:
                        for t in teachers:

                            if teachers_classes[t][c][p].value() == 1:
                                if c in teacher_able[t]:
                                    trues += 1
                                else:
                                    falses += 1
                                if s == students[-1]:
                                    file.write(f"{c}:{t}")
                                else:
                                    file.write(f"{c}:{t},")

        file.write(f"\n")

print(f"{trues}/{len(students) * len(periods)} Correct")

print(f"There are {len(students)} students")
print(f"There are {len(teachers)} teachers")
print(f"The happiness per student is {value(prob.objective) / len(students):.2f}")

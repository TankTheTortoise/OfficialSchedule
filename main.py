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
print(student_choice["abc"]["elective"]["Accounting"])
# Get numbered list of classes teacher can teach. Find the disjunct of that and 1...10
students = student_choice.keys().tolist()
teachers = teacher_preference.keys().tolist()
periods = [i for i in range(1, 5)]
classes = classes()
print(classes)

student_preference = [[0 for i in range(num_of_classes)] for student in students]
students_required = [[] for student in students]
teacher_desirability = [[0 for i in range(num_of_classes)] for teacher in teachers]
for i in range(len(students)):
    for j in range(4):
        student_preference[i][student_choice[students[i]]["elective"][j] - 1] = 4 - j
        student_preference[i][student_choice[students[i]]["elective"][j] - 1] = 4 - j
        student_preference[i][student_choice[students[i]]["elective"][j] - 1] = 4 - j
        student_preference[i][student_choice[students[i]]["elective"][j] - 1] = 4 - j
    students_required[i] = student_choice[students[i]]["required"]


teacher_able = []
teacher_unable = []
for i in range(teacher_preference.shape[1]):
    teacher_able.append(teacher_preference.loc["able"].iloc[i])
    teacher_unable=teacher_able
    teacher_unable[i] = list(set(range(1, num_of_classes+1)).difference(set(teacher_unable[i])))
print(teacher_unable)
# inverse Set.intersection

for i in range(len(teachers)):
    for j in range(len(teacher_preference[teachers[i]]["desired"])):
        teacher_desirability[i][teacher_preference[teachers[i]]["desired"][j] - 1] = 4 - j

students_classes = LpVariable.dicts("Student's_classes", (students, classes, periods), cat=LpBinary)
teachers_classes = LpVariable.dicts("Teacher's_classes", (teachers, classes, periods), cat=LpBinary)
student_desirability = makeDict([students, ], student_preference)
teacher_desirability = makeDict([teachers, classes], teacher_desirability)
students_required = makeDict([students], students_required)
teacher_unable = makeDict([teachers], teacher_unable)
teacher_able = makeDict([teachers], teacher_able)

for t in teachers:
    for p in periods:
        prob += lpSum([teachers_classes[t][str(c)][p] for c in teacher_able[t]]) <= 1
        # I removed this line that was making teachers not always assigned
        # The other two constraints are equivalent to what I mean
        # prob += lpSum([teachers_classes[t][str(c)][p] for c in classes]) == 1
        prob += lpSum([teachers_classes[t][str(c)][p] for c in teacher_unable[t]]) == 0


for s in students:
    for p in periods:
        prob += lpSum([students_classes[s][c][p] for c in classes]) == 1
    for c in classes:
        prob += lpSum([students_classes[s][c][p] for p in periods])<=1

for s in students:
    for r in students_required[s]:
        prob += lpSum([students_classes[s][str(r)][p] for p in periods]) == 1

for p in periods:
    for c in classes:
        prob += lpSum([students_classes[s][c][p] for s in students]) <= max_students * lpSum(
            [teachers_classes[t][c][p] for t in teachers])
        # Only one teacher per class
        prob += lpSum([teachers_classes[t][c][p] for t in teachers]) <= 1

# Must take class 8 if you take class 6
for s in students:
    prob += lpSum(students_classes[s]["8"][p] for p in periods) >= lpSum(students_classes[s]["6"][p] for p in periods)

# New constraint
# Teacher either has class or prep period

prob += lpSum(
    [students_classes[s][c][p] * student_desirability[s][c] + teachers_classes[t][c][p] * teacher_desirability[t][c] for
     s in students for c in classes for p in periods for t in
     teachers])
start = time()
prob.solve(getSolver("HiGHS"))
print(f"Finished in {time() - start:.2f}s")

trues = 0
falses = 0
with open("schedule.csv", "w") as file:
    for s in students:
        file.write(f"{s},")
    file.write("\n")
    for p in periods:
        for s in students:
            for c in classes:
                if students_classes[s][c][p].value() == 1:
                    for t in teachers:
                        if teachers_classes[t][c][p].value() == 1:
                            match t:
                                case "Pricci":
                                    if int(c) % 2 != 0:
                                        trues += 1
                                    else:
                                        falses += 1
                                case "Burchell":
                                    if int(c) % 2 != 0:
                                        trues += 1
                                    else:
                                        falses += 1
                                case "Adair":
                                    if int(c) % 2 == 0:
                                        trues += 1
                                    else:
                                        falses += 1
                                case "Pryle":
                                    if int(c) % 2 == 0:
                                        trues += 1
                                    else:
                                        falses += 1
                                case "Brown":
                                    if int(c) % 2 != 0:
                                        trues += 1
                                    else:
                                        falses += 1
                                case "Kelly":
                                    if int(c) % 2 == 0:
                                        trues += 1
                                    else:
                                        falses += 1
                            if s == students[-1]:
                                file.write(f"{c}:{t}")
                            else:
                                file.write(f"{c}:{t},")

        file.write(f"\n")

print(f"{trues}/{len(students)*len(periods)} Correct")

print(f"There are {len(students)} students")
print(f"There are {len(teachers)} teachers")
print(f"The happiness per student is {value(prob.objective)/len(students):.2f}")

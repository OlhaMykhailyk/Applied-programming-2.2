from Lab5 import Collection, Document, build_condition

col = Collection()

col.add(Document({
    "id": 1,
    "name": "Anna",
    "age": 20,
    "grades": [90, 80, 100]
}))

col.add(Document({
    "id": 2,
    "name": "Ivan",
    "age": 21,
    "grades": [60, 70, 75]
}))

col.add(Document({
    "id": 3,
    "name": "Maria",
    "age": 19,
    "grades": [95, 100, 98]
}))

print("Усі студенти:")
print(col.documents)

print("\nСередній бал Anna:")
print(col.average_grade(1))

print("\nМінімальна оцінка Ivan:")
print(col.min_grade(2))

print("\nМаксимальна оцінка Maria:")
print(col.max_grade(3))

print("\nСортування за середнім балом:")
students = col.sort_by_average_grade(reverse=True)

for s in students:
    print(
        s["name"],
        "->",
        sum(s["grades"]) / len(s["grades"])
    )

print("\nПошук студентів старших за 19:")

cond = build_condition("age", ">", 19)

print(col.find(cond))

print("\nОновлення віку Anna:")

col.update_by_id(1, "age", 22)

print(col.documents[1].data)

print("\nГрупування за віком:")

print(col.groupby("age"))

print("\nЗбереження у файл:")
col.save("students.json")

print("Дані збережено.")

print("\nЗавантаження з файлу:")

new_col = Collection()
new_col.load("students.json")

print(new_col.documents)
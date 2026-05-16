import json
import unittest


class Document:
    def __init__(self, data):
        if not isinstance(data, dict):
            raise ValueError("Invalid document")
        if "id" not in data:
            raise ValueError("Document must contain id")
        self.data = data


class Collection:
    def __init__(self):
        self.documents = {}

    def add(self, doc):
        doc_id = doc.data["id"]
        if doc_id in self.documents:
            raise ValueError("Duplicate id")
        self.documents[doc_id] = doc

    def delete_by_id(self, id_):
        if id_ not in self.documents:
            raise ValueError("Document not found")
        del self.documents[id_]

    def delete_by_condition(self, condition):
        ids = [i for i, d in self.documents.items() if condition(d.data)]
        for i in ids:
            del self.documents[i]

    def update_by_id(self, id_, field, value):
        if id_ not in self.documents:
            raise ValueError("Document not found")

        if field == "id":
            raise ValueError("Cannot update id")

        self._set_field(self.documents[id_].data, field, value)

    def update_by_condition(self, condition, field, value):
        if field == "id":
            raise ValueError("Cannot update id")

        for doc in self.documents.values():
            if condition(doc.data):
                self._set_field(doc.data, field, value)

    def find(self, condition, sort_field=None, reverse=False):
        results = [
            doc.data
            for doc in self.documents.values()
            if condition(doc.data)
        ]

        if sort_field:
            def key_func(d):
                try:
                    return self._get_field(d, sort_field)
                except ValueError:
                    return None

            results.sort(
                key=lambda x: (
                    key_func(x) is None,
                    key_func(x)
                ),
                reverse=reverse
            )

        return results

    def aggregate(self, op, field=None):
        if op == "count":
            return len(self.documents)

        values = []

        for doc in self.documents.values():
            try:
                v = self._get_field(doc.data, field)

                if isinstance(v, (int, float)):
                    values.append(v)

            except ValueError:
                continue

        if not values:
            raise ValueError("No numeric data")

        if op == "sum":
            return sum(values)

        if op == "avg":
            return sum(values) / len(values)

        if op == "min":
            return min(values)

        if op == "max":
            return max(values)

        raise ValueError("Unknown operation")

    def groupby(self, field):
        result = {}

        for doc in self.documents.values():
            try:
                key = self._get_field(doc.data, field)

                if isinstance(key, (dict, list)):
                    key = json.dumps(key, sort_keys=True)

                result.setdefault(key, []).append(doc.data)

            except ValueError:
                continue

        return result

    def average_grade(self, id_):
        if id_ not in self.documents:
            raise ValueError("Document not found")

        grades = self.documents[id_].data.get("grades")

        if not isinstance(grades, list) or not grades:
            raise ValueError("Grades not found")

        numeric = [g for g in grades if isinstance(g, (int, float))]

        if not numeric:
            raise ValueError("No numeric grades")

        return sum(numeric) / len(numeric)

    def min_grade(self, id_):
        grades = self.documents[id_].data.get("grades")

        if not grades:
            raise ValueError("Grades not found")

        return min(grades)

    def max_grade(self, id_):
        grades = self.documents[id_].data.get("grades")

        if not grades:
            raise ValueError("Grades not found")

        return max(grades)

    def sort_by_average_grade(self, reverse=False):
        students = []

        for doc in self.documents.values():
            try:
                avg = self.average_grade(doc.data["id"])
                students.append((avg, doc.data))
            except ValueError:
                continue

        students.sort(key=lambda x: x[0], reverse=reverse)

        return [student[1] for student in students]

    def save(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                [d.data for d in self.documents.values()],
                f,
                ensure_ascii=False,
                indent=2
            )

    def load(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.documents = {}

        for d in data:
            self.add(Document(d))

    def _get_field(self, data, field):
        parts = field.split(".")

        for p in parts:
            if isinstance(data, dict) and p in data:
                data = data[p]
            else:
                raise ValueError("Field not found")

        return data

    def _set_field(self, data, field, value):
        parts = field.split(".")

        for p in parts[:-1]:
            if p not in data:
                data[p] = {}

            elif not isinstance(data[p], dict):
                raise ValueError(
                    "Cannot overwrite non-object field"
                )

            data = data[p]

        data[parts[-1]] = value


def get_nested(data, field):
    parts = field.split(".")

    for p in parts:
        if isinstance(data, dict) and p in data:
            data = data[p]
        else:
            raise ValueError("Field not found")

    return data


def build_condition(field, op, value):
    def condition(doc):
        try:
            v = get_nested(doc, field)

        except ValueError:
            return False

        if op == "==":
            return v == value

        if op == ">":
            return isinstance(v, (int, float)) and v > value

        if op == "<":
            return isinstance(v, (int, float)) and v < value

        if op == ">=":
            return isinstance(v, (int, float)) and v >= value

        if op == "<=":
            return isinstance(v, (int, float)) and v <= value

        if op == "in":
            return isinstance(v, list) and value in v

        if op == "exists":
            return True

        return False

    return condition


class TestCollection(unittest.TestCase):

    def setUp(self):
        self.col = Collection()

        self.col.add(Document({
            "id": 1,
            "name": "Anna",
            "grades": [90, 80, 100]
        }))

        self.col.add(Document({
            "id": 2,
            "name": "Ivan",
            "grades": [60, 70, 75]
        }))

    def test_add(self):
        self.assertEqual(len(self.col.documents), 2)

    def test_duplicate_id(self):
        with self.assertRaises(ValueError):
            self.col.add(Document({"id": 1}))

    def test_delete(self):
        self.col.delete_by_id(1)
        self.assertEqual(len(self.col.documents), 1)

    def test_average_grade(self):
        avg = self.col.average_grade(1)
        self.assertEqual(avg, 90)

    def test_min_grade(self):
        self.assertEqual(self.col.min_grade(1), 80)

    def test_max_grade(self):
        self.assertEqual(self.col.max_grade(1), 100)

    def test_sort_by_average(self):
        sorted_students = self.col.sort_by_average_grade()

        self.assertEqual(
            sorted_students[0]["name"],
            "Ivan"
        )

        self.assertEqual(
            sorted_students[1]["name"],
            "Anna"
        )

    def test_find(self):
        cond = build_condition("name", "==", "Anna")
        result = self.col.find(cond)

        self.assertEqual(len(result), 1)

    def test_update(self):
        self.col.update_by_id(1, "name", "Maria")

        self.assertEqual(
            self.col.documents[1].data["name"],
            "Maria"
        )


if __name__ == "__main__":
    unittest.main()

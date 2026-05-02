import json

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
        results = [doc.data for doc in self.documents.values() if condition(doc.data)]
        if sort_field:
            def key_func(d):
                try:
                    return self._get_field(d, sort_field)
                except ValueError:
                    return None
            results.sort(key=lambda x: (key_func(x) is None, key_func(x)), reverse=reverse)
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

    def save(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([d.data for d in self.documents.values()], f, ensure_ascii=False, indent=2)

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
                raise ValueError("Cannot overwrite non-object field")
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

def parse_value(val):
    try:
        return json.loads(val)
    except Exception:
        return val

def main():
    col = Collection()
    while True:
        try:
            cmd = input(">> ").strip()
            if not cmd:
                continue
            parts = cmd.split(maxsplit=1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""

            if command == "add":
                data = json.loads(args)
                col.add(Document(data))

            elif command == "delete":
                if args.startswith("{"):
                    q = json.loads(args)
                    cond = build_condition(q["field"], q["op"], q.get("value"))
                    col.delete_by_condition(cond)
                else:
                    col.delete_by_id(parse_value(args))

            elif command == "update":
                if args.startswith("{"):
                    q = json.loads(args)
                    cond = build_condition(q["field"], q["op"], q.get("value"))
                    col.update_by_condition(cond, q["update_field"], q["update_value"])
                else:
                    p = args.split(maxsplit=2)
                    if len(p) < 3:
                        raise ValueError("Invalid update command")
                    id_ = parse_value(p[0])
                    field = p[1]
                    value = parse_value(p[2])
                    col.update_by_id(id_, field, value)

            elif command == "find":
                p = args.split()
                if len(p) < 2:
                    raise ValueError("Invalid find command")
                field = p[0]
                op = p[1]
                value = None
                sort_field = None
                reverse = False

                if len(p) >= 3:
                    value = parse_value(p[2])

                if "sort" in p:
                    i = p.index("sort")
                    sort_field = p[i + 1]
                    if len(p) > i + 2 and p[i + 2] == "desc":
                        reverse = True

                cond = build_condition(field, op, value)
                print(col.find(cond, sort_field, reverse))

            elif command == "aggregate":
                p = args.split()
                if len(p) == 1:
                    print(col.aggregate(p[0]))
                else:
                    print(col.aggregate(p[0], p[1]))

            elif command == "groupby":
                print(col.groupby(args.strip()))

            elif command == "save":
                col.save(args.strip())

            elif command == "load":
                col.load(args.strip())

            elif command == "exit":
                break

        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
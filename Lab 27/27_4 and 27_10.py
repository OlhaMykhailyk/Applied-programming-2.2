from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

users = {"admin": "1234", "student": "pass"}
sessions = {}
matrix_data = {}

def page(title, body):
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body{{font-family:Arial;background:#f2f2f2;text-align:center;margin-top:50px}}
.box{{display:inline-block;background:white;padding:30px;border-radius:12px;min-width:520px}}
input{{padding:8px;width:90px;margin:4px}}
.long{{width:340px}}
button{{padding:10px 20px;margin-top:10px}}
a{{text-decoration:none;color:blue}}
table{{margin:auto;border-collapse:collapse}}
td{{border:1px solid black;padding:8px;min-width:50px}}
</style>
</head>
<body>
<div class="box">{body}</div>
</body>
</html>
"""

def matrix_html(mat):
    s = "<table>"
    for row in mat:
        s += "<tr>"
        for x in row:
            s += f"<td>{x}</td>"
        s += "</tr>"
    s += "</table>"
    return s

def multiply(a, b):
    n = len(a)
    k = len(a[0])
    m = len(b[0])
    c = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            for t in range(k):
                c[i][j] += a[i][t] * b[t][j]
    return c

class App(BaseHTTPRequestHandler):
    def current_user(self):
        cookie = self.headers.get("Cookie", "")
        if cookie.startswith("user="):
            u = cookie[5:]
            if u in sessions:
                return u
        return ""

    def html(self, text, cookie=""):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(text.encode("utf-8"))

    def redirect(self, path, cookie=""):
        self.send_response(302)
        self.send_header("Location", path)
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        user = self.current_user()

        if path == "/":
            body = """
<h2>Авторизація</h2>
<form method="post" action="/login">
<input class="long" name="login" placeholder="Логін" required><br>
<input class="long" type="password" name="password" placeholder="Пароль" required><br>
<button>Увійти</button>
</form>
"""
            self.html(page("Вхід", body))

        elif path == "/menu":
            if not user:
                self.redirect("/")
                return
            body = """
<h2>Вибір задачі</h2>
<p><b>27.4</b> Порахувати кількість змін знаку в послідовності</p>
<a href="/task274">Відкрити задачу 27.4</a><br><br>
<p><b>27.10</b> Множення двох матриць</p>
<a href="/task2710">Відкрити задачу 27.10</a><br><br>
<a href="/logout">Вийти</a>
"""
            self.html(page("Меню", body))

        elif path == "/task274":
            if not user:
                self.redirect("/")
                return
            body = """
<h2>Задача 27.4</h2>
<p>Введіть числа через пробіл, останнє число 0</p>
<form method="post" action="/solve274">
<input class="long" name="nums" required><br>
<button>Обробити</button>
</form>
<br><a href="/menu">Назад</a>
"""
            self.html(page("27.4", body))

        elif path == "/task2710":
            if not user:
                self.redirect("/")
                return
            body = """
<h2>Задача 27.10</h2>
<p>Введіть розміри матриць</p>
<form method="post" action="/sizes">
<p>Кількість рядків A</p><input name="n" required><br>
<p>Кількість стовпців A = кількість рядків B</p><input name="k" required><br>
<p>Кількість стовпців B</p><input name="m" required><br>
<button>Далі</button>
</form>
<br><a href="/menu">Назад</a>
"""
            self.html(page("27.10", body))

        elif path == "/matrix_a":
            if not user:
                self.redirect("/")
                return
            d = matrix_data[user]
            n, k = d["n"], d["k"]
            body = '<h2>Введіть матрицю A</h2><form method="post" action="/save_a">'
            for i in range(n):
                for j in range(k):
                    body += f'<input name="a{i}_{j}" required>'
                body += "<br>"
            body += '<button>Далі</button></form>'
            self.html(page("Матриця A", body))

        elif path == "/matrix_b":
            if not user:
                self.redirect("/")
                return
            d = matrix_data[user]
            k, m = d["k"], d["m"]
            body = '<h2>Введіть матрицю B</h2><form method="post" action="/solve2710">'
            for i in range(k):
                for j in range(m):
                    body += f'<input name="b{i}_{j}" required>'
                body += "<br>"
            body += '<button>Обчислити</button></form>'
            self.html(page("Матриця B", body))

        elif path == "/logout":
            if user in sessions:
                del sessions[user]
            if user in matrix_data:
                del matrix_data[user]
            self.redirect("/", "user=; Max-Age=0")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode())
        user = self.current_user()

        if self.path == "/login":
            login = form.get("login", [""])[0]
            password = form.get("password", [""])[0]
            if users.get(login) == password:
                sessions[login] = True
                self.redirect("/menu", f"user={login}")
            else:
                self.redirect("/")

        elif self.path == "/solve274":
            if not user:
                self.redirect("/")
                return
            try:
                arr = list(map(int, form.get("nums", [""])[0].split()))
                if len(arr) < 2 or arr[-1] != 0:
                    txt = "Послідовність має завершуватись нулем"
                elif any(x == 0 for x in arr[:-1]):
                    txt = "Нулі всередині заборонені"
                else:
                    arr = arr[:-1]
                    c = 0
                    for i in range(1, len(arr)):
                        if arr[i] * arr[i - 1] < 0:
                            c += 1
                    txt = f"Кількість змін знаку: {c}"
            except:
                txt = "Некоректне введення"

            body = f"""
<h2>Результат</h2>
<p>{txt}</p>
<a href="/task274">Ще раз</a><br><br>
<a href="/menu">Меню</a>
"""
            self.html(page("Результат", body))

        elif self.path == "/sizes":
            if not user:
                self.redirect("/")
                return
            try:
                n = int(form["n"][0])
                k = int(form["k"][0])
                m = int(form["m"][0])
                if n <= 0 or k <= 0 or m <= 0:
                    self.redirect("/task2710")
                    return
                matrix_data[user] = {"n": n, "k": k, "m": m}
                self.redirect("/matrix_a")
            except:
                self.redirect("/task2710")

        elif self.path == "/save_a":
            d = matrix_data[user]
            n, k = d["n"], d["k"]
            a = []
            try:
                for i in range(n):
                    row = []
                    for j in range(k):
                        row.append(int(form[f"a{i}_{j}"][0]))
                    a.append(row)
                d["a"] = a
                self.redirect("/matrix_b")
            except:
                self.redirect("/matrix_a")

        elif self.path == "/solve2710":
            d = matrix_data[user]
            k, m = d["k"], d["m"]
            b = []
            try:
                for i in range(k):
                    row = []
                    for j in range(m):
                        row.append(int(form[f"b{i}_{j}"][0]))
                    b.append(row)
                a = d["a"]
                c = multiply(a, b)

                body = """
<h2>Результат множення матриць</h2>
<p><b>Матриця A</b></p>
""" + matrix_html(a) + """
<br><p><b>Матриця B</b></p>
""" + matrix_html(b) + """
<br><p><b>Добуток A × B</b></p>
""" + matrix_html(c) + """
<br><br><a href="/task2710">Ще раз</a><br><br>
<a href="/menu">Меню</a>
"""
                self.html(page("Результат", body))
            except:
                self.redirect("/matrix_b")

server = HTTPServer(("localhost", 8000), App)
server.serve_forever()
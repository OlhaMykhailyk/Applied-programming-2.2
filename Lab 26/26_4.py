import re
from urllib.request import Request, urlopen
from collections import Counter
from datetime import datetime

def get_html(date):
    d = datetime.strptime(date, "%d.%m.%Y")
    url = f"https://www.pravda.com.ua/news/date_{d.strftime('%d%m%Y')}/"

    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as f:
        return f.read().decode("utf-8", errors="ignore")

def words(text):
    arr = re.findall(r"\b[А-ЯA-ZЄІЇҐ][а-яa-zєіїґ'-]+\b", text)
    return Counter(arr)

def show(c):
    if not c:
        print("Нічого не знайдено")
        return

    m = max(c.values())

    for k, v in c.items():
        if v == m:
            print(k, "-", v)

date = input("Введіть дату: ")

html = get_html(date)

titles = re.findall(r'href="[^"]*/news/[^"]*".*?>(.*?)</a>', html, re.S)

clean = ""

for t in titles:
    t = re.sub("<.*?>", "", t)
    clean += t + " "

result = words(clean)

show(result)
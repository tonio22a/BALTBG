"""Скачивает эмблемы клубов с baltiho.ru в static/logos/.
Запуск из папки проекта:  python download_logos.py
"""
import os
import urllib.request

KEYS = ["cska", "dynamo", "krylia-sovetov", "spartak", "rubin", "rodina-moscow",
        "lokomotiv", "fakel", "zenit", "akhmat", "rostov", "krasnodar",
        "akron", "dinamo-mx", "orenburg"]

folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "logos")
os.makedirs(folder, exist_ok=True)

for key in KEYS:
    url = f"https://www.baltiho.ru/images/clubs/{key}.png"
    path = os.path.join(folder, f"{key}.png")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r, open(path, "wb") as f:
            f.write(r.read())
        print("OK  ", key)
    except Exception as e:
        print("FAIL", key, e)

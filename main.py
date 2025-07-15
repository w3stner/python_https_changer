import tkinter as tk
from tkinter import ttk
import requests
import re

def get_html(url):
    try:
        response = requests.get(url)
        return response.text
    except Exception as e:
        return ""

def extract_hid(html):
    pattern = r'"hid":"(\d+)","title"'
    match = re.search(pattern, html)
    if match:
        return match.group(1)
    return None

def change_link(original_url, hid, type_):
    new_url = original_url.replace("https", "mtstvapp")
    last_slash_index = new_url.rfind('ru/')
    if type_ == "film":
        new_url = new_url[:last_slash_index + 3] + "video/movie/" + hid
    elif type_ == "serial":
        new_url = new_url[:last_slash_index + 3] + "video/serial/" + hid
    return new_url

def process(type_):
    input_text = url_text.get("1.0", tk.END).strip()
    urls = [line.strip() for line in input_text.splitlines() if line.strip()]
    results = []
    for url in urls:
        html = get_html(url)
        hid = extract_hid(html)
        if hid:
            new_url = change_link(url, hid, type_)
            results.append(f"URL: {url}\n  hid: {hid}\n  Новая ссылка: {new_url}\n")
        else:
            results.append(f"URL: {url}\n  hid не найден\n")
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "\n".join(results))
    result_text.config(state="disabled")

def copy_results():
    result = result_text.get("1.0", tk.END)
    if result.strip():
        root.clipboard_clear()
        root.clipboard_append(result)

# --- GUI ---
root = tk.Tk()
root.title("HID Finder (Множественные ссылки)")

# Ввод ссылок (многострочное поле)
ttk.Label(root, text="Вставьте одну или несколько ссылок (по одной на строку):").pack(pady=5)
url_text = tk.Text(root, width=60, height=8)
url_text.pack(pady=5)

# Кнопки выбора типа
button_frame = ttk.Frame(root)
button_frame.pack(pady=5)
ttk.Button(button_frame, text="Film", command=lambda: process("film")).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame, text="Serial", command=lambda: process("serial")).pack(side=tk.LEFT, padx=5)

# Кнопка копирования всех результатов
ttk.Button(root, text="Копировать все результаты", command=copy_results).pack(pady=5)

# Вывод результатов (многострочное поле, только для чтения)
result_text = tk.Text(root, width=80, height=15, state="disabled")
result_text.pack(pady=10)

root.mainloop()
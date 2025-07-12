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
    new_url = original_url.replace("https", "mtsvapp")
    last_slash_index = new_url.rfind('/')
    if type_ == "film":
        new_url = new_url[:last_slash_index + 3] + "video/movie/" + hid
    elif type_ == "serial":
        new_url = new_url[:last_slash_index + 3] + "video/serial/" + hid
    return new_url

def process(type_):
    url = url_entry.get()
    html = get_html(url)
    hid = extract_hid(html)
    if hid:
        new_url = change_link(url, hid, type_)
        hid_var.set(hid)
        url_var.set(new_url)
        copy_hid_btn["state"] = "normal"
        copy_url_btn["state"] = "normal"
    else:
        hid_var.set("Hid не найден")
        url_var.set("")
        copy_hid_btn["state"] = "disabled"
        copy_url_btn["state"] = "disabled"

def copy_to_clipboard(text):
    if text:
        root.clipboard_clear()
        root.clipboard_append(text)

# --- GUI ---
root = tk.Tk()
root.title("Reworker")

# Ввод ссылки
ttk.Label(root, text="Введите ссылку:").pack(pady=5)
url_entry = ttk.Entry(root, width=50)
url_entry.pack(pady=5)

# Кнопки выбора типа
button_frame = ttk.Frame(root)
button_frame.pack(pady=5)
ttk.Button(button_frame, text="Film", command=lambda: process("film")).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame, text="Serial", command=lambda: process("serial")).pack(side=tk.LEFT, padx=5)

# Результат: hid
hid_frame = ttk.Frame(root)
hid_frame.pack(pady=5, fill="x")
ttk.Label(hid_frame, text="Найденный hid:").pack(side=tk.LEFT)
hid_var = tk.StringVar()
hid_entry = ttk.Entry(hid_frame, textvariable=hid_var, width=30, state="readonly")
hid_entry.pack(side=tk.LEFT, padx=5)
copy_hid_btn = ttk.Button(hid_frame, text="Копировать", command=lambda: copy_to_clipboard(hid_var.get()), state="disabled")
copy_hid_btn.pack(side=tk.LEFT)

# Результат: новая ссылка
url_frame = ttk.Frame(root)
url_frame.pack(pady=5, fill="x")
ttk.Label(url_frame, text="Новая ссылка:").pack(side=tk.LEFT)
url_var = tk.StringVar()
url_entry_result = ttk.Entry(url_frame, textvariable=url_var, width=50, state="readonly")
url_entry_result.pack(side=tk.LEFT, padx=5)
copy_url_btn = ttk.Button(url_frame, text="Копировать", command=lambda: copy_to_clipboard(url_var.get()), state="disabled")
copy_url_btn.pack(side=tk.LEFT)

root.mainloop()
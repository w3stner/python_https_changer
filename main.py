import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re
import threading
from concurrent.futures import ThreadPoolExecutor

# --- сетевые вещи ---
def get_html(url, timeout=8):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
            "Referer": "https://kion.ru/",
            "Connection": "keep-alive",
        }
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
            resp.encoding = resp.apparent_encoding
        return resp.text
    except Exception:
        return ""

HID_RE = re.compile(r'"hid"\s*:\s*"(\d+)"')

def extract_hid(html):
    m = HID_RE.search(html)
    return m.group(1) if m else None

def change_link(original_url, hid, type_):
    new_url = original_url.replace("https", "mtstvapp", 1)
    last_slash_index = new_url.rfind('ru/')
    if last_slash_index == -1:
        return new_url
    if type_ == "film":
        return new_url[:last_slash_index + 3] + "video/movie/" + hid
    elif type_ == "serial":
        return new_url[:last_slash_index + 3] + "video/serial/" + hid
    return new_url

def change_link_hid(original_url, hid, type_):
    last_slash_index = original_url.rfind('ru/')
    if last_slash_index == -1:
        return original_url
    if type_ == "film":
        return original_url[:last_slash_index + 3] + "video/movie/" + hid
    elif type_ == "serial":
        return original_url[:last_slash_index + 3] + "video/serial/" + hid
    return original_url

def format_block_found(url, link_with_hid, new_url):
    return (
        f"URL: {url}\n"
        f" Ссылка + hid: {link_with_hid}\n"
        f" mtsvapp + hid: {new_url}\n"
    )

def format_block_not_found(url):
    return f"URL: {url}\n  hid не найден\n"

# --- GUI ---
root = tk.Tk()
root.title("HID Finder (Множественные ссылки)")

ttk.Label(root, text="Вставьте одну или несколько ссылок (по одной на строку):").pack(pady=5)
url_text = tk.Text(root, width=60, height=8, undo=True, autoseparators=True, maxundo=-1)
url_text.pack(pady=5)
url_text.focus_set()

# Контекстное меню (без доп. биндингов на Ctrl+V — используем штатное поведение Tk)
def make_context_menu(text_widget: tk.Text):
    menu = tk.Menu(text_widget, tearoff=0)
    menu.add_command(label="Вырезать", command=lambda: text_widget.event_generate("<<Cut>>"))
    menu.add_command(label="Копировать", command=lambda: text_widget.event_generate("<<Copy>>"))
    menu.add_command(label="Вставить", command=lambda: text_widget.event_generate("<<Paste>>"))
    def show_menu(e):
        text_widget.focus_set()
        menu.tk_popup(e.x_root, e.y_root)
    text_widget.bind("<Button-3>", show_menu)

make_context_menu(url_text)

button_frame = ttk.Frame(root)
button_frame.pack(pady=5)

status_var = tk.StringVar(value="")
ttk.Label(root, textvariable=status_var).pack(pady=(0,5))

result_text = tk.Text(root, width=80, height=15, state="disabled", wrap="none")
result_text.pack(pady=10)

def set_results(blocks):
    text = "\n".join(blocks)
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, text)
    result_text.config(state="disabled")

def process(type_):
    input_text = url_text.get("1.0", tk.END).strip()
    urls = [line.strip() for line in input_text.splitlines() if line.strip()]
    if not urls:
        return

    status_var.set("Обработка…")

    def worker():
        with ThreadPoolExecutor(max_workers=6) as pool:
            htmls = list(pool.map(get_html, urls))

        blocks = []
        for url, html in zip(urls, htmls):
            hid = extract_hid(html)
            if hid:
                link_with_hid = change_link_hid(url, hid, type_)
                new_url = change_link(url, hid, type_)
                blocks.append(format_block_found(url, link_with_hid, new_url))
            else:
                blocks.append(format_block_not_found(url))

        root.after(0, lambda: (set_results(blocks), status_var.set("Готово")))

    threading.Thread(target=worker, daemon=True).start()

ttk.Button(button_frame, text="Film", command=lambda: process("film")).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame, text="Serial", command=lambda: process("serial")).pack(side=tk.LEFT, padx=5)

def copy_results():
    result = result_text.get("1.0", tk.END)
    if result.strip():
        try:
            root.clipboard_clear()
            root.clipboard_append(result)
        except tk.TclError:
            pass

ttk.Button(root, text="Копировать все результаты", command=copy_results).pack(pady=5)

def report_callback_exception(*args):
    messagebox.showerror("Ошибка", "Произошла ошибка в приложении")
root.report_callback_exception = report_callback_exception

root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Настройки
API_KEY = 'YOUR_API_KEY'  # Замените на свой ключ
API_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD'
HISTORY_FILE = 'history.json'

# Загрузка истории
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Сохранение истории
def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# Получение списка валют
def get_currencies():
    try:
        response = requests.get(API_URL)
        data = response.json()
        if data['result'] == 'success':
            return sorted(data['conversion_rates'].keys())
    except Exception as e:
        messagebox.showerror('Ошибка', f'Не удалось получить список валют: {e}')
    return ['USD', 'EUR', 'RUB', 'GBP']

# Конвертация
def convert():
    from_cur = from_var.get()
    to_cur = to_var.get()
    amount_str = amount_entry.get()

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror('Ошибка', 'Сумма должна быть положительным числом')
        return

    try:
        response = requests.get(f'{API_URL}/{from_cur}')
        data = response.json()
        if data['result'] != 'success':
            raise Exception(data['error-type'])
        rate = data['conversion_rates'][to_cur]
        result = round(amount * rate, 2)

        # Добавление в историю
        history = load_history()
        history.insert(0, {
            'from': from_cur,
            'to': to_cur,
            'amount': amount,
            'result': result,
            'rate': rate,
            'timestamp': data['time_last_update_utc']
        })
        if len(history) > 20:  # Ограничим историю 20 записями
            history = history[:20]
        save_history(history)
        update_history_table()

        result_label.config(text=f'Результат: {result} {to_cur}')
    except Exception as e:
        messagebox.showerror('Ошибка', f'Не удалось выполнить конвертацию: {e}')

# Обновление таблицы истории
def update_history_table():
    for i in history_tree.get_children():
        history_tree.delete(i)
    for entry in load_history():
        history_tree.insert('', 'end', values=(
            entry['timestamp'],
            f"{entry['amount']} {entry['from']} → {entry['result']} {entry['to']}",
            f"1 {entry['from']} = {entry['rate']} {entry['to']}"
        ))

# Создание окна
root = tk.Tk()
root.title('Currency Converter')
root.geometry('600x400')

# Виджеты
tk.Label(root, text='Из:').grid(row=0, column=0, padx=5, pady=5)
tk.Label(root, text='В:').grid(row=1, column=0, padx=5, pady=5)
tk.Label(root, text='Сумма:').grid(row=2, column=0, padx=5, pady=5)

currencies = get_currencies()
from_var = tk.StringVar(value='USD')
to_var = tk.StringVar(value='EUR')
amount_entry = tk.Entry(root)

from_menu = ttk.OptionMenu(root, from_var, *currencies)
to_menu = ttk.OptionMenu(root, to_var, *currencies)

from_menu.grid(row=0, column=1, padx=5, pady=5)
to_menu.grid(row=1, column=1, padx=5, pady=5)
amount_entry.grid(row=2, column=1, padx=5, pady=5)

convert_btn = tk.Button(root, text='Конвертировать', command=convert)
convert_btn.grid(row=3, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text='Результат: ')
result_label.grid(row=4, column=0, columnspan=2, pady=5)

# Таблица истории
history_tree = ttk.Treeview(root, columns=('Дата', 'Операция', 'Курс'), show='headings')
history_tree.heading('Дата', text='Дата')
history_tree.heading('Операция', text='Операция')
history_tree.heading('Курс', text='Курс')
history_tree.column('Дата', width=150)
history_tree.column('Операция', width=250)
history_tree.column('Курс', width=150)
history_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

update_history_table()

root.mainloop()

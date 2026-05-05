import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# --- НАСТРОЙКИ ---
API_KEY = "ВАШ_API_КЛЮЧ"  # Получите на exchangerate-api.com
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"
HISTORY_FILE = "history.json"
CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "RUB"]
# -----------------

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("750x500")
        self.root.resizable(False, False)

        self.history = self.load_history()

        self.create_widgets()
        self.update_history_table()

    # --- ИСТОРИЯ ---
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)
    # ----------------

    # --- API ---
    def get_rate(self, from_cur, to_cur):
        try:
            response = requests.get(BASE_URL + from_cur)
            data = response.json()
            if data.get("result") == "success":
                return data["conversion_rates"].get(to_cur)
            messagebox.showerror("Ошибка API", data.get("error-type", "Неизвестная ошибка"))
        except Exception as e:
            messagebox.showerror("Ошибка сети", str(e))
        return None
    # -------------

    # --- ЛОГИКА ---
    def convert(self):
        try:
            amount = float(self.entry_amount.get())
            if amount <= 0:
                messagebox.showwarning("Ошибка", "Сумма должна быть положительной")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректное число")
            return

        from_cur = self.combo_from.get()
        to_cur = self.combo_to.get()

        if from_cur == to_cur:
            result = amount
        else:
            rate = self.get_rate(from_cur, to_cur)
            if rate is None:
                return
            result = round(amount * rate, 2)

        self.label_result.config(text=f"{amount:.2f} {from_cur} = {result:.2f} {to_cur}")

        # Сохраняем в историю
        self.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": from_cur,
            "to": to_cur,
            "amount": amount,
            "result": result
        })
        self.save_history()
        self.update_history_table()

    def clear_history(self):
        self.history = []
        self.save_history()
        self.update_history_table()
    # --------------

    # --- ИНТЕРФЕЙС ---
    def create_widgets(self):
        # Рамка ввода
        frame_input = tk.LabelFrame(self.root, text="Конвертация", padx=10, pady=10)
        frame_input.pack(pady=10, padx=10, fill="x")

        tk.Label(frame_input, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.entry_amount = tk.Entry(frame_input)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="Из:").grid(row=1, column=0, sticky="w")
        self.combo_from = ttk.Combobox(frame_input, values=CURRENCIES, state="readonly")
        self.combo_from.set("USD")
        self.combo_from.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="В:").grid(row=2, column=0, sticky="w")
        self.combo_to = ttk.Combobox(frame_input, values=CURRENCIES, state="readonly")
        self.combo_to.set("EUR")
        self.combo_to.grid(row=2, column=1, padx=5, pady=5)

        self.btn_convert = tk.Button(frame_input, text="Конвертировать", command=self.convert, bg="lightblue")
        self.btn_convert.grid(row=3, column=0, columnspan=2, pady=10)

        self.label_result = tk.Label(frame_input, text="", font=("Arial", 12))
        self.label_result.grid(row=4, column=0, columnspan=2)

        # Рамка истории
        frame_history = tk.LabelFrame(self.root, text="История", padx=10, pady=10)
        frame_history.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("Время", "Операция", "Результат")
        self.tree = ttk.Treeview(frame_history, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=250)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_history, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Кнопки управления историей
        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=5)

        btn_clear = tk.Button(frame_buttons, text="Очистить историю", command=self.clear_history, bg="lightcoral")
        btn_clear.pack(side="left", padx=5)

    def update_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for record in self.history:
            self.tree.insert("", "end", values=(
                record["timestamp"],
                f"{record['amount']} {record['from']} → {record['to']}",
                f"{record['result']} {record['to']}"
            ))
# ---------------------


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()

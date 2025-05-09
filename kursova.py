import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

# Склад: товар -> [ціна, кількість на складі]
products = {
    "Хліб": [20, 10],
    "Молоко": [30, 15],
    "Сир": [80, 5],
    "Яблука (кг)": [25, 20],
    "Шоколад": [50, 12],
    "Сік апельсиновий": [40, 8],
    "Кава (пакет)": [90, 6],
    "Чай (упаковка)": [70, 10],
    "Яйця (десяток)": [35, 14],
    "Мінеральна вода": [18, 25]
}

cart = []


def get_in_cart_quantity(product_name):
    return sum(q for name, q, _ in cart if name == product_name)


def update_product_menu(event=None):
    input_text = search_var.get().lower()
    filtered = [p for p in products if input_text in p.lower()]
    product_menu['values'] = filtered
    if filtered:
        product_menu.current(0)
        show_stock_and_price()
    else:
        product_var.set("")
        stock_label.config(text="Залишок:")
        price_label.config(text="Ціна:")


def show_stock_and_price(event=None):
    product = product_var.get()
    if product in products:
        _, stock = products[product]
        in_cart = get_in_cart_quantity(product)
        available = stock - in_cart
        stock_label.config(text=f"Залишок: {available}")
        price_label.config(text=f"Ціна: {products[product][0]} грн")
    else:
        stock_label.config(text="Залишок:")
        price_label.config(text="Ціна:")


def update_products_table():
    # Очистити таблицю
    for item in products_tree.get_children():
        products_tree.delete(item)
    # Додати актуальні товари
    for name, (price, stock) in products.items():
        in_cart = get_in_cart_quantity(name)
        available = stock - in_cart
        products_tree.insert("", tk.END, values=(name, price, available))


def add_to_cart():
    product = product_var.get()
    if product not in products:
        messagebox.showerror("Помилка", "Оберіть існуючий товар")
        return
    try:
        quantity = int(quantity_var.get())
        if quantity <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Помилка", "Введіть коректну кількість (ціле число > 0)")
        return

    price, stock = products[product]
    already_in_cart = get_in_cart_quantity(product)
    available = stock - already_in_cart

    if quantity > available:
        messagebox.showerror("Недостатньо на складі", f"Доступно лише {available} одиниць.")
        return

    cart.append((product, quantity, price))
    update_cart_display()
    show_stock_and_price()
    update_products_table()


def update_cart_display():
    cart_listbox.delete(0, tk.END)
    for item in cart:
        name, qty, price = item
        cart_listbox.insert(tk.END, f"{name} x {qty} = {qty * price} грн")


def clear_cart():
    cart.clear()
    update_cart_display()
    show_stock_and_price()
    update_products_table()


def delete_selected_item():
    selected = cart_listbox.curselection()
    if not selected:
        return
    index = selected[0]
    del cart[index]
    update_cart_display()
    show_stock_and_price()
    update_products_table()


def show_receipt():
    if not cart:
        messagebox.showinfo("Порожній кошик", "Спочатку додайте товари до кошика.")
        return

    receipt_window = tk.Toplevel(root)
    receipt_window.title("Чек")

    tk.Label(receipt_window, text="Ваш чек:", font=("Arial", 14, "bold")).pack(pady=10)

    total_price = 0
    lines = []

    for item in cart:
        name, qty, price = item
        products[name][1] -= qty
        line = f"{name} - {qty} x {price} = {qty * price} грн"
        total_price += qty * price
        lines.append(line)
        tk.Label(receipt_window, text=line, font=("Arial", 12)).pack(anchor="w", padx=20)

    total_line = f"Загальна сума: {total_price} грн"
    tk.Label(receipt_window, text=total_line, font=("Arial", 13, "bold")).pack(pady=10)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("receipt.txt", "a", encoding="utf-8") as f:
        f.write("=== Новий чек ===\n")
        f.write(f"Дата і час: {now}\n")
        for l in lines:
            f.write(l + "\n")
        f.write(total_line + "\n\n")

    clear_cart()
    update_product_menu()
    update_products_table()


# Інтерфейс
root = tk.Tk()
root.title("Магазин")
root.geometry("1000x600")  # збільшив, щоб влізла таблиця справа

# Головний фрейм для поділу на ліву і праву частину
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Ліва частина (все управління)
left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

tk.Label(left_frame, text="Пошук товару:", font=("Arial", 12)).pack(pady=5)
search_var = tk.StringVar()
search_entry = tk.Entry(left_frame, textvariable=search_var)
search_entry.pack()
search_entry.bind("<KeyRelease>", update_product_menu)

tk.Label(left_frame, text="Оберіть товар:", font=("Arial", 12)).pack(pady=5)
product_var = tk.StringVar()
product_menu = ttk.Combobox(left_frame, textvariable=product_var, values=list(products.keys()), state="readonly")
product_menu.pack()
product_menu.bind("<<ComboboxSelected>>", show_stock_and_price)

stock_label = tk.Label(left_frame, text="Залишок:", font=("Arial", 10))
stock_label.pack()

price_label = tk.Label(left_frame, text="Ціна:", font=("Arial", 10))
price_label.pack()

tk.Label(left_frame, text="Кількість:", font=("Arial", 12)).pack(pady=5)
quantity_var = tk.StringVar()
quantity_entry = tk.Entry(left_frame, textvariable=quantity_var)
quantity_entry.pack()

tk.Button(left_frame, text="Додати до кошика", command=add_to_cart, width=20, bg="lightgreen").pack(pady=10)

tk.Label(left_frame, text="Кошик:", font=("Arial", 12, "bold")).pack(pady=5)
cart_listbox = tk.Listbox(left_frame, width=50, height=10)
cart_listbox.pack()

buttons_frame = tk.Frame(left_frame)
buttons_frame.pack(pady=10)

tk.Button(buttons_frame, text="Очистити кошик", command=clear_cart, bg="tomato", width=20).grid(row=0, column=0, padx=5)
tk.Button(buttons_frame, text="Видалити обране", command=delete_selected_item, bg="orange", width=20).grid(row=0, column=1, padx=5)
tk.Button(left_frame, text="Оформити покупку", command=show_receipt, bg="lightblue", width=43).pack(pady=10)

# Права частина (газета товарів)
right_frame = tk.Frame(main_frame)
right_frame.pack(side="right", fill="y", padx=10, pady=10)

tk.Label(right_frame, text="Наявні товари:", font=("Arial", 12, "bold")).pack(pady=5)
products_tree = ttk.Treeview(right_frame, columns=("Товар", "Ціна", "Залишок"), show="headings", height=25)
products_tree.heading("Товар", text="Товар")
products_tree.heading("Ціна", text="Ціна (грн)")
products_tree.heading("Залишок", text="Залишок (шт)")

products_tree.column("Товар", width=200, anchor="center")
products_tree.column("Ціна", width=100, anchor="center")
products_tree.column("Залишок", width=100, anchor="center")

products_tree.pack(side=tk.LEFT, fill="y")

scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=products_tree.yview)
products_tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Оновлюємо таблицю при запуску
update_products_table()
update_product_menu()
root.mainloop()

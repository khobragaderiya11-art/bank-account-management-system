"""
Trustline Bank - Account Management System
Mini Project: Python + Tkinter + MySQL

Setup:
    pip install mysql-connector-python
    Edit DB_CONFIG below with your MySQL user/password.
    Run:  python bank_management.py
Default login:  admin / admin123
"""

import re
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ---------------- DATABASE ----------------
DB_CONFIG = {"host": "localhost", "user": "root", "password": "#ritU2006"}
DB_NAME = "bank_db"
BANK_NAME = "TRUSTLINE BANK"
BANK_TAGLINE = "Secure  •  Simple  •  Reliable"

# ---------------- THEME ----------------
NAVY = "#0a2540"
NAVY_LIGHT = "#123a63"
GOLD = "#c9a961"
BG = "#eef1f6"
CARD = "#ffffff"
TEXT_DARK = "#1c2b3a"
MUTED = "#5b6b7d"
GREEN = "#1e7a4c"
RED = "#b3352c"
ROW_ALT = "#f4f7fb"


def get_conn():
    return mysql.connector.connect(database=DB_NAME, **DB_CONFIG)


def setup_database():
    """Create database, tables and default admin user (runs once)."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cur.execute(f"USE {DB_NAME}")
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
                    username VARCHAR(50) PRIMARY KEY,
                    password VARCHAR(64) NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS accounts (
                    acc_no INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    gender VARCHAR(10),
                    phone VARCHAR(10) NOT NULL,
                    email VARCHAR(100),
                    acc_type VARCHAR(20),
                    balance DECIMAL(12,2) DEFAULT 0)""")
    cur.execute("ALTER TABLE accounts AUTO_INCREMENT = 1001")
    cur.execute("""CREATE TABLE IF NOT EXISTS transactions (
                    txn_id INT AUTO_INCREMENT PRIMARY KEY,
                    acc_no INT NOT NULL,
                    txn_type VARCHAR(10) NOT NULL,
                    amount DECIMAL(12,2) NOT NULL,
                    txn_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no) ON DELETE CASCADE)""")
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users VALUES (%s, %s)",
                    ("admin", hashlib.sha256(b"admin123").hexdigest()))
    conn.commit()
    conn.close()


def run_query(sql, params=(), fetch=False):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    data = cur.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data


def fmt_money(value):
    return f"Rs. {float(value):,.2f}"


def fmt_acc(acc_no):
    return f"AC-{int(acc_no):06d}"


# ---------------- APP ----------------
class BankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{BANK_NAME} - Account Management System")
        self.geometry("1000x650")
        self.minsize(950, 600)
        self.configure(bg=BG)
        self.current_frame = None
        self._build_style()
        self.show_login()

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)

        style.configure("TLabel", background=BG, foreground=TEXT_DARK, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=CARD, foreground=TEXT_DARK, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Heading.TLabel", background=CARD, foreground=NAVY, font=("Segoe UI", 12, "bold"))

        style.configure("TEntry", padding=6, fieldbackground="#ffffff")
        style.configure("TCombobox", padding=5)
        style.configure("TRadiobutton", background=CARD, font=("Segoe UI", 10))

        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 7), background="#dbe4f0",
                         foreground=NAVY)
        style.map("TButton", background=[("active", "#c6d3e6")])

        style.configure("Primary.TButton", background=NAVY, foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Primary.TButton", background=[("active", NAVY_LIGHT)])

        style.configure("Gold.TButton", background=GOLD, foreground=NAVY, font=("Segoe UI", 10, "bold"))
        style.map("Gold.TButton", background=[("active", "#b6913f")])

        style.configure("Success.TButton", background=GREEN, foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Success.TButton", background=[("active", "#155c39")])

        style.configure("Danger.TButton", background=RED, foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Danger.TButton", background=[("active", "#8f2a23")])

        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10), background="white",
                         fieldbackground="white", foreground=TEXT_DARK, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=NAVY,
                         foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[("active", NAVY_LIGHT)])
        style.map("Treeview", background=[("selected", GOLD)], foreground=[("selected", NAVY)])

    def switch(self, frame_cls):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_cls(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self.switch(LoginPage)

    def show_dashboard(self):
        self.switch(Dashboard)


# ---------------- LOGIN ----------------
class LoginPage(ttk.Frame):
    def __init__(self, app):
        super().__init__(app, style="TFrame")
        self.app = app

        # Left navy banner
        banner = tk.Frame(self, bg=NAVY, width=380)
        banner.pack(side="left", fill="y")
        banner.pack_propagate(False)
        tk.Label(banner, text="\U0001F3E6", font=("Segoe UI Emoji", 46), bg=NAVY, fg=GOLD).pack(pady=(120, 10))
        tk.Label(banner, text=BANK_NAME, font=("Georgia", 22, "bold"), bg=NAVY, fg="white").pack()
        tk.Label(banner, text=BANK_TAGLINE, font=("Segoe UI", 10), bg=NAVY, fg="#b9c6d6").pack(pady=(6, 0))
        tk.Frame(banner, bg=GOLD, height=2, width=60).pack(pady=20)
        tk.Label(banner, text="Account Management System", font=("Segoe UI", 9),
                 bg=NAVY, fg="#8296ac").pack(side="bottom", pady=20)

        # Right login card
        right = ttk.Frame(self, style="TFrame")
        right.pack(side="left", fill="both", expand=True)

        box = tk.Frame(right, bg=CARD, padx=45, pady=40, highlightbackground="#d7deea",
                       highlightthickness=1)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="Welcome Back", font=("Segoe UI", 18, "bold"), bg=CARD, fg=NAVY).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
        tk.Label(box, text="Sign in to manage customer accounts", font=("Segoe UI", 9),
                 bg=CARD, fg=MUTED).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 22))

        tk.Label(box, text="USERNAME", font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).grid(
            row=2, column=0, sticky="w")
        self.user = ttk.Entry(box, width=28, font=("Segoe UI", 11))
        self.user.grid(row=3, column=0, columnspan=2, pady=(2, 14), ipady=3)

        tk.Label(box, text="PASSWORD", font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).grid(
            row=4, column=0, sticky="w")
        self.pwd = ttk.Entry(box, width=28, show="\u25CF", font=("Segoe UI", 11))
        self.pwd.grid(row=5, column=0, columnspan=2, pady=(2, 22), ipady=3)
        self.pwd.bind("<Return>", lambda e: self.login())

        ttk.Button(box, text="LOGIN", style="Primary.TButton", command=self.login).grid(
            row=6, column=0, columnspan=2, sticky="ew", ipady=4)

        tk.Label(box, text="Default demo login: admin / admin123", font=("Segoe UI", 8),
                 bg=CARD, fg=MUTED).grid(row=7, column=0, columnspan=2, pady=(16, 0))

        self.user.focus()

    def login(self):
        u, p = self.user.get().strip(), self.pwd.get()
        if not u or not p:
            messagebox.showwarning("Login", "Enter username and password")
            return
        hashed = hashlib.sha256(p.encode()).hexdigest()
        rows = run_query("SELECT * FROM users WHERE username=%s AND password=%s",
                         (u, hashed), fetch=True)
        if rows:
            self.app.show_dashboard()
        else:
            messagebox.showerror("Login", "Invalid username or password")
            self.pwd.delete(0, tk.END)


# ---------------- DASHBOARD ----------------
class Dashboard(ttk.Frame):
    def __init__(self, app):
        super().__init__(app, style="TFrame")
        self.app = app
        self.selected_acc = None

        # ---- Header ----
        header = tk.Frame(self, bg=NAVY, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        left = tk.Frame(header, bg=NAVY)
        left.pack(side="left", padx=18)
        tk.Label(left, text="\U0001F3E6", font=("Segoe UI Emoji", 20), bg=NAVY, fg=GOLD).pack(side="left")
        title_box = tk.Frame(left, bg=NAVY)
        title_box.pack(side="left", padx=10)
        tk.Label(title_box, text=BANK_NAME, font=("Georgia", 14, "bold"), bg=NAVY, fg="white").pack(anchor="w")
        tk.Label(title_box, text="Account Management System", font=("Segoe UI", 8), bg=NAVY,
                 fg="#9fb0c4").pack(anchor="w")

        right = tk.Frame(header, bg=NAVY)
        right.pack(side="right", padx=18)
        tk.Label(right, text=datetime.now().strftime("%d %b %Y"), font=("Segoe UI", 9),
                 bg=NAVY, fg="#9fb0c4").pack(side="left", padx=(0, 16))
        ttk.Button(right, text="Logout", style="Gold.TButton", command=self.logout).pack(side="left")

        # ---- Summary strip ----
        self.summary = tk.Frame(self, bg=BG)
        self.summary.pack(fill="x", padx=18, pady=(14, 0))
        self.card_total_accounts = self._summary_card(self.summary, "Total Accounts", "0")
        self.card_total_balance = self._summary_card(self.summary, "Total Deposits", "Rs. 0.00")
        self.card_selected = self._summary_card(self.summary, "Selected Account", "None")

        # ---- Nav ----
        nav = tk.Frame(self, bg=BG)
        nav.pack(fill="x", padx=18, pady=12)
        for text, cmd in [("\u2795 Add / Update", self.focus_form), ("\U0001F4CB View All", self.load_data),
                          ("\u2B07 Deposit", lambda: self.transaction("deposit")),
                          ("\u2B06 Withdraw", lambda: self.transaction("withdraw")),
                          ("\U0001F4C4 Statement", self.show_statement)]:
            ttk.Button(nav, text=text, command=cmd).pack(side="left", padx=(0, 8))

        # ---- Form card ----
        form_card = tk.Frame(self, bg=CARD, highlightbackground="#d7deea", highlightthickness=1)
        form_card.pack(fill="x", padx=18, pady=(0, 12))
        form = tk.Frame(form_card, bg=CARD, padx=18, pady=14)
        form.pack(fill="x")

        ttk.Label(form, text="Customer & Account Details", style="Heading.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        self.name = tk.StringVar()
        self.phone = tk.StringVar()
        self.email = tk.StringVar()
        self.balance = tk.StringVar()
        self.gender = tk.StringVar(value="Male")
        self.acc_type = tk.StringVar()

        ttk.Label(form, text="Full Name", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(form, textvariable=self.name, width=26)
        self.name_entry.grid(row=1, column=1, padx=8)
        ttk.Label(form, text="Phone Number", style="Card.TLabel").grid(row=1, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.phone, width=26).grid(row=1, column=3, padx=8)

        ttk.Label(form, text="Email Address", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.email, width=26).grid(row=2, column=1, padx=8)
        ttk.Label(form, text="Opening Balance (Rs.)", style="Card.TLabel").grid(row=2, column=2, sticky="w")
        self.balance_entry = ttk.Entry(form, textvariable=self.balance, width=26)
        self.balance_entry.grid(row=2, column=3, padx=8)

        ttk.Label(form, text="Gender", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        rb = tk.Frame(form, bg=CARD)
        rb.grid(row=3, column=1, sticky="w", padx=8)
        for g in ("Male", "Female", "Other"):
            ttk.Radiobutton(rb, text=g, variable=self.gender, value=g).pack(side="left", padx=(0, 8))
        ttk.Label(form, text="Account Type", style="Card.TLabel").grid(row=3, column=2, sticky="w")
        ttk.Combobox(form, textvariable=self.acc_type, width=23, state="readonly",
                     values=["Savings", "Current", "Fixed Deposit"]).grid(row=3, column=3, padx=8)
        self.acc_type.set("Savings")

        actions = tk.Frame(form_card, bg=CARD, padx=18, pady=4)
        actions.pack(fill="x")
        ttk.Button(actions, text="Add", style="Success.TButton", command=self.add).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Update", style="Primary.TButton", command=self.update).pack(side="left", padx=6)
        ttk.Button(actions, text="Delete", style="Danger.TButton", command=self.delete).pack(side="left", padx=6)
        ttk.Button(actions, text="Clear", command=self.clear).pack(side="left", padx=6)

        ttk.Label(actions, text="Search:", style="Card.TLabel").pack(side="left", padx=(24, 6))
        self.search_var = tk.StringVar()
        ttk.Entry(actions, textvariable=self.search_var, width=22).pack(side="left")
        ttk.Button(actions, text="Search", command=self.search).pack(side="left", padx=6)

        # ---- Records table ----
        table_card = tk.Frame(self, bg=CARD, highlightbackground="#d7deea", highlightthickness=1)
        table_card.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        ttk.Label(table_card, text="Customer Accounts", style="Heading.TLabel").pack(
            anchor="w", padx=16, pady=(12, 6))

        cols = ("acc_no", "name", "gender", "phone", "email", "acc_type", "balance")
        headers = ("Account No.", "Name", "Gender", "Phone", "Email", "Type", "Balance")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings", height=10)
        for c, h, w in zip(cols, headers, (110, 160, 70, 110, 190, 100, 130)):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center")
        self.tree.tag_configure("odd", background=ROW_ALT)
        self.tree.tag_configure("even", background="white")
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_data()

    # ---------- UI helpers ----------
    def _summary_card(self, parent, label, value):
        card = tk.Frame(parent, bg=CARD, highlightbackground="#d7deea", highlightthickness=1)
        card.pack(side="left", fill="x", expand=True, padx=(0, 12), ipady=8)
        tk.Label(card, text=label.upper(), font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(
            anchor="w", padx=14, pady=(8, 0))
        val_lbl = tk.Label(card, text=value, font=("Segoe UI", 15, "bold"), bg=CARD, fg=NAVY)
        val_lbl.pack(anchor="w", padx=14, pady=(0, 8))
        return val_lbl

    def refresh_summary(self):
        rows = run_query("SELECT COUNT(*), COALESCE(SUM(balance),0) FROM accounts", fetch=True)
        count, total = rows[0]
        self.card_total_accounts.config(text=str(count))
        self.card_total_balance.config(text=fmt_money(total))
        self.card_selected.config(text=fmt_acc(self.selected_acc) if self.selected_acc else "None")

    def focus_form(self):
        self.name_entry.focus()

    def logout(self):
        if messagebox.askyesno("Logout", "Do you want to logout?"):
            self.app.show_login()

    def validate(self, check_balance=True):
        name = self.name.get().strip()
        phone = self.phone.get().strip()
        email = self.email.get().strip()
        if not name or not re.fullmatch(r"[A-Za-z ]+", name):
            messagebox.showerror("Validation", "Enter a valid name (letters only)")
            return False
        if not re.fullmatch(r"[6-9]\d{9}", phone):
            messagebox.showerror("Validation", "Phone must be 10 digits (starting 6-9)")
            return False
        if email and not re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.]+", email):
            messagebox.showerror("Validation", "Enter a valid email address")
            return False
        if check_balance:
            try:
                if float(self.balance.get()) < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation", "Balance must be a non-negative number")
                return False
        return True

    def load_data(self, rows=None):
        if rows is None:
            rows = run_query("SELECT * FROM accounts ORDER BY acc_no", fetch=True)
        self.tree.delete(*self.tree.get_children())
        for i, r in enumerate(rows):
            acc_no, name, gender, phone, email, acc_type, balance = r
            display = (fmt_acc(acc_no), name, gender, phone, email or "-", acc_type, fmt_money(balance))
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", tk.END, iid=str(acc_no), values=display, tags=(tag,))
        self.refresh_summary()

    def on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        acc_no = int(sel[0])
        row = run_query("SELECT * FROM accounts WHERE acc_no=%s", (acc_no,), fetch=True)
        if not row:
            return
        acc_no, name, gender, phone, email, acc_type, balance = row[0]
        self.selected_acc = acc_no
        self.name.set(name)
        self.gender.set(gender)
        self.phone.set(str(phone))
        self.email.set(email or "")
        self.acc_type.set(acc_type)
        self.balance.set(str(balance))
        self.refresh_summary()

    # ---------- CRUD ----------
    def add(self):
        if not self.validate():
            return
        run_query("INSERT INTO accounts (name, gender, phone, email, acc_type, balance) "
                  "VALUES (%s,%s,%s,%s,%s,%s)",
                  (self.name.get().strip(), self.gender.get(), self.phone.get().strip(),
                   self.email.get().strip(), self.acc_type.get(), float(self.balance.get())))
        messagebox.showinfo("Success", "Account opened successfully")
        self.clear()
        self.load_data()

    def update(self):
        if not self.selected_acc:
            messagebox.showwarning("Update", "Select a record from the table first")
            return
        if not self.validate():
            return
        run_query("UPDATE accounts SET name=%s, gender=%s, phone=%s, email=%s, acc_type=%s, "
                  "balance=%s WHERE acc_no=%s",
                  (self.name.get().strip(), self.gender.get(), self.phone.get().strip(),
                   self.email.get().strip(), self.acc_type.get(), float(self.balance.get()),
                   self.selected_acc))
        messagebox.showinfo("Success", "Account updated successfully")
        self.clear()
        self.load_data()

    def delete(self):
        if not self.selected_acc:
            messagebox.showwarning("Delete", "Select a record from the table first")
            return
        if messagebox.askyesno("Confirm", f"Close account {fmt_acc(self.selected_acc)}?"):
            run_query("DELETE FROM accounts WHERE acc_no=%s", (self.selected_acc,))
            messagebox.showinfo("Deleted", "Account closed")
            self.clear()
            self.load_data()

    def search(self):
        key = self.search_var.get().strip()
        if not key:
            self.load_data()
            return
        like = f"%{key}%"
        rows = run_query("SELECT * FROM accounts WHERE CAST(acc_no AS CHAR) LIKE %s "
                         "OR name LIKE %s OR phone LIKE %s", (like, like, like), fetch=True)
        self.load_data(rows)
        if not rows:
            messagebox.showinfo("Search", "No matching records found")

    def clear(self):
        self.selected_acc = None
        self.name.set("")
        self.phone.set("")
        self.email.set("")
        self.balance.set("")
        self.gender.set("Male")
        self.acc_type.set("Savings")
        self.search_var.set("")
        self.tree.selection_remove(self.tree.selection())
        self.refresh_summary()

    # ---------- Extra feature: Deposit / Withdraw ----------
    def transaction(self, kind):
        if not self.selected_acc:
            messagebox.showwarning("Transaction", "Select an account from the table first")
            return
        win = tk.Toplevel(self)
        win.title(kind.title())
        win.geometry("320x180")
        win.configure(bg=CARD)
        win.grab_set()

        tk.Label(win, text=f"{kind.title()} - {fmt_acc(self.selected_acc)}",
                 font=("Segoe UI", 11, "bold"), bg=CARD, fg=NAVY).pack(pady=(16, 4))
        tk.Label(win, text="Enter amount (Rs.)", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack()
        amt = ttk.Entry(win, width=20, font=("Segoe UI", 11))
        amt.pack(pady=8, ipady=3)
        amt.focus()

        def submit():
            try:
                a = float(amt.get())
                if a <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid positive amount", parent=win)
                return
            bal = float(run_query("SELECT balance FROM accounts WHERE acc_no=%s",
                                  (self.selected_acc,), fetch=True)[0][0])
            if kind == "withdraw" and a > bal:
                messagebox.showerror("Error", "Insufficient balance", parent=win)
                return
            new_bal = bal + a if kind == "deposit" else bal - a
            run_query("UPDATE accounts SET balance=%s WHERE acc_no=%s",
                      (new_bal, self.selected_acc))
            run_query("INSERT INTO transactions (acc_no, txn_type, amount) VALUES (%s,%s,%s)",
                      (self.selected_acc, kind, a))
            messagebox.showinfo("Success", f"New balance: {fmt_money(new_bal)}", parent=win)
            win.destroy()
            self.clear()
            self.load_data()

        style_name = "Success.TButton" if kind == "deposit" else "Danger.TButton"
        ttk.Button(win, text=kind.upper(), style=style_name, command=submit).pack(pady=6, ipadx=10)

    # ---------- Extra feature: Mini Statement ----------
    def show_statement(self):
        if not self.selected_acc:
            messagebox.showwarning("Statement", "Select an account from the table first")
            return
        rows = run_query("SELECT txn_type, amount, txn_time FROM transactions "
                         "WHERE acc_no=%s ORDER BY txn_time DESC", (self.selected_acc,), fetch=True)

        win = tk.Toplevel(self)
        win.title(f"Statement - {fmt_acc(self.selected_acc)}")
        win.geometry("460x400")
        win.configure(bg=CARD)
        win.grab_set()

        tk.Label(win, text=BANK_NAME, font=("Georgia", 12, "bold"), bg=CARD, fg=NAVY).pack(pady=(14, 0))
        tk.Label(win, text=f"Mini Statement - {fmt_acc(self.selected_acc)}",
                 font=("Segoe UI", 10), bg=CARD, fg=MUTED).pack(pady=(2, 10))

        cols = ("type", "amount", "date_time")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
        for c, h, w in zip(cols, ("Type", "Amount", "Date & Time"), (90, 120, 200)):
            tree.heading(c, text=h)
            tree.column(c, width=w, anchor="center")
        tree.tag_configure("odd", background=ROW_ALT)
        tree.tag_configure("even", background="white")
        tree.pack(fill="both", expand=True, padx=14, pady=5)

        if not rows:
            tk.Label(win, text="No transactions yet for this account.", bg=CARD, fg=MUTED).pack(pady=10)
        for i, (txn_type, amount, txn_time) in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            sign = "+" if txn_type == "deposit" else "-"
            tree.insert("", tk.END, values=(txn_type.title(), f"{sign} {fmt_money(amount)}", txn_time),
                       tags=(tag,))

        ttk.Button(win, text="Close", style="Primary.TButton", command=win.destroy).pack(pady=10)


if __name__ == "__main__":
    try:
        setup_database()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Could not connect to MySQL:\n{err}")
        raise SystemExit
    BankApp().mainloop()
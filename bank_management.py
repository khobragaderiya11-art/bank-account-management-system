"""
Bank Account Management System
Mini Project: Python + Tkinter + MySQL

Setup:
    pip install mysql-connector-python
    Edit DB_CONFIG below with your MySQL user/password.
    Run:  python bank_management.py
Default login:  admin / admin123
"""

import re
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ---------------- DATABASE ----------------
DB_CONFIG = {"host": "localhost", "user": "root", "password": "#ritU2006"}
DB_NAME = "bank_db"


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


# ---------------- APP ----------------
class BankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bank Account Management System")
        self.geometry("900x600")
        self.configure(bg="#eef2f7")
        self.current_frame = None
        self.show_login()

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
class LoginPage(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="#eef2f7")
        self.app = app
        box = tk.Frame(self, bg="white", padx=40, pady=30, bd=2, relief="groove")
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="Bank Account Management", font=("Arial", 18, "bold"),
                 bg="white", fg="#1f3a5f").grid(row=0, column=0, columnspan=2, pady=(0, 20))
        tk.Label(box, text="Username", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        tk.Label(box, text="Password", bg="white").grid(row=2, column=0, sticky="w", pady=5)

        self.user = ttk.Entry(box, width=25)
        self.pwd = ttk.Entry(box, width=25, show="*")
        self.user.grid(row=1, column=1, pady=5)
        self.pwd.grid(row=2, column=1, pady=5)
        self.pwd.bind("<Return>", lambda e: self.login())

        ttk.Button(box, text="Login", command=self.login).grid(row=3, column=0, columnspan=2, pady=15)
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
class Dashboard(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="#eef2f7")
        self.app = app
        self.selected_acc = None

        # Header
        header = tk.Frame(self, bg="#1f3a5f", height=50)
        header.pack(fill="x")
        tk.Label(header, text="Bank Account Management System", font=("Arial", 16, "bold"),
                 bg="#1f3a5f", fg="white").pack(side="left", padx=15, pady=10)
        ttk.Button(header, text="Logout", command=self.logout).pack(side="right", padx=15)

        # Navigation menu
        nav = tk.Frame(self, bg="#dbe4f0")
        nav.pack(fill="x")
        for text, cmd in [("Add / Update", self.focus_form), ("View All", self.load_data),
                          ("Deposit", lambda: self.transaction("deposit")),
                          ("Withdraw", lambda: self.transaction("withdraw"))]:
            ttk.Button(nav, text=text, command=cmd).pack(side="left", padx=5, pady=5)

        # Form
        form = tk.LabelFrame(self, text="Account Details", bg="#eef2f7", padx=10, pady=8)
        form.pack(fill="x", padx=15, pady=10)

        self.name = tk.StringVar()
        self.phone = tk.StringVar()
        self.email = tk.StringVar()
        self.balance = tk.StringVar()
        self.gender = tk.StringVar(value="Male")
        self.acc_type = tk.StringVar()

        tk.Label(form, text="Name", bg="#eef2f7").grid(row=0, column=0, sticky="w", pady=4)
        self.name_entry = ttk.Entry(form, textvariable=self.name, width=25)
        self.name_entry.grid(row=0, column=1, padx=8)
        tk.Label(form, text="Phone", bg="#eef2f7").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.phone, width=25).grid(row=0, column=3, padx=8)

        tk.Label(form, text="Email", bg="#eef2f7").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.email, width=25).grid(row=1, column=1, padx=8)
        tk.Label(form, text="Opening Balance", bg="#eef2f7").grid(row=1, column=2, sticky="w")
        self.balance_entry = ttk.Entry(form, textvariable=self.balance, width=25)
        self.balance_entry.grid(row=1, column=3, padx=8)

        tk.Label(form, text="Gender", bg="#eef2f7").grid(row=2, column=0, sticky="w", pady=4)
        rb = tk.Frame(form, bg="#eef2f7")
        rb.grid(row=2, column=1, sticky="w", padx=8)
        for g in ("Male", "Female", "Other"):
            ttk.Radiobutton(rb, text=g, variable=self.gender, value=g).pack(side="left")
        tk.Label(form, text="Account Type", bg="#eef2f7").grid(row=2, column=2, sticky="w")
        ttk.Combobox(form, textvariable=self.acc_type, width=22, state="readonly",
                     values=["Savings", "Current", "Fixed Deposit"]).grid(row=2, column=3, padx=8)
        self.acc_type.set("Savings")

        # Buttons
        btns = tk.Frame(self, bg="#eef2f7")
        btns.pack(fill="x", padx=15)
        for text, cmd in [("Add", self.add), ("Update", self.update),
                          ("Delete", self.delete), ("Clear", self.clear)]:
            ttk.Button(btns, text=text, command=cmd).pack(side="left", padx=4)

        tk.Label(btns, text="Search:", bg="#eef2f7").pack(side="left", padx=(30, 4))
        self.search_var = tk.StringVar()
        ttk.Entry(btns, textvariable=self.search_var, width=22).pack(side="left")
        ttk.Button(btns, text="Search", command=self.search).pack(side="left", padx=4)

        # Table
        cols = ("acc_no", "name", "gender", "phone", "email", "acc_type", "balance")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c, w in zip(cols, (80, 150, 70, 110, 190, 100, 100)):
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_data()

    # ---------- helpers ----------
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
        for r in rows:
            self.tree.insert("", tk.END, values=r)

    def on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.selected_acc = v[0]
        self.name.set(v[1])
        self.gender.set(v[2])
        self.phone.set(str(v[3]))
        self.email.set(v[4])
        self.acc_type.set(v[5])
        self.balance.set(v[6])

    # ---------- CRUD ----------
    def add(self):
        if not self.validate():
            return
        run_query("INSERT INTO accounts (name, gender, phone, email, acc_type, balance) "
                  "VALUES (%s,%s,%s,%s,%s,%s)",
                  (self.name.get().strip(), self.gender.get(), self.phone.get().strip(),
                   self.email.get().strip(), self.acc_type.get(), float(self.balance.get())))
        messagebox.showinfo("Success", "Account created successfully")
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
        if messagebox.askyesno("Confirm", f"Delete account {self.selected_acc}?"):
            run_query("DELETE FROM accounts WHERE acc_no=%s", (self.selected_acc,))
            messagebox.showinfo("Deleted", "Account deleted")
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

    # ---------- Extra feature: Deposit / Withdraw ----------
    def transaction(self, kind):
        if not self.selected_acc:
            messagebox.showwarning("Transaction", "Select an account from the table first")
            return
        win = tk.Toplevel(self)
        win.title(kind.title())
        win.geometry("280x140")
        win.grab_set()
        tk.Label(win, text=f"Amount to {kind}:").pack(pady=10)
        amt = ttk.Entry(win)
        amt.pack()
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
            messagebox.showinfo("Success", f"New balance: {new_bal:.2f}", parent=win)
            win.destroy()
            self.clear()
            self.load_data()

        ttk.Button(win, text=kind.title(), command=submit).pack(pady=10)


if __name__ == "__main__":
    try:
        setup_database()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Could not connect to MySQL:\n{err}")
        raise SystemExit
    BankApp().mainloop()
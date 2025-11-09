import sqlite3, os, random
from datetime import datetime, timedelta

# Ensure the database folder exists
os.makedirs("database", exist_ok=True)
db_path = os.path.join("database", "sample_database.db")

# Connect to SQLite
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Drop old tables
tables = [
    "departments", "employees", "projects", "attendance",
    "customers", "products", "orders", "order_items"
]
for t in tables:
    cur.execute(f"DROP TABLE IF EXISTS {t}")

# ---- Table Definitions ----
cur.executescript("""
CREATE TABLE departments (
  department_id INTEGER PRIMARY KEY AUTOINCREMENT,
  department_name TEXT NOT NULL
);

CREATE TABLE employees (
  employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  department_id INTEGER,
  salary REAL,
  hire_date TEXT,
  FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE projects (
  project_id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_name TEXT NOT NULL,
  department_id INTEGER,
  FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE attendance (
  record_id INTEGER PRIMARY KEY AUTOINCREMENT,
  employee_id INTEGER,
  date TEXT,
  status TEXT,
  FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  city TEXT,
  registration_date TEXT
);

CREATE TABLE products (
  product_id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_name TEXT,
  price REAL,
  stock INTEGER
);

CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER,
  order_date TEXT,
  total_amount REAL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
  order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER,
  product_id INTEGER,
  quantity INTEGER,
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);
""")

# ---- Insert Department Data ----
departments = [
    ('Engineering',), ('HR',), ('Finance',),
    ('Marketing',), ('Sales',), ('Support',),
    ('Research',), ('IT',), ('Operations',), ('Legal',)
]
cur.executemany("INSERT INTO departments (department_name) VALUES (?)", departments)

# ---- Employees ----
employees = [
    ('Aravind Kumar', 1, 70000, '2021-06-15'),
    ('Neha Singh', 2, 50000, '2022-03-10'),
    ('Rahul Das', 1, 65000, '2020-09-05'),
    ('Priya Sharma', 3, 85000, '2019-11-20'),
    ('Rohit Patel', 4, 60000, '2021-01-12'),
    ('Anjali Mehta', 5, 55000, '2023-02-18'),
]
cur.executemany(
    "INSERT INTO employees (name, department_id, salary, hire_date) VALUES (?, ?, ?, ?)", 
    employees
)

# ---- Projects ----
projects = [
    ('AI Chatbot System', 1),
    ('Recruitment Drive', 2),
    ('Financial Dashboard', 3),
    ('Brand Revamp', 4),
    ('CRM Automation', 5)
]
cur.executemany("INSERT INTO projects (project_name, department_id) VALUES (?, ?)", projects)

# ---- Attendance ----
statuses = ['Present', 'Absent', 'Leave']
base_date = datetime(2025, 11, 1)
for emp_id in range(1, 7):
    for i in range(1, 11):  # 10 days data
        day = base_date + timedelta(days=i)
        cur.execute(
            "INSERT INTO attendance (employee_id, date, status) VALUES (?, ?, ?)",
            (emp_id, day.strftime('%Y-%m-%d'), random.choice(statuses))
        )

# ---- Customers ----
customers = [
    ('Vikram Rao', 'Bangalore', '2024-11-01'),
    ('Kiran Das', 'Chennai', '2024-11-02'),
    ('Sneha Iyer', 'Mumbai', '2024-11-03'),
    ('Arun Nair', 'Delhi', '2024-11-04')
]
cur.executemany("INSERT INTO customers (name, city, registration_date) VALUES (?, ?, ?)", customers)

# ---- Products ----
products = [
    ('Laptop', 55000, 10),
    ('Mouse', 700, 100),
    ('Keyboard', 1200, 50),
    ('Monitor', 10000, 20),
    ('Headphones', 2500, 30)
]
cur.executemany("INSERT INTO products (product_name, price, stock) VALUES (?, ?, ?)", products)

# ---- Orders and Items ----
order_data = [
    (1, '2025-10-20', 57700),
    (2, '2025-10-21', 62000),
    (3, '2025-10-22', 13200),
]
cur.executemany("INSERT INTO orders (customer_id, order_date, total_amount) VALUES (?, ?, ?)", order_data)

order_items = [
    (1, 1, 1), (1, 2, 1),   # Order 1: Laptop + Mouse
    (2, 1, 1), (2, 5, 2),   # Order 2: Laptop + 2x Headphones
    (3, 3, 2), (3, 4, 1)    # Order 3: 2x Keyboards + 1x Monitor
]
cur.executemany("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)", order_items)

conn.commit()
conn.close()

print("✅ TechCorp database created successfully at:", db_path)

"""
SQL Review Scenarios — 26 query-review scenarios across easy, medium, and hard tiers.

Each scenario contains a broken or sub-optimal SQL query, the corrected version,
schema DDL, seed data, and grading hints.
"""


def load_scenarios():
    """Return a list of scenario dicts (9 easy, 9 medium, 8 hard = 26 total)."""
    return _EASY + _MEDIUM + _HARD


# ──────────────────────────────────────────────────────────────────────────────
# EASY scenarios (9) — wrong JOIN, missing WHERE, bad alias, type mismatch, etc.
# ──────────────────────────────────────────────────────────────────────────────

_EASY = [
    # easy_001 — wrong JOIN type (INNER instead of LEFT)
    {
        "id": "easy_001",
        "difficulty": "easy",
        "task_description": "Fix the query so that all users are listed even if they have no orders.",
        "issue_hint": "The query uses INNER JOIN, which drops users without orders. Use LEFT JOIN instead.",
        "known_issues": ["LEFT JOIN", "INNER JOIN", "missing rows"],
        "schema_ddl": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount REAL NOT NULL,
    created_at TEXT
);""",
        "seed_data": {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"},
                {"id": 3, "name": "Charlie", "email": None},
            ],
            "orders": [
                {"id": 1, "user_id": 1, "amount": 50.0, "created_at": "2024-01-10"},
                {"id": 2, "user_id": 1, "amount": 75.0, "created_at": "2024-02-15"},
                {"id": 3, "user_id": 2, "amount": 30.0, "created_at": "2024-03-01"},
            ],
        },
        "original_query": "SELECT u.name, o.amount FROM users u INNER JOIN orders o ON u.id = o.user_id;",
        "correct_query": "SELECT u.name, o.amount FROM users u LEFT JOIN orders o ON u.id = o.user_id;",
    },
    # easy_002 — missing WHERE clause
    {
        "id": "easy_002",
        "difficulty": "easy",
        "task_description": "Filter the products query to only show products that are in stock (quantity > 0).",
        "issue_hint": "The query returns all products including out-of-stock items. Add a WHERE clause.",
        "known_issues": ["WHERE", "filter", "quantity"],
        "schema_ddl": """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0
);""",
        "seed_data": {
            "products": [
                {"id": 1, "name": "Laptop", "price": 999.99, "quantity": 10},
                {"id": 2, "name": "Mouse", "price": 29.99, "quantity": 0},
                {"id": 3, "name": "Keyboard", "price": 59.99, "quantity": 5},
                {"id": 4, "name": "Monitor", "price": 399.99, "quantity": 0},
            ],
        },
        "original_query": "SELECT name, price FROM products;",
        "correct_query": "SELECT name, price FROM products WHERE quantity > 0;",
    },
    # easy_003 — incorrect column alias
    {
        "id": "easy_003",
        "difficulty": "easy",
        "task_description": "Fix the alias so the total column is named 'total_revenue' instead of 'total'.",
        "issue_hint": "The aggregate column alias is incorrect — it should be 'total_revenue'.",
        "known_issues": ["alias", "AS", "total_revenue"],
        "schema_ddl": """
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    amount REAL NOT NULL,
    sale_date TEXT
);""",
        "seed_data": {
            "sales": [
                {"id": 1, "product_id": 1, "amount": 100.0, "sale_date": "2024-01-01"},
                {"id": 2, "product_id": 1, "amount": 200.0, "sale_date": "2024-01-02"},
                {"id": 3, "product_id": 2, "amount": 150.0, "sale_date": "2024-01-03"},
            ],
        },
        "original_query": "SELECT product_id, SUM(amount) AS total FROM sales GROUP BY product_id;",
        "correct_query": "SELECT product_id, SUM(amount) AS total_revenue FROM sales GROUP BY product_id;",
    },
    # easy_004 — wrong aggregate function (AVG instead of SUM)
    {
        "id": "easy_004",
        "difficulty": "easy",
        "task_description": "Fix the query to compute the total salary per department instead of the average.",
        "issue_hint": "The query uses AVG() but should use SUM() to compute the total salary.",
        "known_issues": ["SUM", "AVG", "aggregate", "total"],
        "schema_ddl": """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL
);""",
        "seed_data": {
            "employees": [
                {"id": 1, "name": "Alice", "department": "Engineering", "salary": 90000},
                {"id": 2, "name": "Bob", "department": "Engineering", "salary": 85000},
                {"id": 3, "name": "Charlie", "department": "Marketing", "salary": 70000},
                {"id": 4, "name": "Diana", "department": "Marketing", "salary": 72000},
            ],
        },
        "original_query": "SELECT department, AVG(salary) AS total_salary FROM employees GROUP BY department;",
        "correct_query": "SELECT department, SUM(salary) AS total_salary FROM employees GROUP BY department;",
    },
    # easy_005 — type mismatch in WHERE
    {
        "id": "easy_005",
        "difficulty": "easy",
        "task_description": "Fix the WHERE clause — the status column is TEXT, but the query compares it to an integer.",
        "issue_hint": "Type mismatch: comparing TEXT column 'status' against integer 1 instead of string 'active'.",
        "known_issues": ["type mismatch", "status", "string", "active"],
        "schema_ddl": """
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'inactive',
    started_at TEXT
);""",
        "seed_data": {
            "sessions": [
                {"id": 1, "user_id": 1, "status": "active", "started_at": "2024-06-01"},
                {"id": 2, "user_id": 2, "status": "inactive", "started_at": "2024-06-02"},
                {"id": 3, "user_id": 1, "status": "active", "started_at": "2024-06-03"},
            ],
        },
        "original_query": "SELECT * FROM sessions WHERE status = 1;",
        "correct_query": "SELECT * FROM sessions WHERE status = 'active';",
    },
    # easy_006 — ORDER BY wrong column
    {
        "id": "easy_006",
        "difficulty": "easy",
        "task_description": "Fix the query to order invoices by total_amount descending, not by invoice_date.",
        "issue_hint": "The ORDER BY clause sorts by the wrong column — use total_amount DESC.",
        "known_issues": ["ORDER BY", "total_amount", "DESC", "sorting"],
        "schema_ddl": """
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    invoice_date TEXT NOT NULL
);""",
        "seed_data": {
            "invoices": [
                {"id": 1, "customer_id": 1, "total_amount": 500.0, "invoice_date": "2024-01-15"},
                {"id": 2, "customer_id": 2, "total_amount": 1200.0, "invoice_date": "2024-01-10"},
                {"id": 3, "customer_id": 1, "total_amount": 300.0, "invoice_date": "2024-02-20"},
            ],
        },
        "original_query": "SELECT * FROM invoices ORDER BY invoice_date DESC;",
        "correct_query": "SELECT * FROM invoices ORDER BY total_amount DESC;",
    },
    # easy_007 — missing GROUP BY
    {
        "id": "easy_007",
        "difficulty": "easy",
        "task_description": "Add a GROUP BY clause so the count is computed per category.",
        "issue_hint": "The query uses COUNT() but has no GROUP BY — results are aggregated across all rows.",
        "known_issues": ["GROUP BY", "COUNT", "category", "aggregate"],
        "schema_ddl": """
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL
);""",
        "seed_data": {
            "inventory": [
                {"id": 1, "item_name": "Widget A", "category": "Electronics", "quantity": 50},
                {"id": 2, "item_name": "Widget B", "category": "Electronics", "quantity": 30},
                {"id": 3, "item_name": "Gadget X", "category": "Toys", "quantity": 100},
                {"id": 4, "item_name": "Gadget Y", "category": "Toys", "quantity": 20},
            ],
        },
        "original_query": "SELECT category, COUNT(*) AS item_count FROM inventory;",
        "correct_query": "SELECT category, COUNT(*) AS item_count FROM inventory GROUP BY category;",
    },
    # easy_008 — missing LIMIT clause
    {
        "id": "easy_008",
        "difficulty": "easy",
        "task_description": "Add a LIMIT clause to return only the top 5 highest-paid employees.",
        "issue_hint": "The query returns all employees but should only return the top 5 by salary.",
        "known_issues": ["LIMIT", "top 5", "ORDER BY", "DESC"],
        "schema_ddl": """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL
);""",
        "seed_data": {
            "employees": [
                {"id": 1, "name": "Alice", "department": "Engineering", "salary": 120000},
                {"id": 2, "name": "Bob", "department": "Marketing", "salary": 85000},
                {"id": 3, "name": "Charlie", "department": "Engineering", "salary": 110000},
                {"id": 4, "name": "Diana", "department": "Sales", "salary": 95000},
                {"id": 5, "name": "Eve", "department": "Engineering", "salary": 130000},
                {"id": 6, "name": "Frank", "department": "Marketing", "salary": 78000},
                {"id": 7, "name": "Grace", "department": "Sales", "salary": 92000},
            ],
        },
        "original_query": "SELECT name, salary FROM employees ORDER BY salary DESC;",
        "correct_query": "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 5;",
    },
    # easy_009 — wrong comparison operator (= instead of LIKE)
    {
        "id": "easy_009",
        "difficulty": "easy",
        "task_description": "Fix the query to use LIKE with wildcard for partial name matching instead of exact match.",
        "issue_hint": "The query uses = for matching but the intent is to find names containing 'son' — use LIKE '%son%'.",
        "known_issues": ["LIKE", "wildcard", "pattern matching", "%"],
        "schema_ddl": """
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    city TEXT NOT NULL
);""",
        "seed_data": {
            "customers": [
                {"id": 1, "name": "Johnson", "email": "johnson@mail.com", "city": "NYC"},
                {"id": 2, "name": "Harrison", "email": "harrison@mail.com", "city": "LA"},
                {"id": 3, "name": "Smith", "email": "smith@mail.com", "city": "NYC"},
                {"id": 4, "name": "Erikson", "email": "erikson@mail.com", "city": "Chicago"},
                {"id": 5, "name": "Brown", "email": "brown@mail.com", "city": "LA"},
            ],
        },
        "original_query": "SELECT name, city FROM customers WHERE name = 'son';",
        "correct_query": "SELECT name, city FROM customers WHERE name LIKE '%son%';",
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# MEDIUM scenarios (9) — N+1 subquery, SELECT *, unnecessary DISTINCT, UNION, etc.
# ──────────────────────────────────────────────────────────────────────────────

_MEDIUM = [
    # medium_001 — N+1 correlated subquery → JOIN
    {
        "id": "medium_001",
        "difficulty": "medium",
        "task_description": "Replace the correlated subquery with a JOIN for better performance.",
        "issue_hint": "The query uses a correlated subquery to fetch user names — rewrite as a JOIN.",
        "known_issues": ["correlated subquery", "JOIN", "performance", "N+1"],
        "schema_ddl": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total REAL NOT NULL
);""",
        "seed_data": {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
            "orders": [
                {"id": 1, "user_id": 1, "total": 100.0},
                {"id": 2, "user_id": 1, "total": 200.0},
                {"id": 3, "user_id": 2, "total": 50.0},
            ],
        },
        "original_query": "SELECT o.id, o.total, (SELECT u.name FROM users u WHERE u.id = o.user_id) AS user_name FROM orders o;",
        "correct_query": "SELECT o.id, o.total, u.name AS user_name FROM orders o JOIN users u ON u.id = o.user_id;",
    },
    # medium_002 — SELECT * → specific columns
    {
        "id": "medium_002",
        "difficulty": "medium",
        "task_description": "Replace SELECT * with only the columns needed: name, email, and created_at.",
        "issue_hint": "SELECT * fetches unnecessary columns — select only what is needed.",
        "known_issues": ["SELECT *", "specific columns", "performance", "projection"],
        "schema_ddl": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    password_hash TEXT,
    created_at TEXT,
    updated_at TEXT,
    is_admin INTEGER DEFAULT 0
);""",
        "seed_data": {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com", "password_hash": "abc123", "created_at": "2024-01-01", "updated_at": "2024-06-01", "is_admin": 0},
                {"id": 2, "name": "Bob", "email": "bob@example.com", "password_hash": "def456", "created_at": "2024-02-01", "updated_at": "2024-06-15", "is_admin": 1},
            ],
        },
        "original_query": "SELECT * FROM users;",
        "correct_query": "SELECT name, email, created_at FROM users;",
    },
    # medium_003 — unnecessary DISTINCT
    {
        "id": "medium_003",
        "difficulty": "medium",
        "task_description": "Remove the unnecessary DISTINCT — the primary key already guarantees unique rows.",
        "issue_hint": "DISTINCT is unnecessary since the query selects from a single table by primary key.",
        "known_issues": ["DISTINCT", "unnecessary", "primary key", "performance"],
        "schema_ddl": """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
);""",
        "seed_data": {
            "products": [
                {"id": 1, "name": "Laptop", "category": "Electronics", "price": 999.99},
                {"id": 2, "name": "Phone", "category": "Electronics", "price": 699.99},
                {"id": 3, "name": "Desk", "category": "Furniture", "price": 299.99},
            ],
        },
        "original_query": "SELECT DISTINCT id, name, price FROM products WHERE category = 'Electronics';",
        "correct_query": "SELECT id, name, price FROM products WHERE category = 'Electronics';",
    },
    # medium_004 — redundant subquery
    {
        "id": "medium_004",
        "difficulty": "medium",
        "task_description": "Simplify the query by removing the redundant subquery — query the table directly.",
        "issue_hint": "The outer query wraps an unnecessary subquery that just selects everything.",
        "known_issues": ["redundant subquery", "simplify", "nested", "performance"],
        "schema_ddl": """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL
);""",
        "seed_data": {
            "employees": [
                {"id": 1, "name": "Alice", "department": "Engineering", "salary": 90000},
                {"id": 2, "name": "Bob", "department": "Marketing", "salary": 75000},
                {"id": 3, "name": "Charlie", "department": "Engineering", "salary": 95000},
            ],
        },
        "original_query": "SELECT * FROM (SELECT * FROM employees) AS t WHERE t.department = 'Engineering';",
        "correct_query": "SELECT * FROM employees WHERE department = 'Engineering';",
    },
    # medium_005 — missing index hint / inefficient OR
    {
        "id": "medium_005",
        "difficulty": "medium",
        "task_description": "Rewrite the OR conditions as a UNION ALL or use IN clause for better index usage.",
        "issue_hint": "Multiple OR conditions on the same column can be replaced with IN for clarity.",
        "known_issues": ["OR", "IN", "index", "performance"],
        "schema_ddl": """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    status TEXT NOT NULL,
    customer_id INTEGER NOT NULL,
    total REAL NOT NULL
);""",
        "seed_data": {
            "orders": [
                {"id": 1, "status": "pending", "customer_id": 1, "total": 100.0},
                {"id": 2, "status": "shipped", "customer_id": 2, "total": 250.0},
                {"id": 3, "status": "delivered", "customer_id": 1, "total": 75.0},
                {"id": 4, "status": "cancelled", "customer_id": 3, "total": 50.0},
            ],
        },
        "original_query": "SELECT * FROM orders WHERE status = 'pending' OR status = 'shipped' OR status = 'delivered';",
        "correct_query": "SELECT * FROM orders WHERE status IN ('pending', 'shipped', 'delivered');",
    },
    # medium_006 — HAVING vs WHERE placement
    {
        "id": "medium_006",
        "difficulty": "medium",
        "task_description": "Move the non-aggregate filter from HAVING to WHERE for efficiency.",
        "issue_hint": "The query filters on a non-aggregate column in HAVING — this should be in WHERE.",
        "known_issues": ["HAVING", "WHERE", "filter", "non-aggregate", "efficiency"],
        "schema_ddl": """
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    region TEXT NOT NULL,
    product TEXT NOT NULL,
    amount REAL NOT NULL
);""",
        "seed_data": {
            "sales": [
                {"id": 1, "region": "East", "product": "Widget", "amount": 100.0},
                {"id": 2, "region": "East", "product": "Gadget", "amount": 200.0},
                {"id": 3, "region": "West", "product": "Widget", "amount": 150.0},
                {"id": 4, "region": "West", "product": "Gadget", "amount": 300.0},
            ],
        },
        "original_query": "SELECT region, SUM(amount) AS total FROM sales GROUP BY region HAVING region = 'East';",
        "correct_query": "SELECT region, SUM(amount) AS total FROM sales WHERE region = 'East' GROUP BY region;",
    },
    # medium_007 — COUNT(*) vs COUNT(column) with NULLs
    {
        "id": "medium_007",
        "difficulty": "medium",
        "task_description": "Use COUNT(email) instead of COUNT(*) to count only users with non-NULL email.",
        "issue_hint": "COUNT(*) counts all rows including NULLs — use COUNT(email) to exclude NULLs.",
        "known_issues": ["COUNT", "NULL", "email", "aggregate"],
        "schema_ddl": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    department TEXT NOT NULL
);""",
        "seed_data": {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com", "department": "Engineering"},
                {"id": 2, "name": "Bob", "email": None, "department": "Engineering"},
                {"id": 3, "name": "Charlie", "email": "charlie@example.com", "department": "Marketing"},
                {"id": 4, "name": "Diana", "email": None, "department": "Marketing"},
            ],
        },
        "original_query": "SELECT department, COUNT(*) AS users_with_email FROM users GROUP BY department;",
        "correct_query": "SELECT department, COUNT(email) AS users_with_email FROM users GROUP BY department;",
    },
    # medium_008 — UNION where UNION ALL suffices
    {
        "id": "medium_008",
        "difficulty": "medium",
        "task_description": "Replace UNION with UNION ALL since the two queries select from different tables and duplicates are impossible.",
        "issue_hint": "UNION removes duplicates with an expensive sort, but these queries pull from separate tables — use UNION ALL.",
        "known_issues": ["UNION ALL", "UNION", "duplicate removal", "performance", "sort"],
        "schema_ddl": """
CREATE TABLE online_sales (
    id INTEGER PRIMARY KEY,
    product TEXT NOT NULL,
    amount REAL NOT NULL,
    sale_date TEXT NOT NULL
);
CREATE TABLE store_sales (
    id INTEGER PRIMARY KEY,
    product TEXT NOT NULL,
    amount REAL NOT NULL,
    sale_date TEXT NOT NULL
);""",
        "seed_data": {
            "online_sales": [
                {"id": 1, "product": "Laptop", "amount": 999.0, "sale_date": "2024-01-10"},
                {"id": 2, "product": "Phone", "amount": 699.0, "sale_date": "2024-01-15"},
            ],
            "store_sales": [
                {"id": 1, "product": "Tablet", "amount": 499.0, "sale_date": "2024-01-12"},
                {"id": 2, "product": "Mouse", "amount": 29.0, "sale_date": "2024-01-18"},
            ],
        },
        "original_query": "SELECT product, amount, sale_date FROM online_sales UNION SELECT product, amount, sale_date FROM store_sales;",
        "correct_query": "SELECT product, amount, sale_date FROM online_sales UNION ALL SELECT product, amount, sale_date FROM store_sales;",
    },
    # medium_009 — subquery in SELECT list → JOIN
    {
        "id": "medium_009",
        "difficulty": "medium",
        "task_description": "Move the subquery from the SELECT list into a JOIN for better readability and performance.",
        "issue_hint": "The scalar subquery in SELECT runs once per row — rewrite as a JOIN with aggregation.",
        "known_issues": ["scalar subquery", "JOIN", "performance", "SELECT list", "aggregate"],
        "schema_ddl": """
CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    salary REAL NOT NULL
);""",
        "seed_data": {
            "departments": [
                {"id": 1, "name": "Engineering"},
                {"id": 2, "name": "Marketing"},
                {"id": 3, "name": "Sales"},
            ],
            "employees": [
                {"id": 1, "name": "Alice", "department_id": 1, "salary": 90000},
                {"id": 2, "name": "Bob", "department_id": 1, "salary": 85000},
                {"id": 3, "name": "Charlie", "department_id": 2, "salary": 70000},
                {"id": 4, "name": "Diana", "department_id": 3, "salary": 80000},
            ],
        },
        "original_query": "SELECT d.name, (SELECT COUNT(*) FROM employees e WHERE e.department_id = d.id) AS emp_count FROM departments d;",
        "correct_query": "SELECT d.name, COUNT(e.id) AS emp_count FROM departments d LEFT JOIN employees e ON d.id = e.department_id GROUP BY d.id, d.name;",
    },
]

_HARD = [
    # hard_001 — correlated subquery → CTE for top-N per group
    {
        "id": "hard_001",
        "difficulty": "hard",
        "task_description": "Rewrite the correlated subquery using a CTE with ROW_NUMBER() to get the latest order per user.",
        "issue_hint": "The correlated subquery runs for each row — use a CTE with window function instead.",
        "known_issues": ["CTE", "ROW_NUMBER", "correlated subquery", "window function", "latest"],
        "schema_ddl": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount REAL NOT NULL,
    order_date TEXT NOT NULL
);""",
        "seed_data": {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 3, "name": "Charlie"},
            ],
            "orders": [
                {"id": 1, "user_id": 1, "amount": 100.0, "order_date": "2024-01-01"},
                {"id": 2, "user_id": 1, "amount": 250.0, "order_date": "2024-03-15"},
                {"id": 3, "user_id": 2, "amount": 75.0, "order_date": "2024-02-10"},
                {"id": 4, "user_id": 2, "amount": 300.0, "order_date": "2024-04-01"},
                {"id": 5, "user_id": 3, "amount": 50.0, "order_date": "2024-01-20"},
            ],
        },
        "original_query": "SELECT u.name, o.amount, o.order_date FROM users u JOIN orders o ON u.id = o.user_id WHERE o.order_date = (SELECT MAX(o2.order_date) FROM orders o2 WHERE o2.user_id = u.id);",
        "correct_query": "WITH ranked AS (SELECT user_id, amount, order_date, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date DESC) AS rn FROM orders) SELECT u.name, r.amount, r.order_date FROM users u JOIN ranked r ON u.id = r.user_id WHERE r.rn = 1;",
    },
    # hard_002 — multi-table JOIN with NULLs causing lost rows
    {
        "id": "hard_002",
        "difficulty": "hard",
        "task_description": "Fix the multi-table join so products without inventory and users without orders still appear.",
        "issue_hint": "INNER JOINs drop rows with NULLs in related tables — use LEFT JOINs.",
        "known_issues": ["LEFT JOIN", "NULL", "multi-table", "lost rows", "INNER JOIN"],
        "schema_ddl": """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT
);
CREATE TABLE inventory (
    product_id INTEGER PRIMARY KEY REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    order_id INTEGER
);""",
        "seed_data": {
            "products": [
                {"id": 1, "name": "Laptop", "category": "Electronics"},
                {"id": 2, "name": "Phone", "category": "Electronics"},
                {"id": 3, "name": "Desk", "category": "Furniture"},
            ],
            "inventory": [
                {"product_id": 1, "quantity": 50},
                {"product_id": 2, "quantity": 0},
            ],
            "order_items": [
                {"id": 1, "product_id": 1, "quantity": 2, "order_id": 101},
                {"id": 2, "product_id": 1, "quantity": 1, "order_id": 102},
            ],
        },
        "original_query": "SELECT p.name, i.quantity AS stock, SUM(oi.quantity) AS sold FROM products p JOIN inventory i ON p.id = i.product_id JOIN order_items oi ON p.id = oi.product_id GROUP BY p.id;",
        "correct_query": "SELECT p.name, COALESCE(i.quantity, 0) AS stock, COALESCE(SUM(oi.quantity), 0) AS sold FROM products p LEFT JOIN inventory i ON p.id = i.product_id LEFT JOIN order_items oi ON p.id = oi.product_id GROUP BY p.id, p.name;",
    },
    # hard_003 — window function: running total
    {
        "id": "hard_003",
        "difficulty": "hard",
        "task_description": "Add a running total column using a window function (SUM OVER) ordered by transaction_date.",
        "issue_hint": "The query only shows individual amounts — add a cumulative running total with a window function.",
        "known_issues": ["window function", "SUM OVER", "running total", "ROWS", "ORDER BY"],
        "schema_ddl": """
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    transaction_date TEXT NOT NULL
);""",
        "seed_data": {
            "transactions": [
                {"id": 1, "account_id": 1, "amount": 100.0, "transaction_date": "2024-01-01"},
                {"id": 2, "account_id": 1, "amount": -30.0, "transaction_date": "2024-01-05"},
                {"id": 3, "account_id": 1, "amount": 200.0, "transaction_date": "2024-01-10"},
                {"id": 4, "account_id": 2, "amount": 500.0, "transaction_date": "2024-01-02"},
                {"id": 5, "account_id": 2, "amount": -100.0, "transaction_date": "2024-01-08"},
            ],
        },
        "original_query": "SELECT account_id, amount, transaction_date FROM transactions ORDER BY account_id, transaction_date;",
        "correct_query": "SELECT account_id, amount, transaction_date, SUM(amount) OVER (PARTITION BY account_id ORDER BY transaction_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total FROM transactions ORDER BY account_id, transaction_date;",
    },
    # hard_004 — GROUP BY edge case: selecting non-aggregated column
    {
        "id": "hard_004",
        "difficulty": "hard",
        "task_description": "Fix the GROUP BY so all selected non-aggregate columns are grouped properly.",
        "issue_hint": "The query selects 'name' but does not GROUP BY it — results are undefined for that column.",
        "known_issues": ["GROUP BY", "non-aggregate", "ambiguous", "name column"],
        "schema_ddl": """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL
);""",
        "seed_data": {
            "employees": [
                {"id": 1, "name": "Alice", "department": "Engineering", "salary": 90000},
                {"id": 2, "name": "Bob", "department": "Engineering", "salary": 85000},
                {"id": 3, "name": "Charlie", "department": "Marketing", "salary": 70000},
                {"id": 4, "name": "Diana", "department": "Marketing", "salary": 72000},
                {"id": 5, "name": "Eve", "department": "Engineering", "salary": 95000},
            ],
        },
        "original_query": "SELECT department, name, MAX(salary) AS top_salary FROM employees GROUP BY department;",
        "correct_query": "WITH ranked AS (SELECT department, name, salary, ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn FROM employees) SELECT department, name, salary AS top_salary FROM ranked WHERE rn = 1;",
    },
    # hard_005 — HAVING vs WHERE confusion with aggregate
    {
        "id": "hard_005",
        "difficulty": "hard",
        "task_description": "Fix the query to correctly filter groups with total sales above 500 using HAVING, not WHERE.",
        "issue_hint": "The query tries to filter on an aggregate in WHERE but that's not allowed — move it to HAVING.",
        "known_issues": ["HAVING", "WHERE", "aggregate filter", "SUM", "GROUP BY"],
        "schema_ddl": """
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    salesperson TEXT NOT NULL,
    region TEXT NOT NULL,
    amount REAL NOT NULL,
    sale_date TEXT NOT NULL
);""",
        "seed_data": {
            "sales": [
                {"id": 1, "salesperson": "Alice", "region": "East", "amount": 300.0, "sale_date": "2024-01-01"},
                {"id": 2, "salesperson": "Alice", "region": "East", "amount": 250.0, "sale_date": "2024-01-15"},
                {"id": 3, "salesperson": "Bob", "region": "West", "amount": 100.0, "sale_date": "2024-02-01"},
                {"id": 4, "salesperson": "Bob", "region": "West", "amount": 150.0, "sale_date": "2024-02-20"},
                {"id": 5, "salesperson": "Charlie", "region": "East", "amount": 600.0, "sale_date": "2024-03-01"},
            ],
        },
        "original_query": "SELECT salesperson, SUM(amount) AS total_sales FROM sales WHERE SUM(amount) > 500 GROUP BY salesperson;",
        "correct_query": "SELECT salesperson, SUM(amount) AS total_sales FROM sales GROUP BY salesperson HAVING SUM(amount) > 500;",
    },
    # hard_006 — duplicate rows from bad join (cartesian-like)
    {
        "id": "hard_006",
        "difficulty": "hard",
        "task_description": "Fix the query that produces duplicate rows because it joins two one-to-many tables without aggregation.",
        "issue_hint": "Joining orders and returns directly on user_id creates a cartesian product — pre-aggregate each side.",
        "known_issues": ["duplicate rows", "cartesian product", "pre-aggregate", "subquery", "JOIN"],
        "schema_ddl": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount REAL NOT NULL
);
CREATE TABLE returns (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount REAL NOT NULL
);""",
        "seed_data": {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
            "orders": [
                {"id": 1, "user_id": 1, "amount": 100.0},
                {"id": 2, "user_id": 1, "amount": 200.0},
                {"id": 3, "user_id": 2, "amount": 50.0},
            ],
            "returns": [
                {"id": 1, "user_id": 1, "amount": 30.0},
                {"id": 2, "user_id": 1, "amount": 20.0},
            ],
        },
        "original_query": "SELECT u.name, SUM(o.amount) AS total_orders, SUM(r.amount) AS total_returns FROM users u LEFT JOIN orders o ON u.id = o.user_id LEFT JOIN returns r ON u.id = r.user_id GROUP BY u.id, u.name;",
        "correct_query": "SELECT u.name, COALESCE(o_agg.total_orders, 0) AS total_orders, COALESCE(r_agg.total_returns, 0) AS total_returns FROM users u LEFT JOIN (SELECT user_id, SUM(amount) AS total_orders FROM orders GROUP BY user_id) o_agg ON u.id = o_agg.user_id LEFT JOIN (SELECT user_id, SUM(amount) AS total_returns FROM returns GROUP BY user_id) r_agg ON u.id = r_agg.user_id;",
    },
    # hard_007 — self-join for hierarchical data → CTE
    {
        "id": "hard_007",
        "difficulty": "hard",
        "task_description": "Rewrite the self-join query using a recursive CTE to find employee-manager pairs including employees with no manager.",
        "issue_hint": "The self-join drops employees without managers. Use a LEFT JOIN or recursive CTE to preserve all employees.",
        "known_issues": ["self-join", "LEFT JOIN", "hierarchical", "manager", "NULL", "CTE"],
        "schema_ddl": """
CREATE TABLE staff (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    manager_id INTEGER REFERENCES staff(id),
    title TEXT NOT NULL
);""",
        "seed_data": {
            "staff": [
                {"id": 1, "name": "CEO Alice", "manager_id": None, "title": "CEO"},
                {"id": 2, "name": "VP Bob", "manager_id": 1, "title": "VP Engineering"},
                {"id": 3, "name": "Lead Charlie", "manager_id": 2, "title": "Tech Lead"},
                {"id": 4, "name": "Dev Diana", "manager_id": 3, "title": "Senior Developer"},
                {"id": 5, "name": "VP Eve", "manager_id": 1, "title": "VP Marketing"},
            ],
        },
        "original_query": "SELECT e.name AS employee, m.name AS manager FROM staff e JOIN staff m ON e.manager_id = m.id;",
        "correct_query": "SELECT e.name AS employee, COALESCE(m.name, 'No Manager') AS manager FROM staff e LEFT JOIN staff m ON e.manager_id = m.id;",
    },
    # hard_008 — LAG window function for day-over-day change
    {
        "id": "hard_008",
        "difficulty": "hard",
        "task_description": "Add a column showing the day-over-day revenue change using the LAG() window function.",
        "issue_hint": "The query only shows daily revenue — use LAG() to compute the difference from the previous day.",
        "known_issues": ["LAG", "window function", "day-over-day", "OVER", "ORDER BY", "difference"],
        "schema_ddl": """
CREATE TABLE daily_revenue (
    id INTEGER PRIMARY KEY,
    revenue_date TEXT NOT NULL UNIQUE,
    revenue REAL NOT NULL
);""",
        "seed_data": {
            "daily_revenue": [
                {"id": 1, "revenue_date": "2024-01-01", "revenue": 1000.0},
                {"id": 2, "revenue_date": "2024-01-02", "revenue": 1200.0},
                {"id": 3, "revenue_date": "2024-01-03", "revenue": 900.0},
                {"id": 4, "revenue_date": "2024-01-04", "revenue": 1500.0},
                {"id": 5, "revenue_date": "2024-01-05", "revenue": 1100.0},
            ],
        },
        "original_query": "SELECT revenue_date, revenue FROM daily_revenue ORDER BY revenue_date;",
        "correct_query": "SELECT revenue_date, revenue, revenue - LAG(revenue) OVER (ORDER BY revenue_date) AS daily_change FROM daily_revenue ORDER BY revenue_date;",
    },
]


import pandas as pd
import duckdb

# Connect to DuckDB (file-based or in-memory)
con = duckdb.connect("./data/library_db.duckdb")

# Load data from CSV files
books = pd.read_csv("./data/csv/book.csv")
checkouts = pd.read_csv("./data/csv/checkouts.csv")
users = pd.read_csv("./data/csv/users.csv")

# Ensure all values are converted to native Python types for compatibility
books = books.applymap(lambda x: int(x) if isinstance(x, (int, float)) else str(x))
checkouts = checkouts.applymap(lambda x: int(x) if isinstance(x, (int, float)) else str(x))
users = users.applymap(lambda x: int(x) if isinstance(x, (int, float)) else str(x))

# Initialize the `books` table with `book_id`
con.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INT,
    title VARCHAR,
    author VARCHAR,
    genre VARCHAR,
    description VARCHAR
)
""")

# Insert data into the `books` table
for _, row in books.iterrows():
    con.execute("""
        INSERT INTO books VALUES (?, ?, ?, ?, ?)
    """, tuple(row))

# Initialize the `user_checkouts` table with `book_id`
con.execute("""
CREATE TABLE IF NOT EXISTS user_checkouts (
    user_id INT,
    book_id INT
)
""")

# Insert data into the `user_checkouts` table
for _, row in checkouts.iterrows():
    con.execute("""
        INSERT INTO user_checkouts VALUES (?, ?)
    """, tuple(row))

# Initialize the `users` table with `user_id`
con.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INT,
    name VARCHAR,
    email VARCHAR,
    address VARCHAR
)
""")

# Insert data into the `users` table
for _, row in users.iterrows():
    con.execute("""
        INSERT INTO users VALUES (?, ?, ?, ?)
    """, tuple(row))

# Verify data upload
books_result = con.execute("SELECT * FROM books").fetchdf()
checkouts_result = con.execute("SELECT * FROM user_checkouts").fetchdf()
users_result = con.execute("SELECT * FROM users").fetchdf()

# Print the tables
print("Books Table:\n", books_result)
print("\nUser Checkouts Table:\n", checkouts_result)
print("\nUsers Table:\n", users_result)

# Close the connection
con.close()
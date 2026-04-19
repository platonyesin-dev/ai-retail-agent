import sqlite3

# We will use rule of "5 C's " for this set up 
def setup_database():
    # CONNECTION: Creare/Open file for our databse 
    conn = sqlite3.connect('retail_store.db')
    
    # CURSOR: Create our messenger with SQL
    cursor = conn.cursor()
    
    # COMMAND (Create): Tell our database what our table looks like
    # Create a table if it doesnt already exist and insert this columns 
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            base_price REAL,
            current_price REAL,
            days_on_shelf INTEGER,
            discount_reason TEXT,
            discount_type TEXT
        )
    ''')
    
    # 3. COMMAND (Insert): Take our mock data from 'engine'
    starting_inventory = [
        (101, "Organic Milk", "Dairy", 2.50, 2, 22, "None", "General discount"),
        (102, "Whole Wheat Bread", "Bakery", 3.00, 2.20, 22, "None", "General discount"),
        (103, "Apples (1kg)", "Produce", 1.50, 1.50, 5, "None", "General discount"),
        (104, "Chicken", "Meat", 4.50, 4.13, 2, "None", "General discount")
    ]
    
    # executemany command helps to import everything faster then running INSERT 4 separate times
    cursor.executemany('''
        INSERT INTO products (product_id, name, category, base_price, current_price, days_on_shelf, discount_reason, discount_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', starting_inventory)# The '?' marks are placeholders. To prevent SQL Injection (users trying to type sql commands in fields)
    
    # 4. COMMIT: Save changes to the hard drive 
    conn.commit()
    
    # 5. CLOSE: Lock the door od the db
    
    conn.close()
    
    print("Database 'retail_store.db' created and populated successfully!")

# Run the setup if we execute this specific file
if __name__ == "__main__":
    setup_database()
    
# pythonic way to add items to the db we have created 
import sqlite3

conn = sqlite3.connect('retail_store.db')
cursor = conn.cursor()

'''
    INSERT INTO products (product_id, name, category, base_price, current_price, days_on_shelf, discount_reason, discount_type)
    VALUES (105, 'Fresh Bananas', 'Fruit', 1.99, 1.50, 4, 'None', 'General discount')
'''


conn.commit()
conn.close()
print("✅ Item added!")
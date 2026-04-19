# Engine for computing new item prices deoending on the discount

# import real time features
from datetime import datetime
from printer import generate_price_tag
import sqlite3

# Functions to build 
'''
1. Fixed Percentage: (e.g., 20% off).
2. Conditional Logic: "If Category == 'Fresh', then 50% off."
3. Date-Based Logic: Use the datetime library to check if today == Friday.

''' 

class Product:
    # init runs whenever we create new product. It set ups intial state of the object
    def __init__(self, product_id, name, category, base_price, days_on_shelf):
        self.product_id = product_id
        self.name = name
        self.category = category
        # We make sure prices are always decimal numbers (NO strings)
        self.base_price = float(base_price)
        # current_price will be used to store our discounted price
        self.current_price = float(base_price)
        self.days_on_shelf = days_on_shelf
        # Reason of the discount
        self.discount_reason = "None"
        # Type of discount (subscribtion card, general discount)
        self.discount_type = "General discount"
        
    # We will be calling this function in the future to apply discount to the product
    # But we need to make sure new discount makes sense and doesnt break logic behind our DB
    def apply_discount(self, multiplier, reason):
        # Discounted price
        new_price = self.base_price * multiplier
        
        # Making sure price cant be negative
        if new_price < 0:
            new_price = 0.0
        
        if new_price < self.current_price:
            self.current_price = round(new_price, 2) # in case we have number 2.5444 it will remove all numbers after 2.54
            self.discount_reason = reason
        
            
    def __str__(self):
        """This makes printing the object look nice in the terminal."""
        # :<18 is used to structure output better, we want name to take up 18 charachters 
        # .2f is used to roud number to 2 decimals 
        return (
            f"[{self.product_id}] {self.name:<18} | "
            f"Original: €{self.base_price:.2f} | "
            f"Current: €{self.current_price:.2f} | "
            f"Rule: {self.discount_reason:<23} | "
            f"Discount Type: {self.discount_type}"
        )
            
# 2. THE PRICING ENGINE CLASS (The "Manager" that controls the rules)         
# In the precious one we build check rules to make sure everything is working and nothing breaks

class PricingEngine:
    def __init__(self):
        # List that holds product objects
        self.inventory = []    
        
    def add_product(self, product):
        # Function that adds all of the products to the inventory to be checked for discount later
        self.inventory.append(product)
        
    # We aslo write is_Friday None by deafault we can or give it manuanlly to the system or let the checker
    # of the date decide for us
    
    def discount_maker(self, is_Friday=None):
        if is_Friday is None:
            # Check the real world clock.
            current_day = datetime.now().weekday()
            # If weekday() is 4, it's Friday 
            is_Friday = (current_day == 4)
            
            if is_Friday:
                print("System detected it is Friday. Activating Friday Specials!")
            else:
                print("System detected it is NOT Friday. Standard pricing applies.")
            
        for item in self.inventory:
            # Now we create rules for automatic discounts 
            # Rule 1: Diary products need to be sold faster cuase expire faster
            if item.category == 'Dairy' and item.days_on_shelf >= 10:
                item.apply_discount(0.5, "Diary product clearance")
                # This continue makes sure we jump to the next object
                continue
            # Rule 2: If any item is on the shelf for 20 days -15%
            if item.days_on_shelf > 20:
                item.apply_discount(0.85, "Old item")
                continue
            # Rule 3: If item wasnt caught by previous checkers and today is Friday
            # then it goes to this block here
            if is_Friday:
                item.apply_discount(0.90, "10% Friday discount")
            # Rule 4: Identifies discount type 
            if item.current_price < item.base_price and item.category == "Meat":
                item.discount_type = "Member Card"
            
''' This is needed to go through sql database everytime tool is called and print all 
price tags needed together'''
def run_print_queue():
    # Coonect to this pecific database 
    conn = sqlite3.connect('retail_store.db')
    cursor = conn.cursor()
    
    # Find a product whos discount satus is NOT None
    try:
        cursor.execute(''' SELECT "product_id" , "name", "base_price", "current_price", "discount_type" 
        FROM products WHERE "discount_type" != 'None' ''')
        # We take all items that match query higher 
        items_to_print = cursor.fetchall()
    # In case something is broken and we cant get result it asks to check database
    except sqlite3.OperationalError as e: 
        print(f"❌ Database Error: {e}. (Check your table and column names!)")
        return
    
    if not items_to_print:
        print("Queue empty. No tags needed to be printed.")
        return
        
    # Go through results and rubn printer function
    
    for item in items_to_print:
        item_id = item[0]
        name = item[1]
        old_price = item[2]
        new_price = item[3]
        discount_type = item[4]
        
        print(f"Processing: {name}...")
        
        # Trigger tag generator 
        generate_price_tag(name, item_id, old_price, new_price, discount_type)
        
        # Update database 
        cursor.execute(''' UPDATE products SET "discount_type" = 'printed' WHERE "product_id" = ?''', (item_id,))
    
    # Save changes 
    conn.commit()
    conn.close()
    print("✅ All pending tags printed and database updated!")
        
        

                
# 3. THE EXECUTION BLOCK (The "Test Script")

# This command is really important cause it says "Execute part of the code below, ONLY 
# if im executing this specific file directly." If another file import this file later this part stays ignored.
if __name__ == "__main__":
    run_print_queue() # DIDNT GIVE PERCENTAGE TO THE TOOL SO IT SHOWS ON TAGS 0%
    
    '''
    # We are building our instance and naming it
    engine = PricingEngine()
    
    # Lets add some elements to play with
    engine.add_product(Product(101, "Organic Milk", "Dairy", 2.50, 22))
    engine.add_product(Product(102, "Whole Wheat Bread", "Bakery", 3.00, 22))
    engine.add_product(Product(103, "Apples (1kg)", "Produce", 1.50, 5))
    engine.add_product(Product(104, "Chicken", "Meat", 4.50, 2))
    
    # 3. Run the logic for discounts 
    engine.discount_maker(is_Friday=True)
    
    # 4. Print results for all items in the inventory
    for item in engine.inventory:
        print(item)
        '''
    
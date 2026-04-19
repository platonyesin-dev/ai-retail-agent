import sqlite3
import os
import printer
# To grab keys from .env
from dotenv import load_dotenv
from telegram import Update
from groq import Groq
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# open .env
load_dotenv()

# 🔑 Paste your BotFather token inside the quotes below!
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
# Async def used in case same function used by a lot of users and the same type 
# update: - when we text in the chat it packs everything in the box called Update
# context: basically toolkit that processes information 
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This function catches every message you type to the bot."""
    
    # Grab the text we typed on our phone
    user_message = update.message.text
    print(f"📥 Received message: {user_message}")
    
    status_message = await update.message.reply_text("🧠 LLM is analyzing request...")
    
    system_prompt = """
    You are an AI database assistant for a retail store. 
    The table is named 'products'. 
    
    RULES:
    1. UPDATING: To change an item, output an UPDATE command. You MUST add this exact phrase to the end so the system can read the new price: RETURNING product_id, name, category, base_price, current_price, days_on_shelf, discount_type, discount_reason
    2. ADDING: To add a new item, output an INSERT INTO command. Append the same RETURNING phrase to the end.
    3. DELETING: To remove an item, output a DELETE command.
    4. VIEWING: To find or print items, output a SELECT command. ALWAYS select: product_id, name, category, base_price, current_price, days_on_shelf, discount_type, discount_reason.
    5. SEARCHING: ALWAYS use LIKE with wildcards (e.g., WHERE name LIKE '%organic milk%'). Do NOT filter by category unless explicitly asked.
    6. SINGLE COMMAND: NEVER write more than one SQL statement. If the user asks to "update and print", ONLY write the UPDATE command with the RETURNING clause.
    7. FORMATTING: ONLY output the raw SQL code. No markdown or quotes.
    8. CRITICAL RULE: NEVER generate an UPDATE or DELETE command without a specific WHERE clause. You must always isolate the exact product or category the user is asking for using WHERE name LIKE '%...%' or WHERE category LIKE '%...%'.
    """

    try:
        # 1. Ask Llama 3.3 for the response
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile", 
        )
        
        ai_output = chat_completion.choices[0].message.content.strip()
        print(f"🤖 Raw AI Output: {ai_output}")
        
        # 2. CLEAN FIRST (Strip the markdown before we check the intent!)
        clean_sql = ai_output.replace('```sql', '').replace('```', '').replace('SQL', '').replace('sql', '').strip()
        
        # --- 🛡️ THE SAFETY GUARD ---
        if ("UPDATE" in clean_sql.upper() or "DELETE" in clean_sql.upper()) and "WHERE" not in clean_sql.upper():
            await status_message.edit_text("⚠️ Safety Alert: The AI tried to update all products at once. I blocked the transaction to protect the database. Please try rephrasing your request!")
            return # This stops the rest of the code from running
        
        # --- INTENT ROUTING ---
        
        # SCENARIO A: The user wants to change data (Update, Add, or Remove)
        if clean_sql.upper().startswith(("UPDATE", "INSERT", "DELETE")):
            
            # THE FIX: isolation_level=None turns on Autocommit to prevent locking!
            conn = sqlite3.connect('retail_store.db', isolation_level=None)
            cursor = conn.cursor()
            
            cursor.execute(clean_sql)
            
            # Catch the returning data
            results = cursor.fetchall() 
            
            # Figure out how many rows changed (using max safely covers UPDATES and DELETES)
            rows_changed = max(cursor.rowcount, len(results))
            
            # Notice we completely removed conn.commit() to simplify saving things
            conn.close()
            
            if rows_changed > 0:
                await status_message.edit_text(f"✅ Database Updated! Changed {rows_changed} item(s).\nExecuted:\n{clean_sql}")
                
                # check if printing tad was asked
                user_wants_tag = "print" in user_message.lower() or "tag" in user_message.lower()
                
                # If they asked for a tag, and we actually updated something
                if user_wants_tag and clean_sql.upper().startswith("UPDATE") and len(results) > 0:
                    await update.message.reply_text("🖨️ Generating the new discount tag...")
                    try:
                        item = results[0] 
                        
                        # call printer for that tag
                        image_path = printer.generate_price_tag(
                            product_name=item[1],
                            item_id=item[0],
                            old_price=item[3],
                            new_price=item[4],
                            discount_type=item[6]
                        )
                        
                        # get that specific tag from the directory 
                        if image_path:
                            with open(image_path, "rb") as tag_image:
                                await update.message.reply_photo(
                                    photo=tag_image,
                                    caption=f"🏷️ Here is the updated tag for {item[1]}!"
                                )
                    except Exception as e:
                        await update.message.reply_text(f"⚠️ Tag generation failed: {e}")
                        
            else:
                await status_message.edit_text(f"⚠️ Query ran safely, but no items matched.\nExecuted:\n{clean_sql}")
                
        # SCENARIO B: The user wants to view/print data
        elif clean_sql.upper().startswith("SELECT"):
            
            conn = sqlite3.connect('retail_store.db')
            cursor = conn.cursor()
            cursor.execute(clean_sql)
            results = cursor.fetchall() 
            conn.close()
            
            if len(results) > 0:
                # 1. Send the text receipt
                response_text = f"✅ Found {len(results)} item(s):\n\n"
                for row in results:
                    response_text += f"📦 {row[1]} (ID: {row[0]} | {row[2]})\n"
                    response_text += f"💰 Current: ${row[4]} (Base: ${row[3]})\n"
                    response_text += f"🏷️ Discount: {row[6]} | Reason: {row[7]}\n"
                    response_text += f"📅 Days on shelf: {row[5]}\n\n"
                
                await status_message.edit_text(response_text)
                # In case i want to look and also print that tag 
                # Just use the same chunck of code from scenario A
                user_wants_tag = "print" in user_message.lower() or "tag" in user_message.lower()
                
                if user_wants_tag:
                    await update.message.reply_text("🖨️ Generating the precise tag...")
                    try:
                        # Grab the very first item the database found
                        item = results[0] 
                        
                        # Database mapping: 
                        # item[0]=id, item[1]=name, item[3]=base_price, item[4]=current_price, item[6]=discount_type
                        
                        # 3. pass info to print the tag
                        image_path = printer.generate_price_tag(
                            product_name=item[1],
                            item_id=item[0],
                            old_price=item[3],
                            new_price=item[4],
                            discount_type=item[6]
                        )
                        
                        # 4. Send the exact image it just created
                        if image_path:
                            with open(image_path, "rb") as tag_image:
                                await update.message.reply_photo(
                                    photo=tag_image,
                                    caption=f"🏷️ Here is the updated tag for {item[1]}!"
                                )
                        else:
                            await update.message.reply_text("⚠️ Could not locate the template files.")
                            
                    except Exception as e:
                        await update.message.reply_text(f"⚠️ Tag generation failed: {e}")
            else:
                await status_message.edit_text(f"⚠️ No items found matching that request.\nExecuted:\n{clean_sql}")
            
    except sqlite3.Error as db_error:
        await status_message.edit_text(f"❌ Database Error: {db_error}")
        
    except Exception as e:
        await status_message.edit_text(f"❌ System Error: {e}")


if __name__ == '__main__':
    print("🟢 Starting Retail AI Bot...")
    
    # Build the bot using the token
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # add_handler is like adding specific rule when talking to a person
    # MessageHandler specifies that we care only abot text messages recieved from the user (cause we could also recieve clicks, paymnets etc)
    # Filters are: Only text, no commands accepted (/start), 
    # chat_handler this is our destination  
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))
    
    # Keep the script running and listening indefinitely
    print("🎧 Bot is actively listening for messages...")
    # This command keeps script in the loop so it always asks telegram fo updates 
    app.run_polling()
    
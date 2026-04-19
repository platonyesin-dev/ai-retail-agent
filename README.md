# 🛒 AI Retail Database Agent

An intelligent, multi-agent Telegram bot that allows store managers to control a retail database and instantly generate graphical price tags entirely through natural language. 

Instead of navigating complex software or writing SQL, users can simply text the bot commands like, *"Apply a 36% discount to the organic milk and print a member card tag,"* and the AI will handle the database transaction and render the graphics in seconds.

### ✨ Key Features
* **Natural Language to SQL:** Powered by Llama 3.3, the agent translates conversational text into perfectly formatted SQLite `UPDATE`, `INSERT`, `DELETE`, or `SELECT` commands.
* **Smart Intent Routing:** Custom Python logic intercepts the AI's output and routes it to the correct database pipeline, preventing accidental data overwrites and distinguishing between data-viewing and data-altering requests.
* **Dynamic Graphic Rendering:** Integrates with the Pillow (PIL) library to automatically draw highly customized, e-ink ready price tags. It dynamically inserts live database variables (Product ID, new prices, discount percentages, and dynamic QR codes) onto pre-designed `.png` templates.
* **Real-Time Data Handling:** Utilizes advanced SQLite operations (like `RETURNING` clauses and Python `isolation_level=None` Autocommit) to read and write data simultaneously without causing lock conflicts.

### 🧠 System Architecture
1. **User Input:** User sends a natural language message via Telegram.
2. **NLP Engine:** Groq processes the text and generates raw SQL.
3. **Python Router:** The system cleans the output and determines the query intent.
4. **Database Execution:** SQLite safely commits the change or fetches the data.
5. **Image Pipeline:** If the user requested a tag, the database immediately passes the updated row parameters directly to `printer.py`, which renders the new tag.
6. **Frontend Delivery:** The Telegram API sends back a formatted text receipt alongside the newly generated `.jpg` tag.

### 🛠️ Tech Stack
* **Language:** Python 3
* **AI/LLM:** Llama 3.3 (via Groq API)
* **Database:** SQLite
* **Graphics:** Pillow (PIL), qrcode, aggdraw
* **Interface:** python-telegram-bot

### 🚀 How to Run Locally
1. Clone this repository to your local machine.
2. Install the required libraries: 
   ```bash
   pip install python-telegram-bot pillow qrcode aggdraw groq
   
3. Create a .env file in the root directory and add your API keys:
   Code snippet
   ```bash
   TELEGRAM_TOKEN=your_telegram_bot_token
   GROQ_API_KEY=your_groq_api_key

4. Run the bot:
   ```bash
   python3 bot.py

5. Start chatting with your bot on Telegram!

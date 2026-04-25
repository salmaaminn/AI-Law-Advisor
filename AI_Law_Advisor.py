import mysql.connector
from groq import Groq
import os
from dotenv import load_dotenv
#configure

load_dotenv()
user = Groq(api_key=os.getenv("GROQ_API_KEY"))  
#Connect to MySQL
def connect_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database="law_intake"
    )

    return conn

#Create table if it doesn't exist

def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            request TEXT
        )
    """)

#input
def get_user_input():

    print("=== Client Processing System ===")
    
    name = input("Enter name: ")
    
    email = input("Enter email: ")
    if not email:
        print("Email cannot be empty.")
        return None
    
    request = input("Enter request: ")
    if not request:
        print("Request cannot be empty.")
        return None
    
    return name, email, request

def summarize_with_ai(message):
    prompt = f"""
You are an assistant for a Lawyer.
A user submitted the following request:

\"{message}\"

provide:
1. Summary: A 1-2 sentence summary of the request
2. Category: One of (Family Law, Criminal Law, Corporate Law, Real Estate Law, Urgent/Time Sensitive, General Inquiry)
3. Next Step: A recommended action for the Lawyer

Format your response exactly like this:
Summary: ...
Category: ...
Next Step: ...
"""
    response = user.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

#save to database
def store_user(cursor, conn, name, email, request, ai_summary):
    cursor.execute("""
        INSERT INTO clients (name, email, request,ai_summary)
        VALUES (%s, %s, %s,%s)
    """, (name, email, request, ai_summary))
    conn.commit()
    print("\nClient added successfully ")

#######format and print advisor view#######
def show_advisor_view(name, email, request, ai_summary):
    print("\n")
    print("=" * 50)
    print("           NEW USER RECEIVED")
    print("=" * 50)
    print(f"  Name:    {name}")
    print(f"  Email:   {email}")
    print(f"  Request: {request}")
    print("-" * 50)
    print("   AI ANALYSIS:")
    print()
    for line in ai_summary.strip().split("\n"):
        print(f"  {line}")
    print("=" * 50)
    print("   User saved to database successfully!")
    print("=" * 50)
    print()

#main

def main():

    conn = connect_db()

    cursor = conn.cursor()
    create_table(cursor)
    conn.commit()
    
    result = get_user_input()
    if result:
        name, email, request = result

        print("\n Analyzing request with AI...")

        ai_summary = summarize_with_ai(request)
        print("\n--- AI Analysis ---")
        print(ai_summary)
        print("-------------------")
        store_user(cursor, conn, name, email, request,ai_summary)
        show_advisor_view(name, email, request, ai_summary)
    cursor.close()
    conn.close()
main()

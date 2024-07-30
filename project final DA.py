import sqlite3
import datetime

# Default subscription plans with prices
default_plans = {
    'Spotify': {'Free': 0, 'Premium': 9.99, 'Family': 14.99},
    'Netflix': {'Basic': 8.99, 'Standard': 12.99, 'Premium': 15.99},
    'Hotstar': {'VIP': 5.99, 'Premium': 9.99}
}

# Function to register a new user
def register_user(conn, cur):
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    # Check if username already exists
    cur.execute('''SELECT * FROM users WHERE username = ?''', (username,))
    existing_user = cur.fetchone()
    if existing_user:
        print("User is already registered.")
    else:
        cur.execute('''INSERT INTO users (username, password) VALUES (?, ?)''', (username, password))
        conn.commit()
        print("User registered successfully!")

# Function to authenticate a user
def authenticate_user(cur):
    username = input("Enter username: ")
    password = input("Enter password: ")
    cur.execute('''SELECT * FROM users WHERE username = ? AND password = ?''', (username, password))
    user = cur.fetchone()
    if user:
        print("Login successful!")
        return user[0]  # Returning user_id
    else:
        print("Invalid username or password.")
        return None

# Function to add a new subscription for a specific user
def add_subscription(conn, cur, user_id):
    service_name = input("Enter service name (e.g., Spotify, Netflix, Hotstar, etc.): ")
    
    # Display available plans with prices
    print("Available plans:")
    for plan, price in default_plans.get(service_name, {}).items():
        print(f"{plan}: ${price}")
    
    plan_name = input("Enter plan name: ")
    
    # Get current date
    current_date = datetime.date.today()
    
    # Get start date of subscription
    start_date = input("Enter subscription start date (YYYY-MM-DD): ")
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    
    # Check if start date is not more than 9 months older than the present date
    if (current_date - start_date) > datetime.timedelta(days=9*30):
        print("Invalid start date. Start date cannot be more than 9 months older than the present date.")
        return
    
    # Get end date of subscription
    end_date = input("Enter subscription end date (YYYY-MM-DD): ")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # Check if end date is not earlier than the present day
    if end_date < current_date:
        print("Invalid end date. End date cannot be earlier than the present day.")
        return
    
    # Add subscription to the database
    cur.execute('''INSERT INTO subscriptions (user_id, service_name, plan_name, subscription_start_date, subscription_end_date)
                    VALUES (?, ?, ?, ?, ?)''', (user_id, service_name, plan_name, start_date, end_date))
    conn.commit()
    print("Subscription added successfully!")

# Function to delete a subscription for a specific user
def delete_subscription(conn, cur, user_id):
    subscription_id = input("Enter subscription ID to delete: ")
    cur.execute('''DELETE FROM subscriptions WHERE id = ? AND user_id = ?''', (subscription_id, user_id))
    conn.commit()
    print("Subscription deleted successfully!")

# Function to display all subscriptions for a specific user
def display_subscriptions(cur, user_id):
    cur.execute('''SELECT * FROM subscriptions WHERE user_id = ?''', (user_id,))
    subscriptions = cur.fetchall()
    print("Subscriptions:")
    for subscription in subscriptions:
        print(subscription)

# Function to display all subscriptions taken by different users
def display_all_subscriptions(cur):
    cur.execute('''SELECT * FROM subscriptions''')
    subscriptions = cur.fetchall()
    print("All Subscriptions:")
    for subscription in subscriptions:
        print(subscription)

# Function to display registered users
def display_registered_users(cur):
    cur.execute('''SELECT * FROM users''')
    users = cur.fetchall()
    print("Registered Users:")
    for user in users:
        print(user)

# Function to alert about expiring subscriptions for a specific user
def alert_expiring_subscriptions(cur, user_id):
    today = datetime.date.today().strftime("%Y-%m-%d")
    cur.execute('''SELECT * FROM subscriptions WHERE subscription_end_date = ? AND user_id = ?''', (today, user_id))
    expiring_subscriptions = cur.fetchall()
    if expiring_subscriptions:
        print("Alert: The following subscriptions are expiring today:")
        for subscription in expiring_subscriptions:
            print(subscription)
    else:
        print("No subscriptions are expiring today.")

# Function to update a subscription for a specific user
def update_subscription(conn, cur, user_id):
    subscription_id = input("Enter subscription ID to update: ")
    start_date = input("Enter new subscription start date (YYYY-MM-DD): ")
    end_date = input("Enter new subscription end date (YYYY-MM-DD): ")
    
    cur.execute('''UPDATE subscriptions 
                    SET subscription_start_date = ?, subscription_end_date = ?
                    WHERE id = ? AND user_id = ?''', (start_date, end_date, subscription_id, user_id))
    conn.commit()
    print("Subscription updated successfully!")

# Function to generate revenue report
def generate_revenue_report(cur):
    cur.execute('''SELECT service_name, COUNT(*) AS total_subscriptions, 
               (strftime('%Y',subscription_end_date) - strftime('%Y',subscription_start_date)) * 12 + 
               (strftime('%m',subscription_end_date) - strftime('%m',subscription_start_date)) AS total_months
               FROM subscriptions
               GROUP BY service_name''')
    revenue_report = cur.fetchall()
    print("Revenue Report:")
    for entry in revenue_report:
        service_name, total_subscriptions, total_months = entry
        total_revenue = total_subscriptions * total_months * default_plans[service_name]['Premium']  # Assuming all plans are 'Premium'
        print(f"Service: {service_name}, Total Subscriptions: {total_subscriptions}, Total Months: {total_months}, Total Revenue: ${total_revenue:.2f}")

# Connect to SQLite database
conn = sqlite3.connect('subscriptions.db')
cur = conn.cursor()

# Create table for users if not exists
cur.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT)''')

# Create table for subscriptions if not exists
cur.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                service_name TEXT,
                plan_name TEXT,
                subscription_start_date DATE,
                subscription_end_date DATE)''')

# Main loop
while True:
    print("\nOptions:")
    print("1. Register")
    print("2. Login")
    print("3. Display All Subscriptions")
    print("4. Display Registered Users")
    print("5. Generate Revenue Report")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == '1':
        register_user(conn, cur)
    elif choice == '2':
        user_id = authenticate_user(cur)
        if user_id:
            # Menu for authenticated users
            while True:
                print("\nAuthenticated User Options:")
                print("1. Add Subscription")
                print("2. Delete Subscription")
                print("3. Display Subscriptions")
                print("4. Alert Expiring Subscriptions")
                print("5. Update Subscription")
                print("6. Logout")

                user_choice = input("Enter your choice: ")

                if user_choice == '1':
                    add_subscription(conn, cur, user_id)
                elif user_choice == '2':
                    delete_subscription(conn, cur, user_id)
                elif user_choice == '3':
                    display_subscriptions(cur, user_id)
                elif user_choice == '4':
                    alert_expiring_subscriptions(cur, user_id)
                elif user_choice == '5':
                    update_subscription(conn, cur, user_id)
                elif user_choice == '6':
                    print("Logged out successfully.")
                    break
                else:
                    print("Invalid choice. Please try again.")
    elif choice == '3':
        display_all_subscriptions(cur)
    elif choice == '4':
        display_registered_users(cur)
    elif choice == '5':
        generate_revenue_report(cur)
    elif choice == '6':
        break
    else:
        print("Invalid choice. Please try again.")

# Close the connection
conn.close()

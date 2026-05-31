import sqlite3
import streamlit as st
from datetime import datetime

# DB Connection
def get_db_connection():
    conn = sqlite3.connect('train_database.db')
    return conn

# Create Tables
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trains (
        train_id INTEGER PRIMARY KEY,
        train_name TEXT,
        source_station TEXT,
        destination_station TEXT,
        departure_time TEXT,
        arrival_time TEXT,
        ticket_price REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS passengers (
        passenger_id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        gender TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id INTEGER PRIMARY KEY,
        passenger_id INTEGER,
        train_id INTEGER,
        booking_time TEXT,
        FOREIGN KEY(passenger_id) REFERENCES passengers(passenger_id),
        FOREIGN KEY(train_id) REFERENCES trains(train_id)
    )
    ''')

    # Insert admin account if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES ('admin', 'admin123', 'admin')")

    conn.commit()
    conn.close()

# Login check
def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Register new user
def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Add train
def insert_train(train_name, source, destination, departure_time, arrival_time, ticket_price):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trains (train_name, source_station, destination_station, departure_time, arrival_time, ticket_price)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (train_name, source, destination, departure_time, arrival_time, ticket_price))
    conn.commit()
    conn.close()

# Add passenger
def insert_passenger(name, age, gender):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO passengers (name, age, gender) VALUES (?, ?, ?)", (name, age, gender))
    conn.commit()
    conn.close()

# Book ticket
def book_ticket(passenger_id, train_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO tickets (passenger_id, train_id, booking_time) VALUES (?, ?, ?)",
                   (passenger_id, train_id, time_now))
    conn.commit()
    conn.close()

# Fetch all
def get_all_trains():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trains")
    return cursor.fetchall()

def get_all_passengers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passengers")
    return cursor.fetchall()

def get_all_tickets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    return cursor.fetchall()

# Main app
def main():
    st.set_page_config("Train Booking", layout="centered")
    create_tables()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.page = "login"

    if not st.session_state.logged_in:

        if st.session_state.page == "login":
            st.title("🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                user = login_user(username, password)
                if user:
                    st.success(f"Welcome {user[0]} ({user[2]})")
                    st.session_state.logged_in = True
                    st.session_state.username = user[0]
                    st.session_state.role = user[2]
                else:
                    st.error("Invalid credentials.")
            st.markdown("Don't have an account? [Register now](#)", unsafe_allow_html=True)
            if st.button("Go to Register"):
                st.session_state.page = "register"
                st.rerun()

        elif st.session_state.page == "register":
            st.title("📝 Register New User")
            username = st.text_input("Choose a Username")
            password = st.text_input("Choose a Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            if st.button("Register"):
                if password != confirm:
                    st.error("Passwords do not match.")
                elif not username or not password:
                    st.warning("All fields are required.")
                else:
                    success = register_user(username, password)
                    if success:
                        st.success("Account created! You can now login.")
                        st.session_state.page = "login"
                    else:
                        st.error("Username already exists.")
            if st.button("Back to Login"):
                st.session_state.page = "login"
                st.rerun()

        return

    # Logged in section
    st.sidebar.title(f"🚆 Welcome, {st.session_state.username}")
    role = st.session_state.role

    menu = ["View Trains", "View Tickets", "Logout"]
    if role == "admin":
        menu = ["Add Train"] + menu
    elif role == "user":
        menu = ["Add Passenger", "Book Ticket"] + menu

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()

    elif choice == "Add Train":
        st.subheader("➕ Add New Train")
        name = st.text_input("Train Name")
        source = st.text_input("Source")
        dest = st.text_input("Destination")
        dep_date = st.date_input("Departure Date")
        dep_time = st.time_input("Departure Time")
        arr_date = st.date_input("Arrival Date")
        arr_time = st.time_input("Arrival Time")
        price = st.number_input("Ticket Price", min_value=1.0)

        if st.button("Add Train"):
            dep = f"{dep_date} {dep_time}"
            arr = f"{arr_date} {arr_time}"
            insert_train(name, source, dest, dep, arr, price)
            st.success("✅ Train added.")

    elif choice == "View Trains":
        st.subheader("🚂 All Trains")
        trains = get_all_trains()
        if trains:
            for t in trains:
                st.write(f"**{t[1]}** ({t[0]}) from {t[2]} to {t[3]} - ₹{t[6]}")
                st.caption(f"Departs: {t[4]} | Arrives: {t[5]}")
                st.markdown("---")
        else:
            st.info("No trains found.")

    elif choice == "Add Passenger":
        st.subheader("👤 Add Passenger")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        if st.button("Add Passenger"):
            insert_passenger(name, age, gender)
            st.success("✅ Passenger added.")

    elif choice == "Book Ticket":
        st.subheader("🎟️ Book Ticket")
        passengers = get_all_passengers()
        trains = get_all_trains()

        if not passengers or not trains:
            st.warning("Add passengers and trains first.")
        else:
            p_name = st.selectbox("Select Passenger", [p[1] for p in passengers])
            t_name = st.selectbox("Select Train", [t[1] for t in trains])

            p_id = next(p[0] for p in passengers if p[1] == p_name)
            t_id = next(t[0] for t in trains if t[1] == t_name)

            if st.button("Confirm Booking"):
                book_ticket(p_id, t_id)
                st.success(f"✅ Ticket booked for {p_name} on {t_name}.")

    elif choice == "View Tickets":
        st.subheader("📄 Booked Tickets")
        tickets = get_all_tickets()
        passengers = get_all_passengers()
        trains = get_all_trains()

        if not tickets:
            st.info("No tickets booked.")
        else:
            for tk in tickets:
                p_name = next((p[1] for p in passengers if p[0] == tk[1]), "Unknown")
                t_name = next((t[1] for t in trains if t[0] == tk[2]), "Unknown")
                st.write(f"Ticket #{tk[0]}: {p_name} → {t_name} at {tk[3]}")
                st.markdown("---")

if __name__ == "__main__":
    main()

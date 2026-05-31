import sqlite3
import streamlit as st
from datetime import datetime


# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('train_database.db')
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn


# Create the tables if they don't exist
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trains (
        train_id INTEGER PRIMARY KEY,
        train_name TEXT NOT NULL,
        source_station TEXT NOT NULL,
        destination_station TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        arrival_time TEXT NOT NULL,
        ticket_price REAL NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS passengers (
        passenger_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id INTEGER PRIMARY KEY,
        passenger_id INTEGER,
        train_id INTEGER,
        booking_time TEXT NOT NULL,
        FOREIGN KEY(passenger_id) REFERENCES passengers(passenger_id),
        FOREIGN KEY(train_id) REFERENCES trains(train_id)
    )
    ''')

    conn.commit()
    conn.close()


# Insert a new train
def insert_train(train_name, source, destination, departure_time, arrival_time, ticket_price):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO trains (train_name, source_station, destination_station, departure_time, arrival_time, ticket_price)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (train_name, source, destination, departure_time.strftime('%Y-%m-%d %H:%M:%S'),
          arrival_time.strftime('%Y-%m-%d %H:%M:%S'), ticket_price))
    conn.commit()
    conn.close()


# Update an existing train's departure and arrival time
def update_train_times(train_id, new_departure, new_arrival):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE trains
    SET departure_time = ?, arrival_time = ?
    WHERE train_id = ?
    ''', (new_departure.strftime('%Y-%m-%d %H:%M:%S'),
          new_arrival.strftime('%Y-%m-%d %H:%M:%S'),
          train_id))
    conn.commit()
    conn.close()


# Delete a train
def delete_train(train_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # First delete all tickets associated with this train
    cursor.execute('DELETE FROM tickets WHERE train_id = ?', (train_id,))

    # Then delete the train
    cursor.execute('DELETE FROM trains WHERE train_id = ?', (train_id,))

    conn.commit()
    conn.close()
    st.rerun()


# Insert a new passenger
def insert_passenger(name, age, gender):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO passengers (name, age, gender)
    VALUES (?, ?, ?)
    ''', (name, age, gender))
    conn.commit()
    conn.close()


# Insert a new ticket booking
def book_ticket(passenger_id, train_id):
    booking_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO tickets (passenger_id, train_id, booking_time)
    VALUES (?, ?, ?)
    ''', (passenger_id, train_id, booking_time))
    conn.commit()
    conn.close()


# Delete a ticket
def delete_ticket(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tickets WHERE ticket_id = ?', (ticket_id,))
    conn.commit()
    conn.close()
    st.rerun()


# View all trains
def get_all_trains():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trains')
    trains = cursor.fetchall()
    conn.close()
    return trains


# View all passengers
def get_all_passengers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM passengers')
    passengers = cursor.fetchall()
    conn.close()
    return passengers


# View all booked tickets
def get_all_tickets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT t.ticket_id, p.name, tr.train_name, t.booking_time, tr.train_id
    FROM tickets t
    JOIN passengers p ON t.passenger_id = p.passenger_id
    JOIN trains tr ON t.train_id = tr.train_id
    ''')
    tickets = cursor.fetchall()
    conn.close()
    return tickets


# Streamlit interface
def main():
    st.title("Train Database Management with Ticket Booking System")

    # Create tables if they don't exist
    create_tables()

    menu = ["Home", "Add Train", "View/Update/Delete Trains", "Add Passenger", "Book Ticket", "View/Delete Tickets"]
    choice = st.sidebar.selectbox("Select Option", menu)

    if choice == "Home":
        st.subheader("Welcome to the Train Database Management System")
        st.write("Choose an option from the sidebar to start managing the train database.")

    elif choice == "Add Train":
        st.subheader("Add a New Train")
        train_name = st.text_input("Train Name")
        source_station = st.text_input("Source Station")
        destination_station = st.text_input("Destination Station")

        col1, col2 = st.columns(2)
        with col1:
            departure_date = st.date_input("Departure Date", min_value=datetime.today())
            departure_time = st.time_input("Departure Time")
        with col2:
            arrival_date = st.date_input("Arrival Date", min_value=departure_date)
            arrival_time = st.time_input("Arrival Time")

        departure_datetime = datetime.combine(departure_date, departure_time)
        arrival_datetime = datetime.combine(arrival_date, arrival_time)

        ticket_price = st.number_input("Ticket Price", min_value=1.0)

        if st.button("Add Train"):
            if train_name and source_station and destination_station and ticket_price:
                insert_train(train_name, source_station, destination_station, departure_datetime, arrival_datetime,
                             ticket_price)
                st.success("Train added successfully!")
            else:
                st.error("Please fill in all fields.")

    elif choice == "View/Update/Delete Trains":
        st.subheader("View/Update/Delete Trains")
        trains = get_all_trains()

        if trains:
            for train in trains:
                st.write(f"**Train ID:** {train[0]}")
                st.write(f"**Train Name:** {train[1]}")
                st.write(f"**Source Station:** {train[2]}")
                st.write(f"**Destination Station:** {train[3]}")

                # Handle datetime parsing more robustly
                try:
                    dep_time_str = train[4].split('.')[0] if '.' in train[4] else train[4]
                    arr_time_str = train[5].split('.')[0] if '.' in train[5] else train[5]

                    dep_time = datetime.strptime(dep_time_str, '%Y-%m-%d %H:%M:%S')
                    arr_time = datetime.strptime(arr_time_str, '%Y-%m-%d %H:%M:%S')

                    st.write(f"**Departure Time:** {dep_time}")
                    st.write(f"**Arrival Time:** {arr_time}")
                except ValueError as e:
                    st.write(f"**Departure Time:** {train[4]} (Invalid format)")
                    st.write(f"**Arrival Time:** {train[5]} (Invalid format)")
                    continue

                st.write(f"**Ticket Price:** ${train[6]:.2f}")

                with st.expander("Update Train Times"):
                    new_dep_date = st.date_input("New Departure Date", value=dep_time.date(),
                                                 key=f"dep_date_{train[0]}")
                    new_dep_time = st.time_input("New Departure Time", value=dep_time.time(),
                                                 key=f"dep_time_{train[0]}")
                    new_arr_date = st.date_input("New Arrival Date", value=arr_time.date(), key=f"arr_date_{train[0]}")
                    new_arr_time = st.time_input("New Arrival Time", value=arr_time.time(), key=f"arr_time_{train[0]}")

                    new_dep_datetime = datetime.combine(new_dep_date, new_dep_time)
                    new_arr_datetime = datetime.combine(new_arr_date, new_arr_time)

                    if st.button("Update Times", key=f"update_{train[0]}"):
                        update_train_times(train[0], new_dep_datetime, new_arr_datetime)
                        st.success("Train times updated successfully!")
                        st.rerun()

                if st.button(f"Delete Train {train[0]}", key=f"delete_train_{train[0]}"):
                    delete_train(train[0])
                    st.success(f"Train {train[0]} deleted successfully!")

                st.write("---")
        else:
            st.write("No trains found.")

    elif choice == "Add Passenger":
        st.subheader("Add a New Passenger")
        name = st.text_input("Passenger Name")
        age = st.number_input("Age", min_value=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        if st.button("Add Passenger"):
            if name and age and gender:
                insert_passenger(name, age, gender)
                st.success("Passenger added successfully!")
            else:
                st.error("Please fill in all fields.")

    elif choice == "Book Ticket":
        st.subheader("Book a Ticket")
        passengers = get_all_passengers()
        trains = get_all_trains()

        if not passengers:
            st.warning("No passengers available. Please add passengers first.")
            return
        if not trains:
            st.warning("No trains available. Please add trains first.")
            return

        passenger_name = st.selectbox("Select Passenger", [p[1] for p in passengers])
        train_name = st.selectbox("Select Train", [t[1] for t in trains])

        # Find the corresponding passenger_id and train_id
        passenger_id = [p[0] for p in passengers if p[1] == passenger_name][0]
        train_id = [t[0] for t in trains if t[1] == train_name][0]

        # Get the ticket price for the selected train
        ticket_price = [t[6] for t in trains if t[0] == train_id][0]

        st.write(f"**Ticket Price:** ${ticket_price:.2f}")

        ticket_count = st.number_input("Number of Tickets", min_value=1, step=1, value=1)

        if st.button("Book Tickets"):
            for _ in range(ticket_count):
                book_ticket(passenger_id, train_id)
            st.success(f"{ticket_count} tickets booked for {passenger_name} on {train_name}!")

    elif choice == "View/Delete Tickets":
        st.subheader("View/Delete Booked Tickets")
        tickets = get_all_tickets()

        if tickets:
            for ticket in tickets:
                st.write(f"**Ticket ID:** {ticket[0]}")
                st.write(f"**Passenger Name:** {ticket[1]}")
                st.write(f"**Train Name:** {ticket[2]}")
                st.write(f"**Booking Time:** {ticket[3]}")

                if st.button(f"Delete Ticket {ticket[0]}", key=f"delete_ticket_{ticket[0]}"):
                    delete_ticket(ticket[0])
                    st.success(f"Ticket {ticket[0]} deleted successfully!")

                st.write("---")
        else:
            st.write("No tickets found.")


if __name__ == "__main__":
    main()
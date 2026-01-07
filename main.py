from flask import Flask, render_template, request

app = Flask(__name__)

# --- 1. Database Configuration ---
# Update these details to match your MySQL Workbench setup
db_config = {
    'user': 'root',  # Your MySQL username
    'password': 'password',  # Your MySQL password
    'host': 'localhost',
    'database': 'AirlineDB'
}


# --- 2. The Home Route ---
# This serves your HTML page when you open the site
@app.route('/')
def home():
    return render_template('home_page.html')


# --- 3. The Search Route ---
# This runs when the user clicks "Search Flights"
@app.route('/search', methods=['POST'])
def search_flights():
    # A. Collect the data from the HTML form
    flight_num = request.form.get('flight_num')

    # Source Details
    src_country = request.form.get('source_country')
    src_city = request.form.get('source_city')
    src_airport = request.form.get('source_airport')

    # Destination Details
    dst_country = request.form.get('dest_country')
    dst_city = request.form.get('dest_city')
    dst_airport = request.form.get('dest_airport')

    # Dates
    exit_date = request.form.get('exit_date')
    return_date = request.form.get('return_date')  # This might be empty!

    # B. Logic Check (Just for debugging right now)
    print("--- New Search Request ---")
    print(f"From: {src_city}, {src_country} ({src_airport})")
    print(f"To: {dst_city}, {dst_country} ({dst_airport})")
    print(f"Date: {exit_date}")
    if return_date:
        print(f"Return Date requested: {return_date}")

    # C. (Future Step) Insert your SQL Query here to actually find flights
    # results = ...

    return "Search received! Check your PyCharm terminal to see the data."


# --- 4. Run the App ---
if __name__ == '__main__':
    app.run(debug=True)
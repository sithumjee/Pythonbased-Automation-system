from flask import Flask, request, render_template, redirect, url_for, flash, send_file
import sqlite3
import csv
import os
from scraper import scrape_ecommerce_site  # Import the scraper function

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')  # Create or connect to a database
    conn.row_factory = sqlite3.Row  # Enable row access by name
    return conn

# Initialize the database if it doesn't exist
def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price TEXT, availability TEXT, rating TEXT)')
    conn.close()

# Route to display the form
@app.route('/')
def index():
    return render_template('form.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    price = request.form['price']
    availability = request.form['availability']
    rating = request.form['rating']
    
    try:
        insert_product(name, price, availability, rating)
        flash('Product added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding product: {e}', 'danger')
    
    return redirect(url_for('index'))

# Function to insert data into the database
def insert_product(name, price, availability, rating):
    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, price, availability, rating) VALUES (?, ?, ?, ?)', (name, price, availability, rating))
    conn.commit()
    conn.close()

# Function to update product data
@app.route('/update/<int:product_id>', methods=['POST'])
def update(product_id):
    name = request.form['name']
    price = request.form['price']
    availability = request.form['availability']
    rating = request.form['rating']
    
    try:
        conn = get_db_connection()
        conn.execute('UPDATE products SET name = ?, price = ?, availability = ?, rating = ? WHERE id = ?', (name, price, availability, rating, product_id))
        conn.commit()
        conn.close()
        flash('Product updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating product: {e}', 'danger')
    
    return redirect(url_for('view_products'))

# Function to query products
@app.route('/products')
def view_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('products.html', products=products)

# Route to edit product data
@app.route('/edit/<int:product_id>')
def edit(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    return render_template('edit.html', product=product)

# Route to trigger scraping and store data in the database
@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = scrape_ecommerce_site()  # Call the scraper function
        for product in data:
            insert_product(product['name'], product['price'], product['availability'], product['rating'])
        flash('Data scraped and saved successfully!', 'success')
    except Exception as e:
        flash(f'Error during scraping: {e}', 'danger')
    
    return redirect(url_for('view_products'))

# Route to generate summary CSV report
@app.route('/generate_summary_csv')
def generate_summary_csv():
    conn = get_db_connection()
    products = conn.execute('SELECT price FROM products').fetchall()
    conn.close()

    # Calculate total products and average price
    total_products = len(products)
    total_price = sum([float(product['price'].replace('$', '').replace(',', '')) for product in products])
    avg_price = total_price / total_products if total_products > 0 else 0

    # Define the path to save the CSV file
    csv_file_path = os.path.join(os.getcwd(), 'product_summary_report.csv')

    # Write the summary report to a CSV file
    with open(csv_file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write the headers
        writer.writerow(['Total Products', 'Average Price'])
        
        # Write the summary data
        writer.writerow([total_products, f'${avg_price:.2f}'])

    # Provide the file for download
    return send_file(csv_file_path, as_attachment=True, download_name='product_summary_report.csv')

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)

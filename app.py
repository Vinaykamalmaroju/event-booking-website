# ==========================================================
# EVENT BOOKING WEBSITE
# PART 1
# Imports + Flask Configuration + Database Initialization
# ==========================================================

import os
import sqlite3
import smtplib
import csv
import razorpay

from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify,
    Response,
    flash
)

from werkzeug.utils import secure_filename

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph
)

from reportlab.lib.styles import getSampleStyleSheet

# ==========================================================
# FLASK APP
# ==========================================================

app = Flask(__name__)

app.secret_key = "eventbooking123"

# ==========================================================
# UPLOAD FOLDER
# ==========================================================

import os

UPLOAD_FOLDER = os.path.join("static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ==========================================================
# DATABASE
# ==========================================================

DATABASE = "bookings.db"

# ==========================================================
# RAZORPAY
# ==========================================================

RAZORPAY_KEY_ID = "rzp_test_T6GkiSbrfeQVxj"

RAZORPAY_KEY_SECRET = "pnbW3AkKwss1PG3ofxCLqvci"

client = razorpay.Client(
    auth=(
        RAZORPAY_KEY_ID,
        RAZORPAY_KEY_SECRET
    )
)

# ==========================================================
# DEBUG INFORMATION
# ==========================================================

print("=" * 60)
print("EVENT BOOKING WEBSITE")
print("=" * 60)
print("Current Directory : ", os.getcwd())
print("Database Path     : ", os.path.abspath(DATABASE))
print("Upload Folder     : ", os.path.abspath(UPLOAD_FOLDER))
print("=" * 60)

# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn

# ==========================================================
# CREATE TABLES
# ==========================================================

def create_tables():

    conn = get_db()
    cursor = conn.cursor()

    # -------------------------
    # CUSTOMERS
    # -------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        phone TEXT
    )
    """)

    # -------------------------
    # PROVIDERS
    # -------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        phone TEXT,

        service TEXT,

        experience TEXT,

        description TEXT,

        image TEXT,

        basic_package INTEGER DEFAULT 0,

        premium_package INTEGER DEFAULT 0,

        luxury_package INTEGER DEFAULT 0,

        status TEXT DEFAULT 'Pending'
    )
    """)

    # -------------------------
    # BOOKINGS
    # -------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        email TEXT,

        phone TEXT,

        date TEXT,

        service TEXT,

        provider_email TEXT,

        amount REAL DEFAULT 0,

        payment_id TEXT,

        payment_status TEXT DEFAULT 'Pending',

        status TEXT DEFAULT 'Pending'
    )
    """)

    conn.commit()
    conn.close()

    print("✓ Database initialized successfully.")
# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

create_tables()

print("Application initialized successfully.")
print("=" * 60)
# ==========================================================
# PART 2
# HELPER FUNCTIONS
# EMAIL SERVICE
# DATABASE CONNECTION
# FILE UPLOAD HELPERS
# ==========================================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

DATABASE = "bookings.db"


def get_db():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


# ==========================================================
# CREATE UPLOAD FOLDER
# ==========================================================

if not os.path.exists(app.config["UPLOAD_FOLDER"]):

    os.makedirs(app.config["UPLOAD_FOLDER"])


# ==========================================================
# SAVE IMAGE
# ==========================================================

from werkzeug.utils import secure_filename
import os

def save_image(image):

    try:

        # No file uploaded
        if image is None:
            return ""

        if image.filename is None:
            return ""

        if image.filename.strip() == "":
            return ""

        filename = secure_filename(image.filename)

        upload_folder = app.config["UPLOAD_FOLDER"]

        # Create upload folder if it doesn't exist
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filepath = os.path.join(upload_folder, filename)

        image.save(filepath)

        return filename

    except Exception as e:

        print("SAVE IMAGE ERROR:", e)

        return ""
# ==========================================================
# SEND EMAIL
# ==========================================================

def send_email(
    to_email,
    subject,
    body,
    attachment=None
):

    sender_email = os.environ.get(
        "EMAIL",
        "eventbookingproject@gmail.com"
    )

    sender_password = os.environ.get(
        "PASSWORD",
        "YOUR_GMAIL_APP_PASSWORD"
    )

    try:

        message = MIMEMultipart()

        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(
            MIMEText(body, "plain")
        )

        if attachment:

            if os.path.exists(attachment):

                with open(attachment, "rb") as file:

                    part = MIMEApplication(
                        file.read(),
                        Name=os.path.basename(attachment)
                    )

                part["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(attachment)}"'
                )

                message.attach(part)

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            sender_email,
            sender_password
        )

        server.send_message(message)

        server.quit()

        print("Email Sent Successfully")

        return True

    except Exception as error:

        print("Email Error:", error)

        return False


# ==========================================================
# LOGIN REQUIRED HELPERS
# ==========================================================

def customer_logged_in():
    return "customer_id" in session


def provider_logged_in():
    return "provider_id" in session


def admin_logged_in():
    return "admin" in session


# ==========================================================
# CURRENT DATE & TIME
# ==========================================================

def current_datetime():

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )


# ==========================================================
# CURRENT DATE
# ==========================================================

def current_date():

    return datetime.now().strftime(
        "%d-%m-%Y"
    )


# ==========================================================
# CREATE NOTIFICATION
# ==========================================================

def add_notification(customer_id, message):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notifications
        (
            customer_id,
            message,
            status,
            created_at
        )

        VALUES
        (
            ?, ?, ?, ?
        )
    """, (

        customer_id,

        message,

        "Unread",

        current_datetime()

    ))

    conn.commit()

    conn.close()


# ==========================================================
# GET PROVIDER DETAILS
# ==========================================================

def get_provider(provider_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM providers

        WHERE id=?

    """, (provider_id,))

    provider = cursor.fetchone()

    conn.close()

    return provider


# ==========================================================
# GET CUSTOMER DETAILS
# ==========================================================

def get_customer(customer_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM customers

        WHERE id=?

    """, (customer_id,))

    customer = cursor.fetchone()

    conn.close()

    return customer


# ==========================================================
# GET BOOKING DETAILS
# ==========================================================

def get_booking(booking_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM bookings

        WHERE id=?

    """, (booking_id,))

    booking = cursor.fetchone()

    conn.close()

    return booking


print("=" * 60)
print("PART 2 LOADED SUCCESSFULLY")
print("=" * 60)

# ==========================================================
# PART 3
# HOME PAGE
# CONTACT
# REVIEWS
# STATIC PAGES
# ==========================================================

from datetime import datetime


# ==========================================================
# HOME PAGE
# ==========================================================

@app.route("/")
def home():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM providers
        WHERE status='Approved'
        ORDER BY id DESC
        LIMIT 6
    """)

    providers = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM reviews
        ORDER BY id DESC
        LIMIT 5
    """)

    reviews = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        providers=providers,
        reviews=reviews
    )


# ==========================================================
# ABOUT PAGE
# ==========================================================

@app.route("/about")
def about():

    return render_template("about.html")


# ==========================================================
# SERVICES PAGE
# ==========================================================

@app.route("/services")
def services():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM providers
        WHERE status='Approved'
        ORDER BY service
    """)

    providers = cursor.fetchall()

    conn.close()

    return render_template(
        "services.html",
        providers=providers
    )


# ==========================================================
# CONTACT PAGE
# ==========================================================

@app.route("/contact")
def contact():

    return render_template("contact.html")


# ==========================================================
# CONTACT FORM
# ==========================================================

@app.route("/contact-submit", methods=["POST"])
def contact_submit():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    message = request.form["message"]

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contacts
        (
            name,
            email,
            phone,
            message
        )

        VALUES
        (
            ?,?,?,?
        )
    """, (

        name,
        email,
        phone,
        message

    ))

    conn.commit()
    conn.close()

    flash(
        "Your message has been sent successfully.",
        "success"
    )

    return redirect("/contact")


# ==========================================================
# REVIEW PAGE
# ==========================================================

@app.route("/reviews")
def reviews():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM reviews
        ORDER BY id DESC
    """)

    reviews = cursor.fetchall()

    conn.close()

    return render_template(
        "reviews.html",
        reviews=reviews
    )


# ==========================================================
# SUBMIT REVIEW
# ==========================================================

@app.route("/submit-review", methods=["POST"])
def submit_review():

    name = request.form["name"]
    rating = request.form["rating"]
    review = request.form["review"]

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reviews
        (
            name,
            rating,
            review,
            review_date
        )

        VALUES
        (
            ?,?,?,?
        )
    """, (

        name,
        rating,
        review,
        current_date()

    ))

    conn.commit()
    conn.close()

    flash(
        "Thank you for your review!",
        "success"
    )

    return redirect("/reviews")



# ==========================================================
# FAQ PAGE
# ==========================================================

@app.route("/faq")
def faq():

    return render_template("faq.html")


# ==========================================================
# GALLERY PAGE
# ==========================================================

@app.route("/gallery")
def gallery():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM providers
        WHERE image!=''
        ORDER BY id DESC
    """)

    images = cursor.fetchall()

    conn.close()

    return render_template(
        "gallery.html",
        images=images
    )


# ==========================================================
# ERROR HANDLER
# ==========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


print("=" * 60)
print("PART 3 LOADED SUCCESSFULLY")
print("=" * 60)

# ==========================================================
# PART 4
# CUSTOMER MODULE
# REGISTER
# LOGIN
# DASHBOARD
# LOGOUT
# PROFILE
# ==========================================================


# ==========================================================
# CUSTOMER REGISTER
# ==========================================================

@app.route("/customer-register")
def customer_register():

    return render_template("customer_register.html")


@app.route("/customer-submit", methods=["POST"])
def customer_submit():

    name = request.form["name"].strip()
    email = request.form["email"].strip().lower()
    password = request.form["password"]
    phone = request.form["phone"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM customers WHERE email=?",
        (email,)
    )

    if cursor.fetchone():

        conn.close()

        flash(
            "Email already registered.",
            "danger"
        )

        return redirect("/customer-register")

    cursor.execute("""
        INSERT INTO customers
        (
            name,
            email,
            password,
            phone
        )

        VALUES
        (
            ?,?,?,?
        )
    """, (

        name,
        email,
        password,
        phone

    ))

    conn.commit()
    conn.close()

    flash(
        "Registration Successful. Please Login.",
        "success"
    )

    return redirect("/customer-login")


# ==========================================================
# CUSTOMER LOGIN
# ==========================================================

@app.route("/customer-login", methods=["GET", "POST"])
def customer_login():

    if request.method == "GET":

        return render_template(
            "customer_login.html"
        )

    email = request.form["email"].strip().lower()
    password = request.form["password"]

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM customers
        WHERE email=?
        AND password=?
    """, (

        email,
        password

    ))

    customer = cursor.fetchone()

    conn.close()

    if customer:

        session["customer_id"] = customer["id"]
        session["customer_name"] = customer["name"]
        session["customer_email"] = customer["email"]

        flash(
            "Welcome Back!",
            "success"
        )

        return redirect("/customer-dashboard")

    flash(
        "Invalid Email or Password",
        "danger"
    )

    return redirect("/customer-login")


# ==========================================================
# CUSTOMER DASHBOARD
# ==========================================================

@app.route("/customer-dashboard")
def customer_dashboard():

    if not customer_logged_in():

        return redirect("/customer-login")

    customer = get_customer(
        session["customer_id"]
    )

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM bookings
        WHERE email=?
        ORDER BY id DESC
    """, (

        customer["email"],

    ))

    bookings = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE customer_id=?
        ORDER BY id DESC
    """, (

        customer["id"],

    ))

    notifications = cursor.fetchall()

    conn.close()

    return render_template(

        "customer_dashboard.html",

        customer=customer,

        bookings=bookings,

        notifications=notifications

    )


# ==========================================================
# CUSTOMER PROFILE
# ==========================================================

@app.route("/customer-profile")
def customer_profile():

    if not customer_logged_in():

        return redirect("/customer-login")

    customer = get_customer(
        session["customer_id"]
    )

    return render_template(

        "customer_profile.html",

        customer=customer

    )


# ==========================================================
# UPDATE PROFILE
# ==========================================================

@app.route("/customer-update", methods=["POST"])
def customer_update():

    if not customer_logged_in():

        return redirect("/customer-login")

    name = request.form["name"]
    phone = request.form["phone"]
    password = request.form["password"]

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE customers

        SET

            name=?,

            phone=?,

            password=?

        WHERE id=?
    """, (

        name,

        phone,

        password,

        session["customer_id"]

    ))

    conn.commit()
    conn.close()

    session["customer_name"] = name

    flash(
        "Profile Updated Successfully.",
        "success"
    )

    return redirect("/customer-profile")


# ==========================================================
# CUSTOMER LOGOUT
# ==========================================================

@app.route("/customer-logout")
def customer_logout():

    session.pop("customer_id", None)
    session.pop("customer_name", None)
    session.pop("customer_email", None)

    flash(
        "Logged Out Successfully.",
        "info"
    )

    return redirect("/")


print("=" * 60)
print("PART 4 LOADED SUCCESSFULLY")
print("=" * 60)


# ==========================================================
# PART 5
# PROVIDER MODULE
# REGISTER
# LOGIN
# DASHBOARD
# PROFILE
# LOGOUT
# ==========================================================


# ==========================================================
# PROVIDER REGISTER
# ==========================================================

@app.route("/provider-submit", methods=["POST"])
def provider_submit():

    print("========== PROVIDER SUBMIT START ==========")

    try:

        print("Form Data:")
        print(request.form)

        print("Files:")
        print(request.files)

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
        service = request.form.get("service")
        experience = request.form.get("experience")
        description = request.form.get("description")

        basic_package = request.form.get("basic_package")
        premium_package = request.form.get("premium_package")
        luxury_package = request.form.get("luxury_package")

        image = request.files.get("image")

        filename = ""

        if image and image.filename != "":
            filename = save_image(image)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM providers WHERE email=?",
            (email,)
        )

        existing = cursor.fetchone()

        print("Existing Provider:", existing)

        if existing:
            conn.close()
            flash("Email already registered.", "danger")
            return redirect("/provider-register")

        cursor.execute("""
            INSERT INTO providers
            (
                name,
                email,
                password,
                phone,
                service,
                experience,
                description,
                image,
                basic_package,
                premium_package,
                luxury_package,
                status
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            password,
            phone,
            service,
            experience,
            description,
            filename,
            basic_package,
            premium_package,
            luxury_package,
            "Pending"
        ))

        conn.commit()
        conn.close()

        print("Provider inserted successfully.")

        flash(
            "Registration Successful. Waiting for Admin Approval.",
            "success"
        )

        return redirect("/provider-login")

    except Exception as e:

        import traceback

        traceback.print_exc()

        return f"""
        <h1>ERROR</h1>
        <pre>{traceback.format_exc()}</pre>
        """, 500


# ==========================================================
# VIEW ALL APPROVED PROVIDERS
# ==========================================================

@app.route("/providers")
def providers():

    search = request.args.get("search", "").strip()
    service = request.args.get("service", "").strip()

    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM providers
        WHERE status='Approved'
    """

    values = []

    if search:
        query += " AND name LIKE ?"
        values.append(f"%{search}%")

    if service:
        query += " AND service=?"
        values.append(service)

    query += " ORDER BY name ASC"

    cursor.execute(query, values)

    providers = cursor.fetchall()

    conn.close()

    return render_template(
        "providers.html",
        providers=providers,
        search=search,
        service=service
    )





# ==========================================================
# PROVIDER LOGIN
# ==========================================================

@app.route("/provider-login", methods=["GET", "POST"])
def provider_login():

    if request.method == "GET":
        return render_template("provider_login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM providers
        WHERE email = ?
          AND password = ?
          AND status = ?
    """, (email, password, "Approved"))

    provider = cursor.fetchone()

    conn.close()

    if provider:

        print("=" * 50)
        print("PROVIDER LOGIN SUCCESS")
        print("Provider ID:", provider["id"])
        print("Provider Name:", provider["name"])
        print("Provider Email:", provider["email"])
        print("=" * 50)

        session.clear()

        session["provider_id"] = provider["id"]
        session["provider_email"] = provider["email"]
        session["provider_name"] = provider["name"]

        print("SESSION:", dict(session))

        flash(
            "Login Successful.",
            "success"
        )

        return redirect("/provider-dashboard")

    print("=" * 50)
    print("PROVIDER LOGIN FAILED")
    print("Email:", email)
    print("=" * 50)

    flash(
        "Invalid email, password, or your account is still pending approval.",
        "danger"
    )

    return redirect("/provider-login")
# ==========================================================
# PROVIDER DASHBOARD
# ==========================================================

# ==========================================================
# PROVIDER DASHBOARD
# ==========================================================

@app.route("/provider-dashboard")
def provider_dashboard():

    # Check login
    if "provider_id" not in session:
        flash("Please login first.", "danger")
        return redirect("/provider-login")

    provider_id = session["provider_id"]

    # Get provider details
    provider = get_provider(provider_id)

    if provider is None:
        session.clear()
        flash("Provider account not found.", "danger")
        return redirect("/provider-login")

    conn = get_db()
    cursor = conn.cursor()

    # ------------------------------------
    # Total Bookings
    # ------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE provider_email=?
    """, (provider["email"],))

    total_bookings = cursor.fetchone()[0]

    # ------------------------------------
    # Approved Bookings
    # ------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE provider_email=?
        AND status='Approved'
    """, (provider["email"],))

    approved_bookings = cursor.fetchone()[0]

    # ------------------------------------
    # Total Earnings
    # ------------------------------------

    total_earnings = 0

    try:

        cursor.execute("""
            SELECT IFNULL(SUM(amount),0)
            FROM bookings
            WHERE provider_email=?
            AND status='Approved'
        """, (provider["email"],))

        total_earnings = cursor.fetchone()[0] or 0

    except Exception as e:
        print("Total Earnings Error:", e)

    # ------------------------------------
    # Current Month Earnings
    # ------------------------------------

    month_earnings = 0

    try:

        cursor.execute("""
            SELECT IFNULL(SUM(amount),0)
            FROM bookings
            WHERE provider_email=?
            AND status='Approved'
            AND strftime('%Y-%m', booking_date)=strftime('%Y-%m','now')
        """, (provider["email"],))

        month_earnings = cursor.fetchone()[0] or 0

    except Exception as e:
        print("Month Earnings Error:", e)

    conn.close()

    print("=" * 60)
    print("PROVIDER DASHBOARD LOADED")
    print("Provider ID :", provider["id"])
    print("Provider Name :", provider["name"])
    print("Provider Email :", provider["email"])
    print("Session :", dict(session))
    print("=" * 60)

    return render_template(
        "provider_dashboard.html",
        provider=provider,
        total_bookings=total_bookings,
        approved_bookings=approved_bookings,
        total_earnings=total_earnings,
        month_earnings=month_earnings
    )



# ==========================================================
# PROVIDER EDIT PROFILE
# ==========================================================

@app.route("/provider-edit")
def provider_edit():

    # Check if provider is logged in
    if "provider_id" not in session:
        flash("Please login first.", "danger")
        return redirect("/provider-login")

    provider_id = session["provider_id"]

    # Get provider details
    provider = get_provider(provider_id)

    # Provider not found
    if provider is None:

        session.clear()

        flash(
            "Provider account not found. Please login again.",
            "danger"
        )

        return redirect("/provider-login")

    # Open edit profile page
    return render_template(
        "provider_edit.html",
        provider=provider
    )
# ==========================================================
# UPDATE PROVIDER PROFILE
# ==========================================================

@app.route("/provider-update", methods=["POST"])
def provider_update():

    if not provider_logged_in():
        return redirect("/provider-login")

    provider_id = session.get("provider_id")

    if not provider_id:
        flash("Session expired. Please login again.", "danger")
        return redirect("/provider-login")

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    service = request.form.get("service", "")
    experience = request.form.get("experience", "")
    description = request.form.get("description", "")

    image = request.files.get("image")

    conn = get_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "SELECT id FROM providers WHERE id=?",
            (provider_id,)
        )

        if cursor.fetchone() is None:
            conn.close()
            flash("Provider not found.", "danger")
            return redirect("/provider-login")

        if image and image.filename != "":

            filename = save_image(image)

            cursor.execute("""
                UPDATE providers
                SET
                    name=?,
                    phone=?,
                    service=?,
                    experience=?,
                    description=?,
                    image=?
                WHERE id=?
            """, (
                name,
                phone,
                service,
                experience,
                description,
                filename,
                provider_id
            ))

        else:

            cursor.execute("""
                UPDATE providers
                SET
                    name=?,
                    phone=?,
                    service=?,
                    experience=?,
                    description=?
                WHERE id=?
            """, (
                name,
                phone,
                service,
                experience,
                description,
                provider_id
            ))

        conn.commit()

        session["provider_name"] = name

        flash(
            "Profile Updated Successfully.",
            "success"
        )

    except Exception as e:

        conn.rollback()
        print("Provider Update Error:", e)

        flash(
            "Unable to update profile.",
            "danger"
        )

    finally:

        conn.close()

    return redirect("/provider-dashboard")


# ==========================================================
# PROVIDER LOGOUT
# ==========================================================

@app.route("/provider-logout")
def provider_logout():

    session.pop("provider_id", None)
    session.pop("provider_email", None)
    session.pop("provider_name", None)

    flash(
        "Logged Out Successfully.",
        "success"
    )

    return redirect("/")


print("=" * 60)
print("PART 5 LOADED SUCCESSFULLY")
print("=" * 60)
# ==========================================================
# PART 6
# BOOKING MODULE
# ==========================================================

# ==========================================================
# BOOKING PAGE
# ==========================================================

@app.route("/booking")
def booking():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM providers
        WHERE status='Approved'
        ORDER BY service,name
    """)

    providers = cursor.fetchall()

    conn.close()

    return render_template(
        "booking.html",
        providers=providers
    )


# ==========================================================
# PROVIDER DETAILS
# ==========================================================

@app.route("/provider/<int:provider_id>")
def provider_profile(provider_id):

    provider = get_provider(provider_id)

    if provider is None:
        return "Provider Not Found"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM reviews
        WHERE provider_email=?
        ORDER BY id DESC
    """, (provider["email"],))

    reviews = cursor.fetchall()

    conn.close()

    return render_template(
        "provider_details.html",
        provider=provider,
        reviews=reviews
    )


# ==========================================================
# AVAILABLE DATES
# ==========================================================

@app.route("/available-dates")
def available_dates():

    provider_email = request.args.get("provider_email")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT available_date
        FROM provider_availability
        WHERE
            provider_email=?
        AND
            status='Available'
        ORDER BY available_date
    """, (provider_email,))

    rows = cursor.fetchall()

    conn.close()

    dates = []

    for row in rows:
        dates.append(row["available_date"])

    return jsonify(dates)


# ==========================================================
# SUBMIT BOOKING
# ==========================================================

@app.route("/submit-booking", methods=["POST"])
def submit_booking():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    date = request.form["date"]
    service = request.form["service"]
    provider_email = request.form["provider_email"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE
            provider_email=?
        AND
            date=?
        AND
            status!='Cancelled'
    """, (

        provider_email,
        date

    ))

    booked = cursor.fetchone()[0]

    if booked > 0:

        conn.close()

        flash(
            "Provider is already booked on this date.",
            "danger"
        )

        return redirect("/booking")

    cursor.execute("""
        INSERT INTO bookings
        (
            name,
            email,
            phone,
            date,
            service,
            provider_email,
            status
        )

        VALUES
        (
            ?,?,?,?,?,?,?
        )
    """, (

        name,
        email,
        phone,
        date,
        service,
        provider_email,
        "Pending"

    ))

    conn.commit()

    conn.close()

    flash(
        "Booking Submitted Successfully.",
        "success"
    )

    return redirect("/booking-history")


# ==========================================================
# BOOKING HISTORY
# ==========================================================

@app.route("/booking-history")
def booking_history():

    if not customer_logged_in():

        return redirect("/customer-login")

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM bookings
        WHERE email=?
        ORDER BY id DESC
    """, (

        session["customer_email"],

    ))

    bookings = cursor.fetchall()

    conn.close()

    return render_template(
        "booking_history.html",
        bookings=bookings
    )


# ==========================================================
# TRACK BOOKING PAGE
# ==========================================================

@app.route("/track-booking")
def track_booking():

    return render_template(
        "track_booking.html"
    )


# ==========================================================
# TRACK BOOKING
# ==========================================================

@app.route("/track", methods=["POST"])
def track():

    email = request.form["email"]

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM bookings
        WHERE email=?
        ORDER BY id DESC
    """, (

        email,

    ))

    bookings = cursor.fetchall()

    conn.close()

    return render_template(
        "booking_result.html",
        bookings=bookings
    )


# ==========================================================
# BOOKED DATES API
# ==========================================================

@app.route("/booked-dates")
def booked_dates():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT date
        FROM bookings
        WHERE status='Approved'
    """)

    rows = cursor.fetchall()

    conn.close()

    booked = []

    for row in rows:

        booked.append(
            row["date"]
        )

    return jsonify(booked)


print("=" * 60)
print("PART 6 LOADED SUCCESSFULLY")
print("=" * 60)

# ==========================================================
# PART 7
# ADMIN MODULE
# ==========================================================


# ==========================================================
# ADMIN LOGIN
# ==========================================================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "GET":
        return render_template("admin_login.html")

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":

        session["admin"] = True

        flash(
            "Welcome Admin",
            "success"
        )

        return redirect("/admin-dashboard")

    flash(
        "Invalid Username or Password",
        "danger"
    )

    return redirect("/admin-login")


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin-login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) total FROM customers")
    total_customers = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) total FROM providers")
    total_providers = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) total FROM bookings")
    total_bookings = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM bookings
        WHERE status='Approved'
    """)
    approved_bookings = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM bookings
        WHERE status='Pending'
    """)
    pending_bookings = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT *
        FROM bookings
        ORDER BY id DESC
    """)
    bookings = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM providers
        ORDER BY id DESC
    """)
    providers = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_customers=total_customers,
        total_providers=total_providers,
        total_bookings=total_bookings,
        approved_bookings=approved_bookings,
        pending_bookings=pending_bookings,
        bookings=bookings,
        providers=providers
    )


# ==========================================================
# APPROVE PROVIDER
# ==========================================================

@app.route("/approve-provider/<int:id>")
def approve_provider(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE providers
        SET status='Approved'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    flash(
        "Provider Approved Successfully.",
        "success"
    )

    return redirect("/admin-dashboard")


# ==========================================================
# DELETE PROVIDER
# ==========================================================

@app.route("/delete-provider/<int:id>")
def delete_provider(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM providers WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Provider Deleted.",
        "info"
    )

    return redirect("/admin-dashboard")


# ==========================================================
# APPROVE BOOKING
# ==========================================================

@app.route("/approve-booking/<int:id>")
def approve_booking(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings
        SET status='Approved'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    flash(
        "Booking Approved.",
        "success"
    )

    return redirect("/admin-dashboard")


# ==========================================================
# CANCEL BOOKING
# ==========================================================

@app.route("/cancel-booking/<int:id>")
def cancel_booking(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings
        SET status='Cancelled'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    flash(
        "Booking Cancelled.",
        "warning"
    )

    return redirect("/admin-dashboard")


# ==========================================================
# DELETE BOOKING
# ==========================================================

@app.route("/delete-booking/<int:id>")
def delete_booking(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM bookings WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Booking Deleted.",
        "danger"
    )

    return redirect("/admin-dashboard")


# ==========================================================
# ADMIN LOGOUT
# ==========================================================

@app.route("/admin-logout")
def admin_logout():

    session.pop("admin", None)

    flash(
        "Logged Out Successfully.",
        "info"
    )

    return redirect("/")


print("=" * 60)
print("PART 7 LOADED SUCCESSFULLY")
print("=" * 60)

# ==========================================================
# PART 8
# AI FEATURES + SUPPORT + FINAL
# ==========================================================

from datetime import datetime


# ==========================================================
# AI EVENT PLANNER
# ==========================================================

@app.route("/event-planner", methods=["GET", "POST"])
def event_planner():

    suggestion = None

    if request.method == "POST":

        event = request.form["event"]
        guests = int(request.form["guests"])
        budget = int(request.form["budget"])

        if event == "Wedding":

            services = [
                "Premium Decoration",
                "Photography",
                "Videography",
                "Luxury Catering",
                "Live Music"
            ]

            venue = "Luxury Wedding Hall"

        elif event == "Birthday":

            services = [
                "Balloon Decoration",
                "Birthday Cake",
                "DJ",
                "Photography"
            ]

            venue = "Party Hall"

        elif event == "Corporate":

            services = [
                "Conference Hall",
                "Projector",
                "Sound System",
                "Corporate Catering"
            ]

            venue = "Business Convention Center"

        else:

            services = [
                "Decoration",
                "Photography",
                "Food"
            ]

            venue = "Community Hall"

        estimated_cost = guests * 1200

        if budget >= estimated_cost:
            package = "Premium Package"
        else:
            package = "Budget Package"

        suggestion = {

            "event": event,
            "guests": guests,
            "budget": budget,
            "venue": venue,
            "services": services,
            "estimated_cost": estimated_cost,
            "package": package,
            "planning_days": max(7, guests // 10)

        }

    return render_template(
        "event_planner.html",
        suggestion=suggestion
    )


# ==========================================================
# AI BUDGET ESTIMATOR
# ==========================================================

@app.route("/budget-estimator", methods=["GET", "POST"])
def budget_estimator():

    result = None

    if request.method == "POST":

        event = request.form["event"]
        guests = int(request.form["guests"])
        budget = int(request.form["budget"])

        decoration = guests * 150
        catering = guests * 500
        photography = 25000
        entertainment = 15000
        venue = 50000

        if event == "Wedding":
            venue = 100000

        elif event == "Birthday":
            venue = 30000

        elif event == "Corporate":
            venue = 70000

        total = (
            decoration +
            catering +
            photography +
            entertainment +
            venue
        )

        if total <= budget:
            status = "Budget is sufficient"
        else:
            status = "Budget is insufficient"

        result = {

            "event": event,
            "guests": guests,
            "budget": budget,
            "decoration": decoration,
            "catering": catering,
            "photography": photography,
            "entertainment": entertainment,
            "venue": venue,
            "total": total,
            "status": status

        }

    return render_template(
        "budget_estimator.html",
        result=result
    )


# ==========================================================
# AI CHATBOT PAGE
# ==========================================================

@app.route("/chat")
def chat():

    return render_template("chatbot.html")


# ==========================================================
# CHATBOT API
# ==========================================================

@app.route("/chatbot", methods=["POST"])
def chatbot():

    data = request.get_json()

    message = data.get(
        "message",
        ""
    ).lower()

    if "hello" in message:

        reply = "Hello! Welcome to Event Booking."

    elif "booking" in message:

        reply = "Click Booking to reserve your event."

    elif "payment" in message:

        reply = "Payments are processed securely."

    elif "support" in message:

        reply = "Visit the Support page for assistance."

    elif "services" in message:

        reply = (
            "Wedding, Birthday, Catering, "
            "Photography, Decoration and Corporate Events."
        )

    else:

        reply = (
            "Sorry, I couldn't understand."
        )

    return jsonify({
        "reply": reply
    })


# ==========================================================
# CUSTOMER SUPPORT
# ==========================================================

@app.route("/support", methods=["GET", "POST"])
def support():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO support_messages

            (
                customer_name,
                customer_email,
                sender,
                message,
                created_at,
                status
            )

            VALUES
            (
                ?,?,?,?,?,?
            )

        """, (

            name,
            email,
            "Customer",
            message,
            current_datetime(),
            "Open"

        ))

        conn.commit()
        conn.close()

        flash(
            "Support request submitted.",
            "success"
        )

        return redirect("/")

    return render_template(
        "support.html"
    )

# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "running",

        "application": "Event Booking Website",

        "version": "2.0"

    })


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )

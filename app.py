import email
from fileinput import filename
import razorpay
from flask import Flask, jsonify, render_template, request, redirect, session, Response,flash
import sqlite3
import os
import csv
import smtplib
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
print("=" * 60)
print("Current Working Directory:")
print(os.getcwd())

print("Database Path:")
print(os.path.abspath("bookings.db"))
print("=" * 60)

app = Flask(__name__)
RAZORPAY_KEY_ID = "rzp_test_T6GkiSbrfeQVxj"

RAZORPAY_KEY_SECRET = "pnbW3AkKwss1PG3ofxCLqvci"

client = razorpay.Client(
    auth=(
        RAZORPAY_KEY_ID,
        RAZORPAY_KEY_SECRET
    )
)
app.secret_key = "eventbooking123"
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")

print("=" * 50)
print("Current Working Directory:", os.getcwd())
print("Database Location:", os.path.abspath("bookings.db"))
print("=" * 50)


# ======================================================
# EMAIL FUNCTION
# ======================================================

def send_email(to_email, subject, body, attachment=None):

    sender_email = os.environ.get(
        "EMAIL",
        "eventbookingproject@gmail.com"
    )

    app_password = os.environ.get(
        "PASSWORD",
        "fcli uryq nyme kooo"
    )

    try:

        msg = MIMEMultipart()

        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        msg.attach(MIMEText(body, "plain"))

        if attachment:

            if os.path.exists(attachment):

                with open(attachment, "rb") as file:

                    part = MIMEApplication(file.read())

                    part.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=os.path.basename(attachment)
                    )

                    msg.attach(part)

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=20
        )

        server.ehlo()

        server.starttls()

        server.ehlo()

        server.login(
            sender_email,
            app_password
        )

        server.send_message(msg)

        server.quit()

        print("✅ Email sent successfully.")

        return True

    except Exception as e:

        print("❌ Email Error:", str(e))

        return False
# ======================================================
# CREATE DATABASE TABLES
# ======================================================

def create_table():

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    # -----------------------------
    # BOOKINGS
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        date TEXT,
        service TEXT,
        provider_email TEXT,
        status TEXT DEFAULT 'Pending',
        experience TEXT,
        description TEXT,
        image TEXT,
        payment_id TEXT,
        payment_status TEXT
    )
    """)

    # -----------------------------
    # CONTACTS
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        message TEXT
    )
    """)

    # -----------------------------
    # PROVIDERS
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        phone TEXT,
        service TEXT,
        experience TEXT,
        description TEXT,
        image TEXT,
        status TEXT DEFAULT 'Pending'
    )
    """)

    # -----------------------------
    # REVIEWS
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        rating INTEGER,
        review TEXT,
        review_date TEXT
    )
    """)

    # -----------------------------
    # PROVIDER AVAILABILITY
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS provider_availability(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider_email TEXT,
        available_date TEXT,
        status TEXT
    )
    """)

    # -----------------------------
    # PROVIDER PORTFOLIO
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS provider_portfolio(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider_id INTEGER,
        file_name TEXT,
        file_type TEXT
    )
    """)

    # -----------------------------
    # CUSTOMERS
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        phone TEXT
    )
    """)

    # -----------------------------
    # WISHLIST
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        provider_id INTEGER
    )
    """)

    # -----------------------------
    # NOTIFICATIONS
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        message TEXT,
        notification_type TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    # -----------------------------
    # SUPPORT MESSAGES
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS support_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        customer_email TEXT,
        sender TEXT,
        message TEXT,
        created_at TEXT,
        status TEXT DEFAULT 'Open'
    )
    """)

    conn.commit()
    conn.close()


create_table()

print("Database tables created successfully")
# ======================================================
# HOME PAGE
# ======================================================

@app.route("/")
def home():

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    # Featured Providers
    cursor.execute("""
        SELECT *
        FROM providers
        WHERE status='Approved'
        LIMIT 3
    """)
    providers = cursor.fetchall()

    # Latest Customer Reviews
    cursor.execute("""
        SELECT name, rating, review
        FROM reviews
        ORDER BY id DESC
        LIMIT 3
    """)
    reviews = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        providers=providers,
        reviews=reviews
    )
@app.route("/provider-availability")
def provider_availability():

    if "provider" not in session:
        return redirect("/provider-login")

    provider_email = session["provider"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT available_date, status
        FROM provider_availability
        WHERE provider_email=?
        ORDER BY available_date
    """, (provider_email,))

    availability = cursor.fetchall()

    conn.close()

    return render_template(
        "provider_availability.html",
        availability=availability
    )

@app.route("/save-availability", methods=["POST"])
def save_availability():

    if "provider" not in session:
        return redirect("/provider-login")

    date = request.form["date"]
    status = request.form["status"]

    provider_email = session["provider"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO provider_availability(
        provider_email,
        available_date,
        status
    )
    VALUES(?,?,?)
    """, (
        provider_email,
        date,
        status
    ))

    conn.commit()
    conn.close()

    return redirect("/provider-availability")


# ======================================================
# BOOKING PAGE
# ======================================================

@app.route("/booking")
def booking():

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM providers
        WHERE status='Approved'
    """)

    providers = cursor.fetchall()

    conn.close()

    return render_template(
        "booking.html",
        providers=providers
    )

@app.route("/submit", methods=["POST"])
def submit():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    date = request.form["date"]
    service = request.form["service"]
    provider_email = request.form["provider_email"]
    amount = request.form["amount"]
    coupon = request.form.get("coupon", "").strip().upper()

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    # Check if the selected provider already has a booking on this date
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE provider_email=? AND date=?
    """, (provider_email, date))

    provider_bookings = cursor.fetchone()[0]

    if provider_bookings > 0:
        conn.close()
        return """
        <h2 style='text-align:center;color:red;margin-top:80px;'>
            Provider is already booked on this date.
            <br><br>
            Please select another provider or another date.
        </h2>
        """

    # Check maximum bookings allowed for the date
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE date=?
    """, (date,))

    booking_count = cursor.fetchone()[0]

    if booking_count >= 5:
        conn.close()
        return """
        <h2 style='text-align:center;color:red;margin-top:80px;'>
            Sorry!
            <br><br>
            This date is fully booked.
            <br><br>
            Please choose another date.
        </h2>
        """

    # Save booking
    cursor.execute("""
        INSERT INTO bookings(
            name,
            email,
            phone,
            date,
            service,
            provider_email,
            status
        )
        VALUES(?,?,?,?,?,?,?)
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

    booking = {
        "name": name,
        "email": email,
        "phone": phone,
        "date": date,
        "service": service,
        "provider_email": provider_email
    }

    session["booking"] = booking

    # Send email to provider
    if provider_email:

        provider_subject = "New Booking Assigned"

        provider_body = f"""
Hello,

A new booking has been assigned.

Customer Name : {name}
Customer Email : {email}
Phone : {phone}

Service : {service}
Date : {date}
"""

        send_email(
            provider_email,
            provider_subject,
            provider_body
        )

    return redirect("/payment-success")


def contact():
    return render_template("contact.html")
@app.route("/review")
def review():

    return render_template("review.html")
from datetime import datetime

# ==========================================
# AI CHATBOT PAGE
# ==========================================

@app.route("/chat")
def chat():

    return render_template("chatbot.html")


# ==========================================
# AI CHATBOT API
# ==========================================

@app.route("/chatbot", methods=["POST"])
def chatbot():

    data = request.get_json()

    print("Received JSON:", data)

    message = ""

    if data:
        message = data.get("message", "")

    print("Message:", message)

    message = message.strip().lower()

    if message == "":
        return jsonify({
            "reply": "Please type a question."
        })

    if "hello" in message or "hi" in message:
        reply = "Hello! Welcome to Event Booking Website."

    elif "book" in message:
        reply = "To book an event, click Booking and choose your provider."

    elif "service" in message:
        reply = "We provide Wedding, Birthday, Photography, Catering and Decoration."

    elif "payment" in message:
        reply = "Payment is securely processed."


# -------------------------
# Human Support
# -------------------------

    elif (
    "support" in message
    or "customer care" in message
    or "human" in message
    or "agent" in message
    or "executive" in message
    or "representative" in message
    or "talk to support" in message
    or "live chat" in message
):

     return jsonify({

        "reply": "Sure! Connecting you to our Human Support Team...",

        "redirect": "/customer-support"

    })


    else:
     reply = "Sorry, I couldn't understand your question."

    return jsonify({
        "reply": reply
    })

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/payment")
def payment():
    return render_template("payment.html")


@app.route("/payment-success")
def payment_success():
    return render_template("payment_success.html")


# ======================================================
# PROVIDER REGISTRATION PAGE
# ======================================================

@app.route("/provider-login", methods=["GET", "POST"])
def provider_login():

    if request.method == "GET":
        return render_template("provider_login.html")

    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM providers
        WHERE email=? AND password=?
    """, (
        email,
        password
    ))

    provider = cursor.fetchone()

    

    conn.close()

    if provider is None:

        return "<h2>Invalid Email or Password</h2>"

    if provider[9] != "Approved":

        return "<h2>Your account is waiting for Admin Approval.</h2>"

    session["provider"] = provider[0]

    return redirect("/provider-dashboard")

@app.route("/provider-register")
def provider_register():
    return render_template("provider_register.html")

@app.route("/provider-submit", methods=["POST"])
def provider_submit():

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    phone = request.form["phone"]
    service = request.form["service"]
    experience = request.form["experience"]
    description = request.form["description"]

    basic_package = request.form["basic_package"]
    premium_package = request.form["premium_package"]
    luxury_package = request.form["luxury_package"]

    image = request.files["image"]

    filename = ""

    if image and image.filename != "":
        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO providers(
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
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
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

    subject = "Provider Registration Successful"

    body = f"""
Hello {name},

Thank you for registering as a service provider.

Your registration has been received successfully.

Package Prices

Basic Package : ₹{basic_package}

Premium Package : ₹{premium_package}

Luxury Package : ₹{luxury_package}

Current Status:
Pending Approval

The admin will review your profile soon.

Thank you for joining Event Booking Website.
"""

    email_sent = send_email(email, subject, body)

    if not email_sent:
        print("Email could not be sent.")

    return render_template("provider_success.html")

@app.route("/save-provider/<int:id>")
def save_provider(id):

    if "customer_email" not in session:
        flash("Please login first.")
        return redirect("/customer-login")

    customer_email = session["customer_email"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM wishlist
        WHERE customer_email=?
        AND provider_id=?
    """, (customer_email, id))

    already_saved = cursor.fetchone()

    if already_saved:
        flash("Provider already saved.")

    else:
        cursor.execute("""
            INSERT INTO wishlist
            (customer_email, provider_id, saved_date)
            VALUES(?,?,?)
        """, (
            customer_email,
            id,
            datetime.now().strftime("%d-%m-%Y")
        ))

        conn.commit()

        flash("Provider saved successfully.")

    conn.close()

    return redirect(f"/provider/{id}")

@app.route("/remove-wishlist/<int:id>")
def remove_wishlist(id):

    conn=sqlite3.connect("bookings.db")

    cursor=conn.cursor()

    cursor.execute("""

    DELETE FROM wishlist

    WHERE provider_id=?

    AND customer_email=?

    """,(id,session["customer_email"]))

    conn.commit()

    conn.close()

    flash("Removed successfully.")

    return redirect("/wishlist")

@app.route("/contact-submit", methods=["POST"])
def contact_submit():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    message = request.form["message"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contacts(
            name,
            email,
            phone,
            message
        )
        VALUES(?,?,?,?)
    """, (
        name,
        email,
        phone,
        message
    ))

    conn.commit()
    conn.close()

    return "<h1>Message Sent Successfully</h1>"
   
   
   

@app.route("/messages")
def messages():

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM contacts")
    messages = cursor.fetchall()

    conn.close()

    return render_template(
        "messages.html",
        messages=messages
    )
@app.route("/providers")
def providers():

    search = request.args.get("search", "")
    service = request.args.get("service", "")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM providers
        WHERE status='Approved'
    """

    values = []

    if search:
        query += " AND name LIKE ?"
        values.append("%" + search + "%")

    if service:
        query += " AND service=?"
        values.append(service)

    cursor.execute(query, values)

    providers = cursor.fetchall()

    print("--------------------------------")
    for p in providers:
        print(p)
    print("--------------------------------")

    conn.close()

    return render_template(
        "providers.html",
        providers=providers,
        search=search,
        service=service
    )
@app.route("/admin-providers")
def admin_providers():

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM providers")

    providers = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_providers.html",
        providers=providers
    )

@app.route("/approve-provider/<int:id>")
def approve_provider(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE providers SET status='Approved' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin-providers")
@app.route("/booking-details/<int:id>")
def booking_details(id):

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM bookings WHERE id=?",
        (id,)
    )

    booking = cursor.fetchone()

    conn.close()

    return render_template(
        "booking_details.html",
        booking=booking
    )


@app.route("/admin-support")
def admin_support():

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            customer_name,
            customer_email,
            status,
            MAX(created_at) AS last_message
        FROM support_messages
        GROUP BY customer_email
        ORDER BY last_message DESC
    """)

    customers = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_support.html",
        customers=customers
    )


@app.route("/admin-support-chat/<email>", methods=["GET", "POST"])
def admin_support_chat(email):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # -----------------------------
    # Save Admin Reply
    # -----------------------------

    if request.method == "POST":

        reply = request.form["reply"]

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

            VALUES(?,?,?,?,?,?)

        """, (

            "",

            email,

            "Admin",

            reply,

            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),

            "Open"

        ))

        conn.commit()

    # -----------------------------
    # Fetch All Messages
    # -----------------------------

    cursor.execute("""

        SELECT *

        FROM support_messages

        WHERE customer_email=?

        ORDER BY id

    """, (email,))

    chats = cursor.fetchall()

    conn.close()

    return render_template(

        "admin_support_chat.html",

        chats=chats,

        email=email

    )

# ----------------------------
# PROVIDER PROFILE
# ----------------------------
@app.route("/provider/<int:id>")
def provider_profile(id):

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get provider details
    cursor.execute(
        "SELECT * FROM providers WHERE id=?",
        (id,)
    )
    provider = cursor.fetchone()
    print(provider)

    if not provider:
        conn.close()
        return "Provider not found"

    # Get provider portfolio
    cursor.execute("""
        SELECT * FROM provider_portfolio
        WHERE provider_id=?
    """, (id,))

    portfolio = cursor.fetchone()

    images = []

    if portfolio and portfolio["images"]:
        images = portfolio["images"].split(",")

    # Get provider reviews

    conn.close()

    return render_template(
        "provider_details.html",
        provider=provider,
        images=images,
        reviews=reviews
    )


@app.route("/admin-login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin-login", methods=["POST"])
def admin_login_post():

    username = request.form["username"]
    password = request.form["password"]

    # Change these credentials if needed
    if username == "admin" and password == "admin123":
        session["admin"] = True
        return redirect("/admin")

    flash("Invalid username or password")
    return redirect("/admin-login")


# ----------------------------
# Admin Dashboard
# ----------------------------
@app.route("/admin")
@app.route("/admin-dashboard")
def admin():

    if "admin" not in session:
        return redirect("/admin-login")

    search = request.args.get("search", "")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    # -----------------------------
    # Search Bookings
    # -----------------------------
    if search:
        cursor.execute(
            "SELECT * FROM bookings WHERE name LIKE ?",
            ('%' + search + '%',)
        )
    else:
        cursor.execute("SELECT * FROM bookings")

    bookings = cursor.fetchall()

    # -----------------------------
    # Booking Counts
    # -----------------------------
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE status='Approved'"
    )
    approved = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE status='Pending'"
    )
    pending = cursor.fetchone()[0]

    # -----------------------------
    # Provider Counts
    # -----------------------------
    cursor.execute("SELECT COUNT(*) FROM providers")
    total_providers = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM providers WHERE status='Approved'"
    )
    approved_providers = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM providers WHERE status='Pending'"
    )
    pending_providers = cursor.fetchone()[0]

    # -----------------------------
    # Contact Messages
    # -----------------------------
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total_messages = cursor.fetchone()[0]

    # -----------------------------
    # Open Support Requests
    # -----------------------------
    cursor.execute("""
        SELECT COUNT(*)
        FROM support_messages
        WHERE status='Open'
    """)

    open_support_requests = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        bookings=bookings,
        total=total,
        approved=approved,
        pending=pending,
        total_providers=total_providers,
        approved_providers=approved_providers,
        pending_providers=pending_providers,
        total_messages=total_messages,
        open_support_requests=open_support_requests,
        search=search
    )
@app.route("/admin-analytics")
def admin_analytics():

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Monthly Bookings
    cursor.execute("""
        SELECT substr(date,4,2) AS month,
               COUNT(*) AS total
        FROM bookings
        GROUP BY month
        ORDER BY month
    """)
    monthly_bookings = cursor.fetchall()
    print(monthly_bookings)

    # Monthly Revenue
    cursor.execute("""
        SELECT substr(date,4,2) AS month,
               COUNT(*) * 500 AS revenue
        FROM bookings
        WHERE payment_status='Paid'
        GROUP BY month
        ORDER BY month
    """)
    monthly_revenue = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_analytics.html",
        monthly_bookings=monthly_bookings,
        monthly_revenue=monthly_revenue
    )

# ----------------------------
# Edit Booking Page
# ----------------------------
@app.route("/edit/<int:id>")
def edit(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM bookings WHERE id=?",
        (id,)
    )

    booking = cursor.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        booking=booking
    )


# ----------------------------
# Update Booking
# ----------------------------
@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    if "admin" not in session:
        return redirect("/admin-login")

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    date = request.form["date"]
    service = request.form["service"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings
        SET
            name=?,
            email=?,
            phone=?,
            date=?,
            service=?
        WHERE id=?
    """, (
        name,
        email,
        phone,
        date,
        service,
        id
    ))

    conn.commit()
    conn.close()

    return redirect("/admin")



# ----------------------------
# Delete Booking
# ----------------------------
@app.route("/delete/<int:id>")
def delete(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM bookings WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")

# ----------------------------
# Export Bookings CSV
# ----------------------------
@app.route("/export")
def export():

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()

    conn.close()

    def generate():

        data = []

        header = [
            "ID",
            "Name",
            "Email",
            "Phone",
            "Date",
            "Service",
            "Status"
        ]

        data.append(",".join(header))

        for row in bookings:
            data.append(",".join(str(item) for item in row))

        return "\n".join(data)

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=bookings.csv"
        }
    )
# ----------------------------
# Approve Booking
# ----------------------------
@app.route("/approve/<int:id>")
def approve(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    # Get booking details
    cursor.execute(
        "SELECT name, email, service, date FROM bookings WHERE id=?",
        (id,)
    )

    booking = cursor.fetchone()

    if booking:

        name = booking[0]
        email = booking[1]
        service = booking[2]
        date = booking[3]

        # Update booking status
        cursor.execute(
            "UPDATE bookings SET status='Approved' WHERE id=?",
            (id,)
        )

        conn.commit()

        subject = "Booking Approved"

        body = f"""
Hello {name},

Congratulations!

Your booking has been approved.

Service: {service}

Date: {date}

Thank you for choosing Event Booking Website.
"""

        send_email(
            email,
            subject,
            body
        )

    conn.close()

    return redirect("/admin")
    # -----------------------------
    # Generate Invoice PDF
    # -----------------------------
    pdf_path = os.path.join("static", "invoice.pdf")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path)
    story = []
    story.append( Paragraph("<b>EVENT BOOKING WEBSITE</b>", styles["Title"]) )
    story.append( Paragraph(f"Customer : {booking['name']}", styles["Normal"]) )
    story.append( Paragraph(f"Email : {booking['email']}", styles["Normal"]) )
    story.append( Paragraph(f"Phone : {booking['phone']}", styles["Normal"]) )
    story.append( Paragraph(f"Service : {booking['service']}", styles["Normal"]) )
    story.append( Paragraph(f"Date : {booking['date']}", styles["Normal"]) )
    story.append( Paragraph(f"Payment ID : {payment_id}", styles["Normal"]) )
    story.append( Paragraph("Amount Paid : ₹500", styles["Normal"]) )
    story.append( Paragraph("Payment Status : Paid", styles["Normal"]) )
    doc.build(story)
    # -----------------------------
    # Send Email with Invoice
    # -----------------------------
    subject = "Booking Confirmation"
    body = f""" Hello {booking['name']}, Your payment was successful. Your booking has been received successfully. Service : {booking['service']} Date : {booking['date']} Payment ID : {payment_id} Thank you for choosing Event Booking Website. """
    send_email( booking["email"], subject, body, pdf_path )
    session.pop("booking", None)
    return redirect("/static/invoice.pdf")

@app.route("/notifications")
def notifications():

    if "customer" not in session:
        return redirect("/customer-login")

    customer_id = session["customer"]

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE customer_id=?
        ORDER BY id DESC
    """, (customer_id,))

    notifications = cursor.fetchall()

    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications
    )




# ----------------------------
# Run Application
# ----------------------------
@app.route("/booking-history", methods=["GET", "POST"])
def booking_history():

    bookings = []

    if request.method == "POST":

        email = request.form["email"]

        conn = sqlite3.connect("bookings.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM bookings WHERE email=?",
            (email,)
        )

        bookings = cursor.fetchall()

        conn.close()

    return render_template(
        "booking_history.html",
        bookings=bookings
    )

@app.route("/submit-review", methods=["POST"])
def submit_review():

    booking_id = request.form["booking_id"]
    provider_email = request.form["provider_email"]
    customer_name = request.form["customer_name"]
    rating = request.form["rating"]
    review = request.form["review"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reviews(
            booking_id,
            provider_email,
            customer_name,
            rating,
            review
        )
        VALUES(?,?,?,?,?)
    """,(
        booking_id,
        provider_email,
        customer_name,
        rating,
        review
    ))

    conn.commit()
    conn.close()

    return redirect("/booking-history")

# ===============================
# CUSTOMER REGISTER
# ===============================

@app.route("/customer-register")
def customer_register():
    return render_template("customer_register.html")

@app.route("/customer-submit", methods=["POST"])
def customer_submit():

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    phone = request.form["phone"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO customers(name,email,password,phone)
        VALUES(?,?,?,?)
    """, (
        name,
        email,
        password,
        phone
    ))

    conn.commit()
    conn.close()

    return redirect("/customer-login")

# ==========================================
# CUSTOMER LOGIN
# ==========================================

@app.route("/customer-login", methods=["GET", "POST"])
def customer_login():

    if request.method == "GET":
        return render_template("customer_login.html")

    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM customers
        WHERE email=? AND password=?
    """, (email, password))

    customer = cursor.fetchone()

    conn.close()

    if customer:
        session["customer"] = customer[0]
        return redirect("/customer-dashboard")

    return "<h2>Invalid Email or Password</h2>"

@app.route("/customer-dashboard")
def customer_dashboard():

    if "customer" not in session:
        return redirect("/customer-login")

    customer_id = session["customer"]

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # -------------------------
    # Customer Details
    # -------------------------
    cursor.execute("""
        SELECT *
        FROM customers
        WHERE id=?
    """, (customer_id,))

    customer = cursor.fetchone()

    if customer is None:
        conn.close()
        session.clear()
        return redirect("/customer-login")

    # -------------------------
    # Wishlist
    # -------------------------
    cursor.execute("""
        SELECT providers.*
        FROM wishlist
        INNER JOIN providers
        ON wishlist.provider_id = providers.id
        WHERE wishlist.customer_id=?
    """, (customer_id,))

    wishlist = cursor.fetchall()

    # -------------------------
    # Notifications
    # -------------------------
    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE customer_id=?
        ORDER BY id DESC
    """, (customer_id,))

    notifications = cursor.fetchall()

    conn.close()

    return render_template(
        "customer_dashboard.html",
        customer=customer,
        wishlist=wishlist,
        notifications=notifications
    )


@app.route("/customer-logout")
def customer_logout():

    # Remove customer session
    session.pop("customer", None)

    # Redirect to home page
    return redirect("/")



@app.route("/customer-support")
def customer_support():

    if "customer" not in session:
        return redirect("/customer-login")

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get logged-in customer
    cursor.execute("""
        SELECT *
        FROM customers
        WHERE id=?
    """, (session["customer"],))

    customer = cursor.fetchone()

    conn.close()

    return redirect("/support-chat/" + customer["email"])
# ======================================
# INVOICE ROUTE
# ======================================

@app.route("/invoice/<int:id>")
def invoice(id):

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM bookings WHERE id=?",
        (id,)
    )

    booking = cursor.fetchone()

    conn.close()

    if booking is None:
        return "Booking Not Found"

    return render_template(
        "invoice.html",
        booking=booking
    )





# ----------------------------
# Track Booking Page
# ----------------------------

@app.route("/track-booking")
def track_booking():
    return render_template("track_booking.html")


# ----------------------------
# Search Booking
# ----------------------------

@app.route("/track", methods=["POST"])
def track():

    email = request.form["email"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM bookings WHERE email=?",
        (email,)
    )

    bookings = cursor.fetchall()

    conn.close()

    return render_template(
        "booking_result.html",
        bookings=bookings
    )
@app.route("/reviews")
def reviews():

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, rating, review, review_date
        FROM reviews
        ORDER BY id DESC
    """)

    reviews = cursor.fetchall()

    conn.close()
    return render_template(
        "reviews.html",
        reviews=reviews
    )
@app.route("/check-date")
def check_date():

    # Get date selected by customer
    date = request.args.get("date")

    # Get selected provider
    provider_email = request.args.get("provider_email")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status
        FROM provider_availability
        WHERE provider_email=?
        AND available_date=?
    """, (
        provider_email,
        date
    ))

    result = cursor.fetchone()

    conn.close()

    if result and result[0] == "Available":
        return {"available": True}

    return {"available": False}

@app.route("/available-dates")
def available_dates():

    provider_email = request.args.get("provider_email")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT available_date
        FROM provider_availability
        WHERE provider_email=?
        AND status='Available'
    """, (provider_email,))

    dates = cursor.fetchall()

    conn.close()

    available = []

    for d in dates:
        available.append(d[0])

    return jsonify(available)


@app.route("/provider-login", methods=["POST"])
def provider_login_post():

    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM providers
        WHERE email=?
        AND password=?
        AND status='Approved'
    """, (email, password))

    provider = cursor.fetchone()

    conn.close()

    if provider:

        session["provider"] = provider[0]

        return redirect("/provider-dashboard")

    return "<h2>Invalid Login or Approval Pending</h2>"

@app.route("/delete-provider/<int:provider_id>")
def delete_provider(provider_id):
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM providers WHERE id=?", (provider_id,))
    conn.commit()
    conn.close()

    flash("Provider deleted successfully!", "success")
    return redirect("/admin-dashboard")


@app.route("/provider-dashboard")
def provider_dashboard():

    if "provider" not in session:
        return redirect("/provider-login")

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Logged in provider
    cursor.execute("""
        SELECT *
        FROM providers
        WHERE id=?
    """, (session["provider"],))

    provider = cursor.fetchone()

    provider_email = provider["email"]

    # -----------------------------
    # Total Bookings
    # -----------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE provider_email=?
        AND status='Approved'
    """, (provider_email,))

    total_bookings = cursor.fetchone()[0]

    # -----------------------------
    # Total Earnings
    # -----------------------------

    cursor.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM bookings
        WHERE provider_email=?
        AND status='Approved'
    """, (provider_email,))

    total_earnings = cursor.fetchone()[0]

    # -----------------------------
    # Current Month Earnings
    # -----------------------------

    current_month = datetime.now().strftime("%Y-%m")

    cursor.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM bookings
        WHERE provider_email=?
        AND status='Approved'
        AND date LIKE ?
    """, (
        provider_email,
        current_month + "%"
    ))

    month_earnings = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "provider_dashboard.html",
        provider=provider,
        total_bookings=total_bookings,
        total_earnings=total_earnings,
        month_earnings=month_earnings
    )
from datetime import datetime

@app.route("/provider-bookings")
def provider_bookings():

    if "provider" not in session:
        return redirect("/provider-login")

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # -----------------------------
    # Logged-in Provider
    # -----------------------------
    cursor.execute("""
        SELECT *
        FROM providers
        WHERE id=?
    """, (session["provider"],))

    provider = cursor.fetchone()

    provider_email = provider["email"]

    # -----------------------------
    # Provider Bookings
    # -----------------------------
    cursor.execute("""
        SELECT *
        FROM bookings
        WHERE provider_email=?
        ORDER BY date DESC
    """, (provider_email,))

    bookings = cursor.fetchall()

    # -----------------------------
    # Total Bookings
    # -----------------------------
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE provider_email=?
        AND status='Approved'
    """, (provider_email,))

    total_bookings = cursor.fetchone()[0]

    # -----------------------------
    # Total Earnings
    # -----------------------------
    cursor.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM bookings
        WHERE provider_email=?
        AND status='Approved'
    """, (provider_email,))

    total_earnings = cursor.fetchone()[0]

    # -----------------------------
    # Current Month Earnings
    # -----------------------------
    current_month = datetime.now().strftime("%m")

    cursor.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM bookings
        WHERE provider_email=?
        AND status='Approved'
        AND substr(date,4,2)=?
    """, (provider_email, current_month))

    month_earnings = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "provider_bookings.html",
        provider=provider,
        bookings=bookings,
        total_bookings=total_bookings,
        total_earnings=total_earnings,
        month_earnings=month_earnings
    )

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":
        session["admin"] = True
        return redirect("/admin")

    return "Invalid Login"


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/customer-login")

@app.route("/provider-edit")
def provider_edit():

    if "provider" not in session:
        return redirect("/provider-login")

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute(
    "SELECT * FROM providers WHERE id=?",
    (session["provider"],)
)
    provider = cursor.fetchone()

    conn.close()

    return render_template(
        "provider_edit.html",
        provider=provider
    )
@app.route("/provider-update", methods=["POST"])
def provider_update():

    if "provider" not in session:
        return redirect("/provider-login")

    id = request.form["id"]
    name = request.form["name"]
    phone = request.form["phone"]
    service = request.form["service"]
    experience = request.form["experience"]
    description = request.form["description"]

    image = request.files["image"]

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    if image.filename != "":

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

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
        """,
        (
            name,
            phone,
            service,
            experience,
            description,
            filename,
            id
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
        """,
        (
            name,
            phone,
            service,
            experience,
            description,
            id
        ))

    conn.commit()
    conn.close()

    return redirect("/provider-dashboard")

@app.route("/booked-dates")
def booked_dates():

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date
        FROM bookings
        WHERE status='Approved'
    """)

    dates = cursor.fetchall()

    conn.close()

    booked = []

    for d in dates:
        booked.append(d[0])

    return jsonify(booked)

@app.route("/provider-logout")
def provider_logout():

    session.pop("provider", None)

    return redirect("/provider-login")

from datetime import datetime

@app.route("/support", methods=["GET", "POST"])
def support():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        message = request.form["message"]

        conn = sqlite3.connect("bookings.db")

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO support_messages
            (
                customer_name,
                customer_email,
                sender,
                message,
                created_at
            )

            VALUES(?,?,?,?,?)

        """, (

            name,

            email,

            "Customer",

            message,

            datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        ))

        conn.commit()

        conn.close()

    return redirect("/support-chat/" + email)
    return render_template("support_chat.html")


@app.route("/support-chat/<email>", methods=["GET", "POST"])
def support_chat(email):

    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # -----------------------------
    # Customer Sends New Message
    # -----------------------------
    if request.method == "POST":

        message = request.form["message"]

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

            VALUES(?,?,?,?,?,?)
        """, (

            "",

            email,

            "Customer",

            message,

            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),

            "Open"

        ))

        conn.commit()

    # -----------------------------
    # Load Complete Conversation
    # -----------------------------

    cursor.execute("""

        SELECT *

        FROM support_messages

        WHERE customer_email=?

        ORDER BY id

    """, (email,))

    chats = cursor.fetchall()

    conn.close()

    return render_template(
        "support_chat_page.html",
        chats=chats,
        email=email
    )

# =====================================================
# AI EVENT PLANNER
# =====================================================

@app.route("/event-planner", methods=["GET", "POST"])
def event_planner():

    suggestion = None

    if request.method == "POST":

        # -----------------------------
        # Get Form Data
        # -----------------------------

        event = request.form.get("event")

        guests = int(request.form.get("guests"))

        budget = int(request.form.get("budget"))

        suggestions = []

        # -----------------------------
        # AI Service Suggestions
        # -----------------------------

        if event == "Wedding":

            suggestions = [

                "💒 Premium Venue Decoration",
                "📸 Professional Photography",
                "🎥 Cinematic Videography",
                "🎵 DJ & Live Music",
                "🍽 Premium Catering",
                "💄 Bridal Makeup",
                "🌸 Flower Decoration",
                "🎂 Luxury Wedding Cake"

            ]

        elif event == "Birthday":

            suggestions = [

                "🎈 Balloon Decoration",
                "🎂 Customized Birthday Cake",
                "📸 Photography",
                "🎵 DJ",
                "🍕 Food Catering",
                "🎁 Return Gifts",
                "🎨 Theme Decoration"

            ]

        elif event == "Corporate":

            suggestions = [

                "🎤 Stage Setup",
                "🎧 Sound System",
                "📽 LED Screen",
                "🍽 Corporate Catering",
                "📸 Event Photography",
                "🪑 Conference Seating",
                "🎁 Welcome Kit"

            ]

        elif event == "Engagement":

            suggestions = [

                "💍 Ring Ceremony Stage",
                "📸 Photography",
                "🎵 Music System",
                "🌸 Flower Decoration",
                "🍽 Catering"

            ]

        elif event == "Reception":

            suggestions = [

                "✨ Luxury Decoration",
                "🎥 Videography",
                "🎵 Live Orchestra",
                "🍽 Catering",
                "📸 Photography"

            ]

        # -----------------------------
        # Package Recommendation
        # -----------------------------

        if budget < 50000:

            package = "⭐ Basic Package"

        elif budget < 150000:

            package = "⭐⭐ Premium Package"

        else:

            package = "⭐⭐⭐ Luxury Package"

        # -----------------------------
        # Venue Recommendation
        # -----------------------------

        if guests <= 100:

            venue = "Small Banquet Hall"

        elif guests <= 300:

            venue = "Medium Convention Hall"

        else:

            venue = "Large Convention Centre"

        # -----------------------------
        # Estimated Cost
        # -----------------------------

        estimated_cost = guests * 1200

        if event == "Wedding":

            estimated_cost += 150000

        elif event == "Birthday":

            estimated_cost += 40000

        elif event == "Corporate":

            estimated_cost += 80000

        elif event == "Engagement":

            estimated_cost += 60000

        elif event == "Reception":

            estimated_cost += 100000

        # -----------------------------
        # Cost Per Guest
        # -----------------------------

        per_guest = estimated_cost // guests

        # -----------------------------
        # Planning Duration
        # -----------------------------

        if guests <= 100:

            planning_days = "10 - 15 Days"

        elif guests <= 300:

            planning_days = "20 - 30 Days"

        else:

            planning_days = "45 - 60 Days"

        # -----------------------------
        # AI Confidence
        # -----------------------------

        confidence = 98

        # -----------------------------
        # AI Recommendation
        # -----------------------------

        suggestion = {

            "event": event,

            "guests": guests,

            "budget": budget,

            "package": package,

            "venue": venue,

            "services": suggestions,

            "estimated_cost": estimated_cost,

            "per_guest": per_guest,

            "planning_days": planning_days,

            "confidence": confidence

        }


# =====================================================
# AI BUDGET ESTIMATOR
# =====================================================

@app.route("/budget-estimator", methods=["GET", "POST"])
def budget_estimator():

    result = None

    if request.method == "POST":

        event = request.form.get("event")

        guests = int(request.form.get("guests"))

        budget = int(request.form.get("budget"))

        # ------------------------
        # Estimated Costs
        # ------------------------

        decoration = guests * 150
        catering = guests * 500
        photography = 25000
        entertainment = 15000
        miscellaneous = 10000

        if event == "Wedding":
            venue = 100000

        elif event == "Birthday":
            venue = 30000

        elif event == "Corporate":
            venue = 60000

        elif event == "Reception":
            venue = 70000

        else:
            venue = 50000

        total = (
            decoration +
            catering +
            photography +
            entertainment +
            miscellaneous +
            venue
        )

        if total <= budget:
            status = "✅ Your budget is sufficient."
        else:
            status = "⚠ Your budget is lower than the estimated cost."

        result = {

            "event": event,

            "guests": guests,

            "budget": budget,

            "decoration": decoration,

            "catering": catering,

            "photography": photography,

            "entertainment": entertainment,

            "miscellaneous": miscellaneous,

            "venue": venue,

            "total": total,

            "status": status

        }

    return render_template(
        "budget_estimator.html",
        result=result
    )



    return render_template(

        "event_planner.html",

        suggestion=suggestion

    )





if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )

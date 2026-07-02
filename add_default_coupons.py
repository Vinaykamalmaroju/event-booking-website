import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

coupons = [

    ("WELCOME10",10),

    ("EVENT20",20),

    ("NEWUSER",15)

]

for coupon in coupons:

    try:

        cursor.execute(
            "INSERT INTO coupons(coupon_code,discount) VALUES(?,?)",
            coupon
        )

    except:

        pass

conn.commit()
conn.close()

print("Coupons Added")
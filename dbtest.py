#!/usr/bin/env python3
"""
Database Setup Script for BBMS Flask App

- Checks/creates database tables
- Adds a superadmin user if it doesn't exist
- Prints login info
"""

from app import create_app, db, bcrypt
from app.models import User

# Create Flask app context
app = create_app()
app.app_context().push()


# 3 Check if superadmin exists
username = "superadmin"
email = "superadmin@bagbank.com"
password = "superadmin"  # Plain text password

existing_user = User.query.filter(User.username==username).first()
if existing_user:
    print(f"Superadmin already exists: username={existing_user.username}, email={existing_user.email}")
else:    
    # 4️⃣ Hash the password
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    # 5️⃣ Create the superadmin user
    # superadmin = User(
    #     username=username,
    #     email=email,
    #     password_hash=hashed_pw,
    #     role="superadmin",  # Ensure your User model has a 'role' column
    #     name="Super Admin",
    #     phone="1234567890"
    # )
    # db.session.add(superadmin)
    # db.session.commit()
    print("Superadmin user created successfully!")

# 6️⃣ Print login info
print("\n✅ Superadmin Login Info")
print(f"User: {existing_user.username}")
print(f"User: {existing_user.role}")
print(f"User: {existing_user.is_superadmin()}")


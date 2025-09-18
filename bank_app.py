import json
import random
import string
from pathlib import Path
import streamlit as st


class Bank:
    database = "data.json"
    data = []

    # Load data from JSON if exists
    try:
        if Path(database).exists():
            with open(database, "r") as fs:
                data = json.load(fs)
        else:
            data = []
    except Exception as err:
        st.error(f"An error occurred while loading database: {err}")
        data = []

    @classmethod
    def __update(cls):
        """Save changes to the database file"""
        with open(cls.database, "w") as fs:
            json.dump(cls.data, fs, indent=4)

    @classmethod
    def __accountgenerate(cls):
        """Generate unique account number"""
        alpha = random.choices(string.ascii_uppercase, k=3)
        num = random.choices(string.digits, k=3)
        spchar = random.choices("$#%&@!", k=1)
        acc_id = alpha + num + spchar
        random.shuffle(acc_id)
        return "".join(acc_id)

    @classmethod
    def create_account(cls, name, age, email, pin):
        if age < 18 or len(str(pin)) != 4:
            return None, "You are not eligible to open an account"

        info = {
            "name": name,
            "age": age,
            "email": email,
            "pin": pin,
            "accountnumber": cls.__accountgenerate(),
            "balance": 0,
        }
        cls.data.append(info)
        cls.__update()
        return info, "Account created successfully!"

    @classmethod
    def find_user(cls, account, pin):
        return [i for i in cls.data if i["accountnumber"] == account and i["pin"] == pin]

    @classmethod
    def deposit(cls, account, pin, amount):
        user = cls.find_user(account, pin)
        if not user:
            return "Account not found"
        if amount <= 0 or amount > 10000:
            return "Deposit must be between 1 and 10000"
        user[0]["balance"] += amount
        cls.__update()
        return "Amount deposited successfully!"

    @classmethod
    def withdraw(cls, account, pin, amount):
        user = cls.find_user(account, pin)
        if not user:
            return "Account not found"
        if amount <= 0 or amount > 10000:
            return "Withdrawal must be between 1 and 10000"
        if user[0]["balance"] < amount:
            return "Insufficient balance"
        user[0]["balance"] -= amount
        cls.__update()
        return "Amount withdrawn successfully!"

    @classmethod
    def details(cls, account, pin):
        user = cls.find_user(account, pin)
        if not user:
            return None
        return user[0]

    @classmethod
    def update(cls, account, pin, field, new_value):
        user = cls.find_user(account, pin)
        if not user:
            return "Account not found"
        if field == "pin" and len(str(new_value)) != 4:
            return "PIN must be 4 digits"
        user[0][field] = new_value
        cls.__update()
        return f"{field} updated successfully!"

    @classmethod
    def delete(cls, account, pin):
        user = cls.find_user(account, pin)
        if not user:
            return "Account not found"
        cls.data.remove(user[0])
        cls.__update()
        return "Account deleted successfully!"


# ---------------- STREAMLIT UI ---------------- #
st.title("🏦 Simple Bank System")

menu = ["Create Account", "Deposit", "Withdraw", "Account Details", "Update Account", "Delete Account"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Create Account":
    st.subheader("Create a New Account")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, step=1)
    email = st.text_input("Email")
    pin = st.text_input("PIN (4 digits)", type="password")
    if st.button("Create"):
        if not pin.isdigit():
            st.error("PIN must be numeric")
        else:
            acc, msg = Bank.create_account(name, age, email, int(pin))
            st.success(msg)
            if acc:
                st.json(acc)

elif choice == "Deposit":
    st.subheader("Deposit Money")
    account = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    amount = st.number_input("Amount", min_value=1)
    if st.button("Deposit"):
        st.info(Bank.deposit(account, int(pin), amount))

elif choice == "Withdraw":
    st.subheader("Withdraw Money")
    account = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    amount = st.number_input("Amount", min_value=1)
    if st.button("Withdraw"):
        st.info(Bank.withdraw(account, int(pin), amount))

elif choice == "Account Details":
    st.subheader("Check Account Details")
    account = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    if st.button("Check"):
        details = Bank.details(account, int(pin))
        if details:
            st.json(details)
        else:
            st.error("Account not found")

elif choice == "Update Account":
    st.subheader("Update Account Information")
    account = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    field = st.selectbox("Field to Update", ["name", "email", "pin"])
    new_value = st.text_input("New Value")
    if st.button("Update"):
        if field == "pin" and not new_value.isdigit():
            st.error("PIN must be numeric")
        else:
            st.success(Bank.update(account, int(pin), field, new_value if field != "pin" else int(new_value)))

elif choice == "Delete Account":
    st.subheader("Delete Your Account")
    account = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    if st.button("Delete"):
        st.warning(Bank.delete(account, int(pin)))

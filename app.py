import streamlit as st

from db import (
    initialize_database,
    get_voter,
    register_voter
)

# Initialize database
initialize_database()

# Page configuration
st.set_page_config(
    page_title="VIGIL",
    page_icon="🛡️",
    layout="centered"
)

# Title
st.title("🛡️ VIGIL")
st.caption("Voter Identity & Integrity Guard")
st.write("Simulated polling station")

st.divider()

# -------------------------------
# VOTER REGISTRATION
# -------------------------------

st.header("👤 Register Voter")

student_id = st.text_input(
    "Student ID",
    placeholder="Example: 25UAD105",
    key="register_id"
)

name = st.text_input(
    "Student Name",
    placeholder="Example: Adith",
    key="register_name"
)

if st.button("Register Voter"):

    if not student_id or not name:
        st.warning("Please enter both Student ID and Name.")

    else:
        existing_voter = get_voter(student_id)

        if existing_voter:
            st.error("⚠️ This Student ID is already registered.")

        else:
            register_voter(student_id, name)
            st.success(f"✅ {name} registered successfully!")

st.divider()

# -------------------------------
# VOTER VERIFICATION
# -------------------------------

st.header("🔎 Verify Voter")

verify_id = st.text_input(
    "Enter Student ID",
    placeholder="Example: 25UAD105",
    key="verify_id"
)

if st.button("Verify Voter"):

    if not verify_id:
        st.warning("Please enter a Student ID.")

    else:
        voter = get_voter(verify_id)

        if voter:

            st.success("✅ Voter found!")

            st.write(f"**Student ID:** {voter[1]}")
            st.write(f"**Name:** {voter[2]}")

            if voter[3] == 1:
                st.success("📷 Face registered")
            else:
                st.info("📷 Face not registered")

            if voter[4] == 1:
                st.error("🚫 This voter has already voted.")
            else:
                st.info("🗳️ Voting status: Not voted")

        else:
            st.error("❌ Voter not found.")
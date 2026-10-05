import streamlit as st
import cv2
from pathlib import Path

from db import (
    initialize_database,
    get_voter,
    register_voter,
    mark_face_registered
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

st.divider()

# FACE REGISTRATION

st.divider()
st.header("Face Registration")

face_id = st.text_input(
    "Enter registered Student ID for face registration",
    key="face_register_id"
)

camera_image = st.camera_input("Capture face")

if st.button("Register Face"):
    if not face_id.strip():
        st.warning("Please enter a Student ID.")

    else:
        voter = get_voter(face_id.strip())

        if voter is None:
            st.error("Student ID is not registered.")

        elif camera_image is None:
            st.warning("Please capture a face image first.")

        else:
            image_bytes = camera_image.getvalue()
            image_array = __import__("numpy").frombuffer(
                image_bytes, dtype=__import__("numpy").uint8
            )
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if frame is None:
                st.error("Could not read the captured image.")

            else:
                detector = cv2.CascadeClassifier(
                    cv2.data.haarcascades
                    + "haarcascade_frontalface_default.xml"
                )

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                faces = detector.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(60, 60)
                )

                if len(faces) == 0:
                    st.error(
                        "No face detected. Try again with better lighting "
                        "and your face clearly visible."
                    )

                elif len(faces) > 1:
                    st.error(
                        "Multiple faces detected. Please capture only "
                        "the enrolled participant."
                    )

                else:
                    student_id = face_id.strip()
                    save_dir = Path("face_data")
                    save_dir.mkdir(parents=True, exist_ok=True)

                    image_path = save_dir / f"{student_id}.jpg"

                    success = cv2.imwrite(str(image_path), frame)

                    if not success:
                        st.error("Could not save the face image.")

                    elif mark_face_registered(student_id):
                        st.success(
                            f"Face image saved for Student ID {student_id}."
                        )
                        st.image(
                            str(image_path),
                            caption="Saved test face image",
                            width=350
                        )

                    else:
                        st.error("Could not update the database.")

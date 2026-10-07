import streamlit as st
import cv2
import numpy as np
from pathlib import Path

from db import (
    initialize_database,
    get_voter,
    register_voter,
    mark_face_registered,
    mark_as_voted,
    cast_vote
)

# Initialize database
initialize_database()


# Page configuration
st.set_page_config(
    page_title="VIGIL",
    page_icon="V",
    layout="centered"
)


# --------------------------------------------------
# FACE RECOGNITION FUNCTION
# --------------------------------------------------

def recognize_face(student_id, captured_image):

    student_dir = Path("face_data") / student_id

    if not student_dir.exists():
        return False, "No enrolled face data found."

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    training_faces = []
    training_labels = []

    image_files = list(
        student_dir.glob("sample_*.jpg")
    )

    if not image_files:
        return False, "No face samples found for this student."

    for image_path in image_files:

        image = cv2.imread(
            str(image_path),
            cv2.IMREAD_GRAYSCALE
        )

        if image is None:
            continue

        image = cv2.equalizeHist(image)

        image = cv2.resize(
            image,
            (200, 200)
        )

        training_faces.append(image)
        training_labels.append(1)

    if not training_faces:
        return False, "Could not load enrolled face samples."

    recognizer.train(
        training_faces,
        np.array(training_labels)
    )

    image_array = np.frombuffer(
        captured_image.getvalue(),
        dtype=np.uint8
    )

    frame = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if frame is None:
        return False, "Could not read captured image."

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.equalizeHist(gray)

    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    if len(faces) == 0:
        return False, "No face detected."

    if len(faces) > 1:
        return False, "Multiple faces detected. Please show only one face."

    x, y, w, h = faces[0]

    captured_face = gray[
        y:y + h,
        x:x + w
    ]

    captured_face = cv2.resize(
        captured_face,
        (200, 200)
    )

    label, confidence = recognizer.predict(
        captured_face
    )

    if confidence < 65:
        return True, f"Face matched. Score: {confidence:.1f}"

    return False, f"Face did not match. Score: {confidence:.1f}"

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("VIGIL")
st.caption("Voter Identity & Integrity Guard")
st.write("Simulated polling station")

st.divider()


# --------------------------------------------------
# VOTER VERIFICATION
# --------------------------------------------------

st.header("Verify Voter")

verify_id = st.text_input(
    "Enter Student ID",
    placeholder="Example: 25UAD105",
    key="vote_verify_id"
)

verification_image = st.camera_input(
    "Capture face for verification",
    key="verification_camera"
)

if st.button("Verify Voter"):

    if not verify_id:

        st.warning("Please enter a Student ID.")

    else:

        voter = get_voter(verify_id)

        if voter is None:

            st.error("Voter not found.")

        elif voter[3] == 0:

            st.warning(
                "Face is not registered for this voter."
            )

        elif verification_image is None:

            st.warning(
                "Please capture a face for verification."
            )

        else:

            matched, message = recognize_face(
                verify_id,
                verification_image
            )

            if matched:

                st.success(message)
                st.success("Voter identity verified.")

                if voter[4] == 1:

                    st.error(
                        "This voter has already voted."
                    )

                else:

                    st.info(
                        "Voting status: Not voted."
                    )

                    st.divider()

                    st.subheader("Cast Your Vote")

                    candidate = st.radio(
                        "Select a candidate:",
                        [
                            "Candidate A",
                            "Candidate B",
                            "Candidate C"
                        ],
                        key="candidate_choice"
                    )

                    confirm_vote = st.checkbox(
                        "I confirm that I want to cast this vote.",
                        key="confirm_vote"
                    )

                    if st.button("Cast Vote"):

                        if not confirm_vote:

                            st.warning(
                                "Please confirm your vote first."
                            )

                        else:

                            success = cast_vote(
                                verify_id,
                                candidate
                            )

                            if success:

                                st.success(
                                    f"Vote successfully recorded for {candidate}."
                                )

                                st.info(
                                    "This voter is now marked as having voted."
                                )

                            else:

                                st.error(
                                    "Vote could not be recorded."
                                )

            else:

                st.error(message)

                st.error(
                    "Voter identity could not be verified."
                )

# --------------------------------------------------
# FACE REGISTRATION
# --------------------------------------------------

st.header("Face Registration")

face_id = st.text_input(
    "Enter registered Student ID for face registration",
    key="face_register_id"
)

camera_image = st.camera_input(
    "Capture face"
)

if st.button("Register Face"):

    if not face_id.strip():

        st.warning(
            "Please enter a Student ID."
        )

    else:

        voter = get_voter(
            face_id.strip()
        )

        if voter is None:

            st.error(
                "Student ID is not registered."
            )

        elif camera_image is None:

            st.warning(
                "Please capture a face image first."
            )

        else:

            image_bytes = camera_image.getvalue()

            image_array = np.frombuffer(
                image_bytes,
                dtype=np.uint8
            )

            frame = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if frame is None:

                st.error(
                    "Could not read the captured image."
                )

            else:

                detector = cv2.CascadeClassifier(
                    cv2.data.haarcascades +
                    "haarcascade_frontalface_default.xml"
                )

                gray = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY
                )

                faces = detector.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(60, 60)
                )

                if len(faces) == 0:

                    st.error(
                        "No face detected. Try again with better lighting."
                    )

                elif len(faces) > 1:

                    st.error(
                        "Multiple faces detected. Please capture only one face."
                    )

                else:

                    student_id = face_id.strip()

                    save_dir = Path(
                        "face_data"
                    )

                    save_dir.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    image_path = (
                        save_dir /
                        f"{student_id}.jpg"
                    )

                    success = cv2.imwrite(
                        str(image_path),
                        frame
                    )

                    if not success:

                        st.error(
                            "Could not save the face image."
                        )

                    elif mark_face_registered(
                        student_id
                    ):

                        st.success(
                            f"Face registered successfully for {student_id}."
                        )

                        st.image(
                            str(image_path),
                            caption="Enrolled face",
                            width=350
                        )

                    else:

                        st.error(
                            "Could not update the database."
                        )


st.divider()


# --------------------------------------------------
# VOTER VERIFICATION
# --------------------------------------------------

st.header("Verify Voter")

verify_id = st.text_input(
    "Enter Student ID",
    placeholder="Example: 25UAD105",
    key="verify_id"
)

verification_image = st.camera_input(
    "Capture face for verification",
    key="verification_camera"
)

if st.button("Verify Voter"):

    if not verify_id:

        st.warning(
            "Please enter a Student ID."
        )

    else:

        voter = get_voter(
            verify_id
        )

        if voter:

            st.write(
                f"Student ID: {voter[1]}"
            )

            st.write(
                f"Name: {voter[2]}"
            )

            if voter[3] == 0:

                st.warning(
                    "Face is not registered for this voter."
                )

            elif verification_image is None:

                st.warning(
                    "Please capture a face for verification."
                )

            else:

                matched, message = recognize_face(
                    verify_id,
                    verification_image
                )

                if matched:

                    st.success(
                        message
                    )

                    st.success(
                        "Voter identity verified."
                    )

                    if voter[4] == 1:

                        st.error(
                            "This voter has already voted."
                        )

                    else:

                        st.info(
                            "Voting status: Not voted."
                        )

                else:

                    st.error(
                        message
                    )

                    st.error(
                        "Voter identity could not be verified."
                    )

        else:

            st.error(
                "Voter not found."
            )
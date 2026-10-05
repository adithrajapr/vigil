import cv2
from pathlib import Path
import numpy as np

FACE_DIR = Path("face_data")

student_id = input("Enter Student ID: ").strip()
known_face_path = FACE_DIR / f"{student_id}.jpg"

if not known_face_path.exists():
    print("No enrolled face found for this Student ID.")
    raise SystemExit

detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

recognizer = cv2.face.LBPHFaceRecognizer_create()

known_image = cv2.imread(str(known_face_path))

if known_image is None:
    print("Could not read enrolled face image.")
    raise SystemExit

known_gray = cv2.cvtColor(known_image, cv2.COLOR_BGR2GRAY)

known_faces = detector.detectMultiScale(
    known_gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(60, 60)
)

if len(known_faces) != 1:
    print("Could not find exactly one face in the enrolled image.")
    raise SystemExit

x, y, w, h = known_faces[0]
known_face = known_gray[y:y + h, x:x + w]

recognizer.train([known_face], np.array([1]))

print("Enrolled face loaded.")
print("Starting recognition test.")
print("Press Q to quit.")

camera = cv2.VideoCapture(0)

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read camera frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    for (x, y, w, h) in faces:

        face = gray[y:y + h, x:x + w]

        label, confidence = recognizer.predict(face)

        if confidence < 70:
            text = "MATCH"
        else:
            text = "NO MATCH"

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"{text} ({confidence:.1f})",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    cv2.imshow("VIGIL - Face Recognition Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
import cv2
from pathlib import Path
import numpy as np

FACE_DIR = Path("face_data")

student_id = input("Enter Student ID: ").strip()

student_dir = FACE_DIR / student_id

if not student_dir.exists():
    print("No enrolled face data found.")
    raise SystemExit

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
    print("No face samples found.")
    raise SystemExit

for image_path in image_files:

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_GRAYSCALE
    )

    if image is not None:

        image = cv2.equalizeHist(image)

        image = cv2.resize(
            image,
            (200, 200)
        )

        training_faces.append(image)
        training_labels.append(1)

if not training_faces:
    print("Could not load face samples.")
    raise SystemExit

recognizer.train(
    training_faces,
    np.array(training_labels)
)

print()
print(f"Loaded {len(training_faces)} face samples.")
print("Recognition started.")
print("Press Q to quit.")

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera could not be opened.")
    raise SystemExit

while True:

    success, frame = camera.read()

    if not success:
        break

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

    for (x, y, w, h) in faces:

        face = gray[
            y:y + h,
            x:x + w
        ]

        face = cv2.resize(
            face,
            (200, 200)
        )

        label, confidence = recognizer.predict(face)

        if confidence < 65:

            result = "MATCH"

        else:

            result = "NO MATCH"

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"{result} | Score: {confidence:.1f}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2
        )

    cv2.imshow(
        "VIGIL - Face Recognition",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
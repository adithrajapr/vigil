import cv2
from pathlib import Path
from db import get_voter, mark_face_registered

FACE_DIR = Path("face_data")

student_id = input("Enter Student ID: ").strip()

voter = get_voter(student_id)

if voter is None:
    print("Student ID is not registered.")
    raise SystemExit

student_dir = FACE_DIR / student_id
student_dir.mkdir(parents=True, exist_ok=True)

detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera could not be opened.")
    raise SystemExit

print()
print("Face enrollment started.")
print("Look at the camera.")
print("Slowly move your head left, right, up and down.")
print("Press Q to cancel.")
print()

sample_count = 0
frame_count = 0
target_samples = 20

while sample_count < target_samples:

    success, frame = camera.read()

    if not success:
        print("Could not read camera frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    gray = cv2.equalizeHist(gray)

    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    if len(faces) == 1:

        x, y, w, h = faces[0]

        face = gray[y:y + h, x:x + w]

        face = cv2.resize(
            face,
            (200, 200)
        )

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Samples: {sample_count}/{target_samples}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        frame_count += 1

        if frame_count % 5 == 0:

            sample_count += 1

            image_path = (
                student_dir /
                f"sample_{sample_count}.jpg"
            )

            cv2.imwrite(
                str(image_path),
                face
            )

    else:

        cv2.putText(
            frame,
            "Show exactly one face",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    cv2.imshow(
        "VIGIL - Face Enrollment",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

if sample_count == target_samples:

    mark_face_registered(student_id)

    print()
    print(f"Enrollment complete.")
    print(f"{sample_count} face samples saved.")
    print(f"Student ID: {student_id}")

else:

    print()
    print("Enrollment cancelled.")
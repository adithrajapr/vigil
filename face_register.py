
import cv2
from pathlib import Path

SAVE_DIR = Path("face_data")
SAVE_DIR.mkdir(exist_ok=True)

detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera could not be opened.")
    raise SystemExit

print("Press S to save your detected face.")
print("Press Q to quit.")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read camera frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            frame, "Face detected", (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )

    cv2.imshow("VIGIL - Face Registration", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        if len(faces) == 0:
            print("No face detected. Try again in better lighting.")
        else:
            filename = SAVE_DIR / "test_face.jpg"
            cv2.imwrite(str(filename), frame)
            print(f"Face image saved: {filename}")

    elif key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

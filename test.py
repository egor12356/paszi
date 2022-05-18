

import face_recognition
from PIL import Image
import cv2

# known_image = face_recognition.load_image_file("biden.jpg")
known_image = cv2.imread("biden.jpg")
# unknown_image = face_recognition.load_image_file("unknown.jpg")
unknown_image = cv2.imread("biden1.jpg")

biden_encoding = face_recognition.face_encodings(known_image)[0]
unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

results = face_recognition.compare_faces([biden_encoding], unknown_encoding)

print(results)
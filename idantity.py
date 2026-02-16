import cv2
import face_recognition
from database import *

def ditact_face(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    location = face_recognition.face_locations(rgb)
    return rgb,location
def face_encoding(rgb,location):
    return face_recognition.face_encodings(rgb,location)

def match_face(face_embedding, threshold=0.5):
    user = find_user_by_embedding(face_embedding, threshold)
    return user


import cv2
import face_recognition

# 0 means the default laptop webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    resized_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_resized_frame)

    if face_locations:
        print('Face Detected')
    else:
        print('Face not detected.')

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
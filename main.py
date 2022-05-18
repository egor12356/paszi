import pickle
import time

import face_recognition
import cv2
import numpy as np
from add_user import get_arr_name_and_img


# Время жизни распознованного образа
from connect_to_bd import update_last_access

TIME_LIVE = 5


class User:
    def __init__(self, name):
        # Имя пользователя
        self.name = name
        # Текущий статус пользователя
        self.active = False
        # Время обнаружения пользователя
        self.time_found = ''
        # Время непрерывного обнаружения пользователя
        self.time_live = 0




def get_known_face_encodings_and_known_face_names():
    """Получаем массив изображений и имен из БД"""

    # Получаем данные из БД
    arr_name_and_img = get_arr_name_and_img()

    print('Данные из БД получены!')

    known_face_encodings = []
    known_face_names = []

    for name, blob in arr_name_and_img:
        # Приводим изображение в нужный формат
        img = pickle.loads(blob)
        img_need = face_recognition.face_encodings(img)[0]

        known_face_names.append(name)
        known_face_encodings.append(img_need)

    return known_face_encodings, known_face_names


def clean_found_names(dict_names_is_found):
    """Удаляем имена людей, которые ушли из поля зрения"""
    time_now = time.time()

    names_for_del = []

    # Проходим по всем именам
    for name, time_found in dict_names_is_found.items():

        # Этот человек ушел из поля зрения более TIME_LIVE секунд назад, удаляем его из найденных
        if time_now - time_found > TIME_LIVE:
            names_for_del.append(name)

    # Удаляем распознанных пользователей
    for name in names_for_del:
        del dict_names_is_found[name]
        print(f'Пользователь {name} пропал из поля зрения')

        if name != "Unknown":
            # Обновляем время последнего распознования
            update_last_access(name)


def main():

    # Массив найденных имен
    dict_names_is_found = {}



    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)


    # obama_image = cv2.imread("im.jpg")
    # obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
    #
    #
    # biden_image = cv2.imread("biden.jpg")
    # biden_face_encoding = face_recognition.face_encodings(biden_image)[0]


    # # Массив изображений из БД
    # known_face_encodings = [
    #     obama_face_encoding,
    #     biden_face_encoding
    # ]
    #
    # # Массив имен владельцев фото из БД
    # known_face_names = [
    #     "Im",
    #     "Joe Biden"
    # ]

    print('Получаем данные из БД')
    # Получаем данные из БД
    known_face_encodings, known_face_names = get_known_face_encodings_and_known_face_names()
    print('Данные из БД приведены к нужному ввиду!')

    # Initialize some variables
    face_locations = []
    face_names = []
    process_this_frame = True

    while True:

        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # If a match was found in known_face_encodings, just use the first one.
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                # # Or instead, use the known face with the smallest distance to the new face
                # face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                # best_match_index = np.argmin(face_distances)
                # if matches[best_match_index]:
                #     name = known_face_names[best_match_index]

                face_names.append(name)


                # if name != 'Unknown':
                # Добавляем распознанного пользователя в список найденных с текущим именем

                # Пользователь только что попал в поле зрения, обновляем его время последнего доступа
                if name not in dict_names_is_found and name != "Unknown":
                    # Обновляем время последнего распознования
                    update_last_access(name)
                    print(f'Пользователь {name} распознан!')

                dict_names_is_found[name] = time.time()




        # Удаляем имена людей, которые ушли из поля зрения
        clean_found_names(dict_names_is_found)


        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
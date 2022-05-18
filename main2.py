import os
import pickle
import time

import face_recognition
import cv2
from connect_to_bd import update_last_access, get_arr_name_and_img

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

    def __repr__(self):
        return f'name: {self.name}, time_found: {self.time_found}, time_live: {self.time_live}'




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
    for name, user in dict_names_is_found.items():

        # Этот человек ушел из поля зрения более TIME_LIVE секунд назад, удаляем его из найденных
        if time_now - user.time_found > TIME_LIVE:
            names_for_del.append(name)

        # Человек всё ещё в поле зрения, проверяем сколько он находится в состоянии распознанным
        else:
            # Пользователь находится в поле зрения в течении TIME_LIVE секунд
            if user.time_live > TIME_LIVE + 3:

                # Это новый распознанный пользователь, сообщаем о его нахождении и обновляем время последнего доступа
                if not user.active:
                    # Сообщаем о распозновании пользователя
                    print(f'Пользователь {name} распознан!')

                    # Меняем его статус
                    user.active = True

                    # Обновляем время последнего распознования
                    update_last_access(name)



    # Удаляем распознанных пользователей
    for name in names_for_del:
        user = dict_names_is_found[name]

        # Пользователь был распознан и находился в поле зрения в течении TIME_LIVE секунд
        if user.active and name != "Unknown":
            # Обновляем время последнего распознования
            update_last_access(name)

            print(f'Пользователь {name} пропал из поля зрения')


        del dict_names_is_found[name]




def main():

    # Массив найденных имен
    dict_names_is_found = {}

    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    # RTSP_URL = 'rtsp://admin:123Qwerty@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'
    #
    # os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
    #
    # video_capture = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

    # RTSP_URL = 'rtsp://admin:123Qwerty@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'
    #
    # os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
    #
    # video_capture = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)


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

        cv2.imshow('RTSP stream', frame)
        pass

    # cap.release()
    # cv2.destroyAllWindows()

        if type(frame) == None:
            pass

        else:


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

                    face_names.append(name)


                    if name != "Unknown":
                        # Пользователь только что попал в поле зрения
                        if name not in dict_names_is_found:
                            # Создаем объект класса User
                            user = User(name)

                            # Добавляем в список найденных
                            dict_names_is_found[name] = user

                            # Обновляем время нахождения пользователя
                            dict_names_is_found[name].time_found = time.time()


                        # Пользователь был в поле зрения
                        else:
                            user = dict_names_is_found[name]

                            # Обновляем время непрерывного обнаружения пользователя
                            user.time_live += time.time() - user.time_found

                            # Обновляем время последнего нахождения пользователя
                            user.time_found = time.time()


            print(dict_names_is_found)
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
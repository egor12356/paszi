import pickle

import bcrypt as bcrypt
import cv2

from connect_to_bd import connect_bd, name_table


def add_user(name, path, hash_passw):
    """Добавляем пользователя в БД"""
    db, cursor = connect_bd()  # Подключение к БД

    print('Перевод изображения в нужный формат')
    img = cv2.imread(path)
    blob = pickle.dumps(img, -1)
    print('Изображение успешно конвертировано')

    sql = f"INSERT INTO {name_table} (name, img, password_hash) VALUES (%s, %s, %s)"
    val = (name, blob, hash_passw)
    cursor.execute(sql, val)
    db.commit()
    db.close()





if __name__ == '__main__':
    # name = 'Ivan'
    # path = 'Ivan.jpg'

    name = input('Введите имя нового пользователя: ')
    password = input('Введите пароль нового пользователя: ')
    path = input('Введите путь к фото нового пользователя: ')

    # Переводим пароль в хеш
    hash_passw = str(bcrypt.hashpw(password.encode(), bcrypt.gensalt()))

    hash_passw = hash_passw.replace("b'", "").replace("'", '')
    print(hash_passw)
    print(type(hash_passw))

    add_user(name, path, hash_passw)
    # get_arr_name_and_img()
    print(f'Пользователь {name} добавлен в базу данных!')

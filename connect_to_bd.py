# -*- coding: utf-8 -*-
import datetime

import pymysql


host = '89.108.98.131'
# host = '89.108.115.144'
# user_ = 'mysqladmin'
user_ = 'egor'
# passwd = 'seing3Jooghi'
passwd = '555555'
database = 'paszi'
# name_table = 'name'
name_table = 'users'

def connect_bd():
    print(host)
    db = pymysql.connect(
        host=host,
        user=user_,
        passwd=passwd,
        database=database,
    )

    cursor = db.cursor()  # cursor created
    return db, cursor


def add_one_track(name, place):
    """Добавляем в БД запись о передвижении человека"""
    db, cursor = connect_bd()  # Подключение к БД
    sql = f"INSERT INTO tracker (name, place) VALUES (%s, %s)"
    val = (name, place)
    cursor.execute(sql, val)
    db.commit()
    db.close()


def update_last_access(name):
    """Обновляем последний доступ человека"""
    time_now_utc = datetime.datetime.utcnow()

    print(f'Пользователь {name} последнее распознование: {time_now_utc} (UTC)')

    db, cursor = connect_bd()  # Подключение к БД

    sql = f"UPDATE {name_table} SET last_access=%s WHERE name=%s"
    val = (time_now_utc, name)

    cursor.execute(sql, val)

    db.commit()
    db.close()


def get_arr_name_and_img():
    """Получаем изображение из БД"""
    db, cursor = connect_bd()  # Подключение к БД
    sql = f"SELECT name, img FROM {name_table}"
    cursor.execute(sql, )
    arr_name_and_img = cursor.fetchall()
    # print(name, blob)

    db.close()
    # img = pickle.loads(blob)

    # # display image until any key is pressed
    # cv2.imshow('image', img)
    # print('Press any key..')
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    #
    # exit()
    print(f'Пользователей в БД: {len(arr_name_and_img)}')
    return arr_name_and_img


if __name__ == '__main__':
    connect_bd()
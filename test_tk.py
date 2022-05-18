
# импортируем библиотеку tkinter всю сразу
import datetime
from tkinter import *
from tkinter import messagebox

# главное окно приложения
import bcrypt

from connect_to_bd import connect_bd

# Время, в течении которого пользователь может войти в свою учетную запись после распознования лица (min)
DELTA_ACCESS = 5

window = Tk()
# заголовок окна
window.title('Авторизация')
# размер окна
window.geometry('450x230')
# можно ли изменять размер окна - нет
window.resizable(False, False)

# кортежи и словари, содержащие настройки шрифтов и отступов
font_header = ('Arial', 15)
font_entry = ('Arial', 12)
label_font = ('Arial', 11)
base_padding = {'padx': 10, 'pady': 8}
header_padding = {'padx': 10, 'pady': 12}




def check_user(name, password):
    db, cursor = connect_bd()  # Подключение к БД

    sql = f"SELECT last_access, password_hash FROM users WHERE name=%s"
    val = (name, )
    cursor.execute(sql, val)
    result = cursor.fetchone()

    db.close()

    now = datetime.datetime.utcnow()

    if result:
        print(f'Пользователь {name} найден в БД')
        last_access, password_hash = result

        # Пользователь недавно был распознан камерой, поэтому он может войти в учетную запись
        if now - last_access < datetime.timedelta(minutes=DELTA_ACCESS):
            print(f'now: {now}, last_access: {last_access} - пользователь в помещении')

            valid = bcrypt.checkpw(password.encode(), password_hash.encode('utf-8'))

            # Правильный пароль
            if valid:
                print('Верный пароль')
                return f'Вы успешно вошли в систему {name}!'

            # Неверный пароль
            else:
                print('Неверный пароль')
                return 'Неверный пароль!!!'

        # Данный пользователь не находится в помещении
        else:
            print(f'now: {now}, last_access: {last_access} - пользователь не в помещении')

            return 'Данный пользователь не находится в помещении'

    else:
        print(f'Пользователь {name} не найден в БД')
        return 'Пользователь не найден'




# обработчик нажатия на клавишу 'Войти'
def clicked():

    # получаем имя пользователя и пароль
    name = name_entry.get()
    password = password_entry.get()

    # Проверяем правильность данных и права доступа
    text = check_user(name, password)

    # выводим в диалоговое окно результат проверки
    messagebox.showinfo('Заголовок', text)


# заголовок формы: настроены шрифт (font), отцентрирован (justify), добавлены отступы для заголовка
# для всех остальных виджетов настройки делаются также
main_label = Label(window, text='Авторизация', font=font_header, justify=CENTER, **header_padding)
# помещаем виджет в окно по принципу один виджет под другим
main_label.pack()

# метка для поля ввода имени
name_label = Label(window, text='Имя пользователя', font=label_font , **base_padding)
name_label.pack()

# поле ввода имени
name_entry = Entry(window, bg='#fff', fg='#444', font=font_entry)
name_entry.pack()

# метка для поля ввода пароля
password_label = Label(window, text='Пароль', font=label_font , **base_padding)
password_label.pack()

# поле ввода пароля
password_entry = Entry(window, bg='#fff', fg='#444', font=font_entry, show = '*')
password_entry.pack()

# кнопка отправки формы
send_btn = Button(window, text='Войти', command=clicked)
send_btn.pack(**base_padding)


# запускаем главный цикл окна
window.mainloop()

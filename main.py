import random
import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem
from PyQt6.uic import loadUi

from admin_window import Ui_AdminWindow
from login_window import Ui_LoginWindow
from student_window import Ui_StudentWindow
from teacher_window import Ui_InstructorWindow


class Storage():
    def __init__(self):
        self.user_id = None

    def set_id(self, user_id):
        self.user_id = user_id

    def get_id(self):
        return self.user_id


conn = sqlite3.connect("database.db")
cursor = conn.cursor()
storage = Storage()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)

        self.ui.pushButtonLogin.clicked.connect(self.login)

    def login(self):

        username = self.ui.lineEditLogin.text()
        password = self.ui.lineEditPassword.text()

        conn = None

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            cursor.execute('''
            SELECT user_id, role FROM users WHERE username = ? AND password = ?;
            ''', (username, password))
            result = cursor.fetchone()

            if result:
                user_id, role = result

                storage.set_id(user_id)

                if role == "student":
                    QMessageBox.information(self, "Успешно", f"Вы вошли как {role}.")
                    self.open_student_window()
                if role == "instructor":
                    QMessageBox.information(self, "Успешно", f"Вы вошли как {role}.")
                    self.open_instructor_window()
                if role == "admin":
                    QMessageBox.information(self, "Успешно", f"Вы вошли как {role}.")
                    self.open_admin_window()
            else:
                QMessageBox.critical(self, "Ошибка", "Неправильный логин или пароль.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при подключении к базе данных: {e}")
        finally:
            if conn:
                conn.close()

    def open_student_window(self):

        self.student_window = StudentWindow()
        self.student_window.show()
        self.close()

    def open_instructor_window(self):

        self.instructor_window = InstructorWindow()
        self.instructor_window.show()
        self.close()

    def open_admin_window(self):

        self.admin_window = AdminWindow()
        self.admin_window.show()
        self.close()


class InstructorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_InstructorWindow()
        self.ui.setupUi(self)

        self.ui.pushButtonCourses.clicked.connect(self.show_courses)
        self.ui.pushButtonAddCourse.clicked.connect(self.add_course)
        self.ui.pushButtonChapters.clicked.connect(self.show_chapters)
        self.ui.comboBoxCourses.currentIndexChanged.connect(self.load_chapters)
        self.ui.pushButtonAddChapter.clicked.connect(self.add_chapter)
        self.ui.pushButtonGrades.clicked.connect(self.show_grades)
        self.ui.pushButtonGrade.clicked.connect(self.add_grade)
        self.ui.pushButtonBack.clicked.connect(self.go_back_to_login)
        self.ui.comboBoxCourse.currentIndexChanged.connect(self.load_students)

        self.show_courses()

    def show_courses(self):

        self.ui.stackedWidget.setCurrentIndex(0)

        self.ui.listWidgetCourses.clear()

        try:

            instructor_id = storage.get_id()

            cursor.execute('''
            SELECT course_name, course_description
            FROM courses
            WHERE instructor_id = ?;
            ''', (instructor_id,))

            courses = cursor.fetchall()
            for course_name, course_description in courses:
                item = QListWidgetItem(f"{course_name}: {course_description}")
                self.ui.listWidgetCourses.addItem(item)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки курсов: {e}")

    def add_course(self):

        course_name = self.ui.lineEditCourseName.text().strip()
        course_description = self.ui.plainTextEditCourseDescription.toPlainText().strip()

        if not course_name or not course_description:
            QMessageBox.warning(self, "Ошибка", "Введите название и описание курса.")
            return

        try:

            instructor_id = storage.get_id()

            cursor.execute('''
            INSERT INTO courses (course_name, course_description, instructor_id)
            VALUES (?, ?, ?);
            ''', (course_name, course_description, instructor_id))

            conn.commit()

            QMessageBox.information(self, "Успешно", "Курс успешно добавлен.")
            self.show_courses()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления курса: {e}")

    def show_chapters(self):

        self.ui.stackedWidget.setCurrentIndex(1)

        self.ui.comboBoxCourses.clear()
        self.ui.comboBoxCourses.addItem("--", None)

        try:

            instructor_id = storage.get_id()

            cursor.execute('''
            SELECT course_id, course_name
            FROM courses
            WHERE instructor_id = ?;
            ''', (instructor_id,))

            courses = cursor.fetchall()
            for course_id, course_name in courses:
                self.ui.comboBoxCourses.addItem(course_name, course_id)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки курсов: {e}")

    def load_chapters(self):

        course_id = self.ui.comboBoxCourses.currentData()
        if not course_id:
            self.ui.listWidgetChapters.clear()
            return

        self.ui.listWidgetChapters.clear()

        try:

            cursor.execute('''
            SELECT chapter_title
            FROM course_chapters
            WHERE course_id = ?;
            ''', (course_id,))

            chapters = cursor.fetchall()
            for chapter_title, in chapters:
                self.ui.listWidgetChapters.addItem(chapter_title)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки глав: {e}")

    def add_chapter(self):

        course_id = self.ui.comboBoxCourses.currentData()
        if not course_id:
            QMessageBox.warning(self, "Ошибка", "Выберите курс для добавления главы.")
            return

        chapter_title = self.ui.lineEditChapter.text().strip()
        chapter_content = self.ui.plainTextEditChapter.toPlainText().strip()

        if not chapter_title or not chapter_content:
            QMessageBox.warning(self, "Ошибка", "Введите название и содержание главы.")
            return

        try:

            cursor.execute('''
            INSERT INTO course_chapters (course_id, chapter_title, chapter_content)
            VALUES (?, ?, ?);
            ''', (course_id, chapter_title, chapter_content))

            conn.commit()

            QMessageBox.information(self, "Успешно", "Глава успешно добавлена.")
            self.load_chapters()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления главы: {e}")

    def load_students(self):

        course_id = self.ui.comboBoxCourse.currentData()
        if not course_id:
            self.ui.comboBoxStudent.clear()
            self.ui.comboBoxStudent.addItem("--", None)
            return

        self.ui.comboBoxStudent.clear()
        self.ui.comboBoxStudent.addItem("--", None)

        try:

            cursor.execute('''
            SELECT s.user_id, s.username
            FROM users s
            JOIN course_enrollments ce ON s.user_id = ce.student_id
            WHERE ce.course_id = ?;
            ''', (course_id,))

            students = cursor.fetchall()
            for student_id, username in students:
                self.ui.comboBoxStudent.addItem(username, student_id)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки студентов: {e}")

    def show_grades(self):

        self.ui.stackedWidget.setCurrentIndex(2)

        self.ui.comboBoxCourse.clear()
        self.ui.comboBoxCourse.addItem("--", None)

        try:

            instructor_id = storage.get_id()

            cursor.execute('''
            SELECT course_id, course_name
            FROM courses
            WHERE instructor_id = ?;
            ''', (instructor_id,))

            courses = cursor.fetchall()
            for course_id, course_name in courses:
                self.ui.comboBoxCourse.addItem(course_name, course_id)
            self.load_students()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки курсов: {e}")

    def add_grade(self):

        course_id = self.ui.comboBoxCourse.currentData()
        student_id = self.ui.comboBoxStudent.currentData()
        grade = self.ui.spinBoxGrade.value()

        if not course_id or not student_id:
            QMessageBox.warning(self, "Ошибка", "Выберите курс и студента для оценки.")
            return

        try:

            cursor.execute('''
            INSERT INTO grades (student_id, course_id, grade)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, course_id) DO UPDATE SET grade = excluded.grade;
            ''', (student_id, course_id, grade))

            conn.commit()
            QMessageBox.information(self, "Успешно", "Оценка успешно добавлена.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления оценки: {e}")

    def go_back_to_login(self):

        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()


class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AdminWindow()
        self.ui.setupUi(self)

        self.ui.pushButtonAdd.clicked.connect(self.add_user)
        self.ui.pushButtonBack.clicked.connect(self.go_back_to_login)

        self.populate_roles()

    def populate_roles(self):

        self.ui.comboBoxRole.clear()
        self.ui.comboBoxRole.addItem("--")
        self.ui.comboBoxRole.addItem("instructor")
        self.ui.comboBoxRole.addItem("student")

    def add_user(self):

        username = self.ui.lineEditLogin.text().strip()
        password = self.ui.lineEditPass.text().strip()
        role = self.ui.comboBoxRole.currentText()

        if not username or not password or role == '--':
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:

            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?);
            ''', (username, password, role))

            conn.commit()

            QMessageBox.information(self, "Успешно", "Пользователь успешно добавлен.")

            self.ui.lineEditLogin.clear()
            self.ui.lineEditPass.clear()
            self.ui.comboBoxRole.setCurrentIndex(0)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления пользователя: {e}")

    def go_back_to_login(self):

        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()


class StudentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_StudentWindow()
        self.ui.setupUi(self)

        self.ui.pushButtonCourses.clicked.connect(self.show_courses)
        self.ui.pushButtonGrades.clicked.connect(self.show_grades)
        self.ui.pushButtonBack.clicked.connect(self.open_login_window)

        self.show_courses()

    def show_courses(self):

        self.ui.stackedWidget.setCurrentIndex(0)

        self.ui.listWidget.clear()

        try:

            cursor.execute('''
            SELECT courses.course_id, courses.course_name, users.username 
            FROM courses
            JOIN users ON courses.instructor_id = users.user_id;
            ''')

            courses = cursor.fetchall()
            for course_id, course_name, instructor_username in courses:
                item = QListWidgetItem(f"{course_name} (Преподаватель: {instructor_username})")
                item.setData(1, course_id)
                self.ui.listWidget.addItem(item)

            self.ui.listWidget.itemClicked.connect(self.display_course_chapters)

        except sqlite3.Error as e:
            self.ui.textBrowser.setText(f"Ошибка загрузки курсов: {e}")

    def display_course_chapters(self, item):

        course_id = item.data(1)

        try:

            cursor.execute('''
            SELECT chapter_title, chapter_content 
            FROM course_chapters 
            WHERE course_id = ?;
            ''', (course_id,))

            chapters = cursor.fetchall()

            self.ui.textBrowser.clear()
            for chapter_title, chapter_content in chapters:
                self.ui.textBrowser.append(f"Глава: {chapter_title}\n")
                self.ui.textBrowser.append(f"{chapter_content}\n")
                self.ui.textBrowser.append("-" * 40)

        except sqlite3.Error as e:
            self.ui.textBrowser.setText(f"Ошибка загрузки глав курса: {e}")

    def show_grades(self):

        self.ui.stackedWidget.setCurrentIndex(1)

        try:

            student_id = storage.get_id()

            cursor.execute('''
            SELECT courses.course_name, grades.grade
            FROM grades
            JOIN courses ON grades.course_id = courses.course_id
            WHERE grades.student_id = ?;
            ''', (student_id,))

            grades = cursor.fetchall()

            self.ui.textBrowser_2.clear()
            for course_name, grade in grades:
                self.ui.textBrowser_2.append(f"Курс: {course_name}, Оценка: {grade}")

        except sqlite3.Error as e:
            self.ui.textBrowser_2.setText(f"Ошибка загрузки оценок: {e}")

    def open_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())

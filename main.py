import typing
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # WINDOW DETAILS
        self.setWindowTitle("Student Management System")
        # self.setFixedSize(600, 500)

        # Add Menu Bar
        self.file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        self.edit_menu_item = self.menuBar().addMenu("&Edit")

        # SUB-ITEMS
        # File
        add_student_action = QAction("Add Student", self)
        add_student_action.triggered.connect(self.insert)
        self.file_menu_item.addAction(add_student_action)

        # Help
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        # only add if on mac
        about_action.setMenuRole(QAction.MenuRole.NoRole)

        # Edit
        search_action = QAction("Search", self)
        self.edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # CENTRAL TABLE WIDGET
        # instantiate table class
        self.table = QTableWidget()

        # set column count
        self.table.setColumnCount(4)

        # set table headings
        self.table.setHorizontalHeaderLabels(
            ("ID", "Name", "Course", "Mobile"))

        # remove index col
        self.table.verticalHeader().setVisible(False)

        # set table as central widget of the main window
        self.setCentralWidget(self.table)

    def load_data(self):
        # establist connection to the db
        connection = sqlite3.connect("database.db")

        # run query on the database
        result = connection.execute("SELECT * FROM students")

        # ensures no duplicate data on reload
        self.table.setRowCount(0)

        # populate table with data from db
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(data)))

        connection.close()

    def insert(self):
        # displays dialogue box on screen as a pop up window
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()


class InsertDialog(QDialog):
    """Dialog class for component-like rendering"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedSize(300, 300)

        # initialize layout container
        layout = QVBoxLayout()

        # ADD STUDENT DIALOG BOX

        # Student Name Widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # Course Selection Widget
        self.course_name = QComboBox()
        courses = ["Biology", "Chemistry", "Physics", "Math"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Phone number Widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText('Mobile Number')
        layout.addWidget(self.mobile)

        # Submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        # show layout + widgets
        self.setLayout(layout)

    def add_student(self):

        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)", (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set Window title and size
        self.setWindowTitle("Search Student")
        self.setFixedSize(300, 300)

        # instantiate layout container
        layout = QVBoxLayout()

        # Widgets
        # Name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Button
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search)
        layout.addWidget(self.search_btn)

        # display dialog
        self.setLayout(layout)

    def search(self):
        # Get student name from search
        name = self.student_name.text()

        # Query DB for data
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute(
            "SELECT * FROM students WHERE name = ?", (name,))

        # Parse data
        # row = list(result)[0]
        items = main_window.table.findItems(
            name, Qt.MatchFlag.MatchFixedString)

        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        # Close DB connection
        cursor.close()
        connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()
    main_window.load_data()
    sys.exit(app.exec())

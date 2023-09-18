import typing
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import sys
import sqlite3

from PyQt6.QtWidgets import QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # WINDOW DETAILS
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

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

        # MENU BAR
        # Add Menu Bar
        self.file_menu_item = self.menuBar().addMenu("&File")
        self.edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        # File
        add_student_action = QAction(
            QIcon('icons/add.png'), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        self.file_menu_item.addAction(add_student_action)

        # Help
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        # only add if on mac
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        # Edit
        search_action = QAction(QIcon('icons/search.png'), "Search", self)
        self.edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # TOOLBAR
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        # add functionality using previously set actions
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # STATUS BAR
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Detect cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        # Edit Button
        edit_btn = QPushButton('Edit Record')
        edit_btn.clicked.connect(self.click_edit_btn)

        # Delete Button
        delete_btn = QPushButton('Delete Record')
        delete_btn.clicked.connect(self.click_delete_btn)

        # Checks for existing edit/delete btns and clears them
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        # Add buttons to status bar on cell click
        self.status_bar.addWidget(edit_btn)
        self.status_bar.addWidget(delete_btn)

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

    def click_edit_btn(self):
        dialog = EditDialog()
        dialog.exec()

    def click_delete_btn(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
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
        courses = ["Biology", "Chemistry", "Physics", "Math", "Astronomy"]
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
        self.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set Window title and size
        self.setWindowTitle("Search Student")
        self.setFixedSize(400, 200)

        # instantiate layout container
        layout = QVBoxLayout()

        # Widgets
        # Name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Label
        warning_text = """
        Please type the student's name exactly as in the table. 
        (e.g John Smith)
        """
        warning_label = QLabel(warning_text)
        layout.addWidget(warning_label)

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
            main_window.table.item(item.row(), 0).setSelected(True)
            main_window.table.item(item.row(), 1).setSelected(True)
            main_window.table.item(item.row(), 2).setSelected(True)
            main_window.table.item(item.row(), 3).setSelected(True)

        # Close DB connection
        cursor.close()
        connection.close()

        # Close window
        self.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.setWindowTitle("Edit Student Record")
        self.setFixedSize(300, 300)

        # initialize layout container
        layout = QVBoxLayout()

        # ADD STUDENT DIALOG BOX

        # Get Index from Selected Row
        index = main_window.table.currentRow()
        self.student_id = main_window.table.item(index, 0).text()

        # Student Name Widget
        # Get student name from cell based on selected row index
        name = main_window.table.item(index, 1).text()

        self.student_name = QLineEdit(name)
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # Course Selection Widget
        # Get student course from cell based on selected row index
        course = main_window.table.item(index, 2).text()

        self.course_name = QComboBox()
        courses = ["Biology", "Chemistry", "Physics", "Math", "Astronomy"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course)
        layout.addWidget(self.course_name)

        # Phone number Widget

        # Get studen mobile from cell based on selected row index
        mobile = main_window.table.item(index, 3).text()

        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText('Mobile Number')
        layout.addWidget(self.mobile)

        # Submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        # show layout + widgets
        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
            (self.student_name.text(),
             self.course_name.itemText(self.course_name.currentIndex()),
             self.mobile.text(),
             self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set Window title and size
        self.setWindowTitle('Delete Record')

        # Set container layout
        layout = QGridLayout()

        # Widgets
        confirmation = QLabel("Are you sure you want to delete?")
        yes_button = QPushButton('Yes')
        no_button = QPushButton('No')

        # Add widgets to layout
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 1)
        self.setLayout(layout)

        # Button functionality
        yes_button.clicked.connect(self.delete_record)
        no_button.clicked.connect(self.close)

    def delete_record(self):
        # Get record id for SQL query
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        # Delete record from database with SQL query
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id,))

        # Commit changes and close connections to db
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        # Close current window after functionality completed
        # and display success msg
        self.close()
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText('The record was successfully deleted!')
        confirmation_widget.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About")

        content = """
        A simple cross-platform GUI built with Python's PyQt6 library, following Ardit Sulce's instruction.

        Feel free to use and edit as you see fit. 

        """
        self.setText(content)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()
    main_window.load_data()
    sys.exit(app.exec())

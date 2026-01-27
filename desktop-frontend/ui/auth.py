import requests
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt

from config import API_URL
from ui.dashboard import MainWindow

class AuthWindow(QMainWindow):
    def __init__(self, stylesheet):
        super().__init__()
        self.setWindowTitle("Welcome - ChemData Visualizer")
        self.resize(1000, 700)
        self.setStyleSheet(stylesheet)
        
        # Main Container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- LEFT SIDE: FORM ---
        self.left_widget = QWidget()
        self.left_widget.setStyleSheet("background-color: white;")
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Form Container (to center it nicely)
        form_container = QWidget()
        form_container.setFixedWidth(360)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        
        # Logo
        lbl_logo = QLabel("C")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setFixedSize(60, 60)
        lbl_logo.setStyleSheet("background-color: #0d9488; color: white; font-size: 30px; font-weight: bold; border-radius: 10px;")
        form_layout.addWidget(lbl_logo)
        
        # Title
        self.lbl_title = QLabel("Welcome Back!")
        self.lbl_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #111827; margin-top: 10px;")
        form_layout.addWidget(self.lbl_title)
        
        self.lbl_subtitle = QLabel("Please enter your details.")
        self.lbl_subtitle.setStyleSheet("font-size: 14px; color: #6b7280; margin-bottom: 10px;")
        form_layout.addWidget(self.lbl_subtitle)
        
        # Inputs
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Username")
        self.txt_username.setFixedHeight(45)
        form_layout.addWidget(self.txt_username)
        
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Email Address (for Signup)")
        self.txt_email.setFixedHeight(45)
        self.txt_email.hide() # Hidden by default (Login mode)
        form_layout.addWidget(self.txt_email)
        
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Password")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setFixedHeight(45)
        form_layout.addWidget(self.txt_password)

        self.txt_confirm = QLineEdit()
        self.txt_confirm.setPlaceholderText("Confirm Password")
        self.txt_confirm.setEchoMode(QLineEdit.Password)
        self.txt_confirm.setFixedHeight(45)
        self.txt_confirm.hide()
        form_layout.addWidget(self.txt_confirm)
        
        # Connect Enter key to submit
        self.txt_username.returnPressed.connect(self.handle_action)
        self.txt_password.returnPressed.connect(self.handle_action)
        self.txt_email.returnPressed.connect(self.handle_action)
        self.txt_confirm.returnPressed.connect(self.handle_action)

        # Action Button
        self.btn_action = QPushButton("Sign In")
        self.btn_action.setFixedHeight(45)
        self.btn_action.setCursor(Qt.PointingHandCursor)
        self.btn_action.clicked.connect(self.handle_action)
        form_layout.addWidget(self.btn_action)
        
        # Toggle Mode
        self.btn_toggle = QPushButton("Don't have an account? Sign Up")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setStyleSheet("background: none; color: #0d9488; border: none; font-weight: normal;")
        self.btn_toggle.clicked.connect(self.toggle_mode)
        form_layout.addWidget(self.btn_toggle)
        
        left_layout.addWidget(form_container)
        main_layout.addWidget(self.left_widget, 4) # 40% width
        
        # --- RIGHT SIDE: VISUALS ---
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background-color: #f3f4f6;
                border-left: 1px solid #e5e7eb;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Visual Content
        lbl_visual_title = QLabel("Monitor Chemical Parameters\nin Real-Time")
        lbl_visual_title.setAlignment(Qt.AlignCenter)
        lbl_visual_title.setStyleSheet("font-size: 32px; font-weight: bold; color: #111827; background: transparent;")
        right_layout.addWidget(lbl_visual_title)
        
        lbl_visual_desc = QLabel("Track flowrates, pressure, and temperature\nwith advanced visualization.")
        lbl_visual_desc.setAlignment(Qt.AlignCenter)
        lbl_visual_desc.setStyleSheet("font-size: 16px; color: #6b7280; background: transparent; margin-top: 20px;")
        right_layout.addWidget(lbl_visual_desc)
        
        # Mockup Card
        card = QFrame()
        card.setFixedSize(400, 250)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
            }
        """)
        card_layout = QVBoxLayout(card)
        
        lbl_card_head = QLabel("Overview")
        lbl_card_head.setStyleSheet("font-weight: bold; font-size: 16px; border: none;")
        card_layout.addWidget(lbl_card_head)
        
        metrics_layout = QHBoxLayout()
        m1 = QLabel("Flowrate\n120.5 ↑")
        m1.setStyleSheet("background: #f9fafb; padding: 10px; border-radius: 8px; color: #111827; border: none;")
        m2 = QLabel("Pressure\n15.2 ↓")
        m2.setStyleSheet("background: #f9fafb; padding: 10px; border-radius: 8px; color: #111827; border: none;")
        metrics_layout.addWidget(m1)
        metrics_layout.addWidget(m2)
        card_layout.addLayout(metrics_layout)
        
        # Mock bars
        bars_layout = QHBoxLayout()
        for h in [40, 70, 50, 85, 60]:
            bar = QFrame()
            bar.setStyleSheet(f"background-color: #0d9488; border-radius: 4px; min-height: {h}px;")
            bars_layout.addWidget(bar)
        card_layout.addLayout(bars_layout)
        
        right_layout.addSpacing(40)
        right_layout.addWidget(card)
        
        main_layout.addWidget(right_widget, 6) # 60% width
        
        self.is_login_mode = True

    def toggle_mode(self):
        self.is_login_mode = not self.is_login_mode
        if self.is_login_mode:
            self.lbl_title.setText("Welcome Back!")
            self.txt_email.hide()
            self.txt_confirm.hide()
            self.btn_action.setText("Sign In")
            self.btn_toggle.setText("Don't have an account? Sign Up")
        else:
            self.lbl_title.setText("Create Account")
            self.txt_email.show()
            self.txt_confirm.show()
            self.btn_action.setText("Sign Up")
            self.btn_toggle.setText("Already have an account? Sign In")

    def handle_action(self):
        username = self.txt_username.text()
        password = self.txt_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        if self.is_login_mode:
            self.login(username, password)
        else:
            email = self.txt_email.text()
            confirm = self.txt_confirm.text()
            if password != confirm:
                QMessageBox.warning(self, "Error", "Passwords do not match")
                return
            self.signup(username, email, password, confirm)

    def login(self, username, password):
        try:
            resp = requests.post(API_URL + "api-token-auth/", data={'username': username, 'password': password})
            if resp.status_code == 200:
                token = resp.json()['token']
                self.open_dashboard(token)
            else:
                QMessageBox.warning(self, "Failed", "Invalid credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def signup(self, username, email, password, confirm):
        try:
            # Matches the django-rest-auth registration payload we fixed earlier
            data = {
                'username': username, 
                'email': email, 
                'password1': password, 
                'password2': confirm
            }
            resp = requests.post(API_URL + "auth/registration/", data=data)
            if resp.status_code in [200, 201]:
                data = resp.json()
                if 'key' in data:
                    self.open_dashboard(data['key'])
                else:
                    QMessageBox.information(self, "Success", "Account created! Please log in.")
                    self.toggle_mode()
            else:
                QMessageBox.warning(self, "Error", f"Signup failed: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_dashboard(self, token):
        self.main_window = MainWindow(token)
        self.main_window.show()
        self.close()

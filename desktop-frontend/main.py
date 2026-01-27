import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QFileDialog, QTabWidget, QMessageBox, QListWidget, QListWidgetItem,
                             QFrame, QSplitter, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000/api/"

# --- MODERN STYLESHEET ---
STYLESHEET = """
QMainWindow {
    background-color: #f3f4f6;
}
QWidget {
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    color: #1f2937;
}
QLineEdit {
    padding: 10px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background-color: white;
    selection-background-color: #6366f1;
}
QLineEdit:focus {
    border: 2px solid #6366f1;
}
QPushButton {
    background-color: #6366f1;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #4f46e5;
}
QPushButton#secondary {
    background-color: white;
    color: #4b5563;
    border: 1px solid #d1d5db;
}
QPushButton#secondary:hover {
    background-color: #f9fafb;
    color: #111827;
}
QListWidget {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 5px;
    background-color: white;
    outline: none;
}
QListWidget::item {
    padding: 10px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #e0e7ff;
    color: #4338ca;
}
QTableWidget {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background-color: white;
    gridline-color: #f3f4f6;
}
QHeaderView::section {
    background-color: #f9fafb;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #e5e7eb;
    font-weight: bold;
    color: #6b7280;
}
QTabWidget::pane {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background: white;
    top: -1px; 
}
QTabBar::tab {
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    padding: 10px 20px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #6b7280;
}
QTabBar::tab:selected {
    background: white;
    color: #6366f1;
    font-weight: bold;
    border-bottom: 2px solid white; 
}
QLabel#Heading {
    font-size: 24px;
    font-weight: bold;
    color: #111827;
}
QLabel#SubHeading {
    font-size: 16px;
    color: #6b7280;
    margin-bottom: 15px;
}
QFrame#Card {
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}
"""

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome - ChemData Visualizer")
        self.resize(1000, 700)
        self.setStyleSheet(STYLESHEET)
        
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
        lbl_logo.setStyleSheet("background-color: #4f46e5; color: white; font-size: 30px; font-weight: bold; border-radius: 10px;")
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
        self.txt_confirm.returnPressed.connect(self.handle_action)
        form_layout.addWidget(self.txt_confirm)
        
        # Connect Enter key to submit
        self.txt_username.returnPressed.connect(self.handle_action)
        self.txt_password.returnPressed.connect(self.handle_action)
        self.txt_email.returnPressed.connect(self.handle_action)
        
        # Action Button
        self.btn_action = QPushButton("Sign In")
        self.btn_action.setFixedHeight(45)
        self.btn_action.setCursor(Qt.PointingHandCursor)
        self.btn_action.clicked.connect(self.handle_action)
        form_layout.addWidget(self.btn_action)
        
        # Toggle Mode
        self.btn_toggle = QPushButton("Don't have an account? Sign Up")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setStyleSheet("background: none; color: #4f46e5; border: none; font-weight: normal;")
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
            bar.setStyleSheet(f"background-color: #6366f1; border-radius: 4px; min-height: {h}px;")
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
                # Most dj-rest-auth configs return key on signup, if not prompt login
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

class MainWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.headers = {'Authorization': f'Token {token}'}
        self.setWindowTitle("ChemData Visualizer")
        self.resize(1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # --- LEFT SIDEBAR ---
        sidebar = QFrame()
        sidebar.setObjectName("Card")
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("#Card { background-color: white; border-right: 1px solid #e5e7eb; }")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(15)
        
        lbl_brand = QLabel("ChemViz")
        lbl_brand.setStyleSheet("font-size: 22px; font-weight: bold; color: #4338ca;")
        sidebar_layout.addWidget(lbl_brand)
        
        sidebar_layout.addSpacing(10)
        
        lbl_menu = QLabel("DATASETS")
        lbl_menu.setStyleSheet("font-size: 12px; font-weight: bold; color: #9ca3af; letter-spacing: 1px;")
        sidebar_layout.addWidget(lbl_menu)
        
        self.list_datasets = QListWidget()
        self.list_datasets.itemClicked.connect(self.load_dataset)
        sidebar_layout.addWidget(self.list_datasets)
        
        self.btn_upload = QPushButton("+ Upload New CSV")
        self.btn_upload.setObjectName("secondary")
        self.btn_upload.setCursor(Qt.PointingHandCursor)
        self.btn_upload.clicked.connect(self.upload_csv)
        sidebar_layout.addWidget(self.btn_upload)
        
        main_layout.addWidget(sidebar)
        
        # --- RIGHT CONTENT ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        self.lbl_page_title = QLabel("Dashboard")
        self.lbl_page_title.setObjectName("Heading")
        header_layout.addWidget(self.lbl_page_title)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tab_data = QWidget()
        self.tab_charts = QWidget()
        self.tab_summary = QWidget()
        
        self.tabs.addTab(self.tab_summary, "Overview")
        self.tabs.addTab(self.tab_data, "Raw Data")
        self.tabs.addTab(self.tab_charts, "Analytics")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content_area)
        
        # --- TAB: SUMMARY ---
        self.tab_summary.setLayout(QVBoxLayout())
        
        self.summary_card = QFrame()
        self.summary_card.setObjectName("Card")
        summary_inner = QVBoxLayout(self.summary_card)
        summary_inner.setContentsMargins(30, 30, 30, 30)
        
        self.lbl_stats = QLabel("Please select a dataset from the sidebar to view insights.")
        self.lbl_stats.setAlignment(Qt.AlignCenter)
        self.lbl_stats.setStyleSheet("font-size: 18px; color: #6b7280;")
        summary_inner.addWidget(self.lbl_stats)
        
        self.tab_summary.layout().addWidget(self.summary_card)
        self.tab_summary.layout().addStretch()

        # --- TAB: DATA ---
        data_layout = QVBoxLayout()
        data_layout.setContentsMargins(0, 20, 0, 0)
        
        self.table = QTableWidget()
        data_layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_pdf = QPushButton("Download Analysis PDF")
        self.btn_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.download_pdf)
        btn_layout.addWidget(self.btn_pdf)
        
        data_layout.addLayout(btn_layout)
        self.tab_data.setLayout(data_layout)

        # --- TAB: CHARTS ---
        charts_layout = QVBoxLayout()
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor('#f3f4f6') # Match bg
        self.canvas = FigureCanvas(self.figure)
        charts_layout.addWidget(self.canvas)
        self.tab_charts.setLayout(charts_layout)
        
        self.current_dataset_id = None
        self.refresh_datasets()

    def refresh_datasets(self):
        try:
            resp = requests.get(API_URL + "datasets/", headers=self.headers)
            if resp.status_code == 200:
                self.list_datasets.clear()
                data = resp.json()
                results = data.get('results', data)
                for ds in results:
                    item = QListWidgetItem(f"Dataset #{ds['id']} - {ds['uploaded_at'][:10]}")
                    item.setData(Qt.UserRole, ds['id'])
                    self.list_datasets.addItem(item)
        except Exception as e:
            print(e)

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            files = {'file': open(file_path, 'rb')}
            try:
                resp = requests.post(API_URL + "upload/", headers=self.headers, files=files)
                if resp.status_code == 201:
                    QMessageBox.information(self, "Success", "File uploaded successfully.")
                    self.refresh_datasets()
                else:
                    QMessageBox.warning(self, "Upload Failed", resp.text)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def load_dataset(self, item):
        dataset_id = str(item.data(Qt.UserRole))
        self.current_dataset_id = dataset_id
        self.lbl_page_title.setText(f"Analysis: Dataset #{dataset_id}")
        self.load_data(dataset_id)
        self.load_stats(dataset_id)

    def load_data(self, id):
        try:
            resp = requests.get(f"{API_URL}datasets/{id}/data/", headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                # Pagination disabled on backend, so it returns a list directly
                # But keep check just in case
                if isinstance(data, dict) and 'results' in data: 
                    data = data['results']
                
                self.table.setRowCount(len(data))
                self.table.setColumnCount(5)
                self.table.setHorizontalHeaderLabels(["Name", "Type", "Flowrate", "Pressure", "Temp"])
                self.table.horizontalHeader().setStretchLastSection(True)
                self.table.setAlternatingRowColors(True)
                
                for i, row in enumerate(data):
                    self.table.setItem(i, 0, QTableWidgetItem(str(row['equipment_name'])))
                    self.table.setItem(i, 1, QTableWidgetItem(str(row['equipment_type'])))
                    self.table.setItem(i, 2, QTableWidgetItem(f"{row['flowrate']:.2f}"))
                    self.table.setItem(i, 3, QTableWidgetItem(f"{row['pressure']:.2f}"))
                    self.table.setItem(i, 4, QTableWidgetItem(f"{row['temperature']:.2f}"))
        except Exception as e:
            print(f"Error loading data: {e}")

    def load_stats(self, id):
        try:
            resp = requests.get(f"{API_URL}datasets/{id}/stats/", headers=self.headers)
            if resp.status_code == 200:
                 stats = resp.json()
                 
                 # --- 1. OVERVIEW TAB: KPI DASHBOARD ---
                 
                 # Clear existing
                 layout = self.summary_card.layout()
                 while layout.count():
                     item = layout.takeAt(0)
                     if item.widget(): item.widget().deleteLater()
                 
                 # Main Grid for Overview
                 grid = QGridLayout()
                 grid.setSpacing(15)
                 
                 # Helper to create styled KPI Card
                 def create_kpi(title, value, unit, color, icon_text="📊"):
                     card = QFrame()
                     card.setStyleSheet(f"""
                        QFrame {{
                            background-color: white;
                            border-radius: 10px;
                            border: 1px solid #e5e7eb;
                            border-left: 5px solid {color};
                        }}
                        QFrame:hover {{
                            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                        }}
                     """)
                     v_layout = QVBoxLayout(card)
                     
                     lbl_title = QLabel(title)
                     lbl_title.setStyleSheet("color: #6b7280; font-size: 12px; font-weight: bold; border: none;")
                     
                     lbl_value = QLabel(f"{value}")
                     lbl_value.setStyleSheet("color: #111827; font-size: 24px; font-weight: bold; border: none;")
                     
                     lbl_unit = QLabel(unit)
                     lbl_unit.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold; border: none;")
                     
                     v_layout.addWidget(lbl_title)
                     v_layout.addWidget(lbl_value)
                     v_layout.addWidget(lbl_unit)
                     return card

                 # Add KPI Cards
                 grid.addWidget(create_kpi("TOTAL RECORDS", stats['total_count'], "Active Items", "#6366f1"), 0, 0)
                 grid.addWidget(create_kpi("AVG FLOWRATE", f"{stats['average_flowrate']:.1f}", "Liters/min", "#10b981"), 0, 1)
                 grid.addWidget(create_kpi("AVG PRESSURE", f"{stats['average_pressure']:.1f}", "PSI", "#f59e0b"), 0, 2)
                 grid.addWidget(create_kpi("AVG TEMP", f"{stats['average_temperature']:.1f}", "Celsius", "#ef4444"), 0, 3)
                 
                 # Add Pie Chart Row
                 self.summary_figure = Figure(figsize=(4, 3), dpi=100)
                 self.summary_figure.patch.set_facecolor('#f9fafb') # Light gray bg to blend
                 self.summary_canvas = FigureCanvas(self.summary_figure)
                 
                 ax = self.summary_figure.add_subplot(111)
                 types = list(stats['type_distribution'].keys())
                 counts = list(stats['type_distribution'].values())
                 wedges, texts, autotexts = ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90, 
                                                   colors=['#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe', '#e0e7ff'])
                 plt.setp(autotexts, size=8, weight="bold", color="white")
                 plt.setp(texts, size=9)
                 ax.set_title("Equipment Distribution", fontsize=12, pad=10, color="#374151")
                 
                 container_chart = QWidget()
                 container_chart.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e5e7eb;")
                 chart_layout = QVBoxLayout(container_chart)
                 chart_layout.addWidget(self.summary_canvas)
                 
                 grid.addWidget(container_chart, 1, 0, 1, 4) # Span full width
                 
                 layout.addLayout(grid)


                 # --- 2. ANALYTICS TAB: ANIMATED BAR CHART ---
                 self.figure.clear()
                 self.ax_bar = self.figure.add_subplot(111)
                 
                 self.bar_types = list(stats['type_distribution'].keys())
                 self.bar_counts = list(stats['type_distribution'].values())
                 
                 # Prepare Animation
                 self.anim_frame = 0
                 self.anim_total_frames = 25
                 self.anim_timer = QTimer()
                 self.anim_timer.timeout.connect(self.update_bar_animation)
                 self.anim_timer.start(20) # 20ms * 25 frames = 500ms duration
                 
        except Exception as e:
            print(f"Error loading stats: {e}")

    def update_bar_animation(self):
        self.anim_frame += 1
        progress = self.anim_frame / self.anim_total_frames
        
        # Ease out cubic
        progress = 1 - pow(1 - progress, 3)
        
        current_counts = [c * progress for c in self.bar_counts]
        
        self.ax_bar.clear()
        bars = self.ax_bar.bar(self.bar_types, current_counts, color='#6366f1', alpha=0.8)
        
        self.ax_bar.set_title("Equipment Frequency (Live)", fontsize=14, pad=20, color="#1f2937")
        self.ax_bar.spines['top'].set_visible(False)
        self.ax_bar.spines['right'].set_visible(False)
        self.ax_bar.spines['left'].set_color('#e5e7eb')
        self.ax_bar.spines['bottom'].set_color('#e5e7eb')
        self.ax_bar.grid(axis='y', linestyle='--', alpha=0.5, color='#e5e7eb')
        self.ax_bar.tick_params(axis='x', colors='#4b5563')
        self.ax_bar.tick_params(axis='y', colors='#4b5563')
        
        self.canvas.draw()
        
        if self.anim_frame >= self.anim_total_frames:
            self.anim_timer.stop()

    def download_pdf(self):
        if not self.current_dataset_id: return
        try:
            resp = requests.get(f"{API_URL}datasets/{self.current_dataset_id}/pdf/", headers=self.headers)
            if resp.status_code == 200:
                path, _ = QFileDialog.getSaveFileName(self, "Save Analysis Report", f"ChemViz_Report_{self.current_dataset_id}.pdf", "PDF Files (*.pdf)")
                if path:
                    with open(path, 'wb') as f:
                        f.write(resp.content)
                    QMessageBox.information(self, "Success", "PDF Report saved successfully.")
        except Exception as e:
             QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(STYLESHEET)
    
    auth_window = AuthWindow()
    auth_window.show()
    sys.exit(app.exec_())

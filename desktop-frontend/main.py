
import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QFileDialog, QTabWidget, QMessageBox, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_URL = "http://127.0.0.1:8000/api/"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - ChemData Visualizer")
        self.resize(300, 200)
        self.layout = QVBoxLayout()
        
        self.username = QLineEdit(self)
        self.username.setPlaceholderText("Username")
        self.layout.addWidget(self.username)
        
        self.password = QLineEdit(self)
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password)
        
        self.btn_login = QPushButton("Login", self)
        self.btn_login.clicked.connect(self.login)
        self.layout.addWidget(self.btn_login)
        
        self.setLayout(self.layout)

    def login(self):
        username = self.username.text()
        password = self.password.text()
        try:
            # Note: 127.0.0.1 is local, make sure server is running
            resp = requests.post(API_URL + "api-token-auth/", data={'username': username, 'password': password})
            if resp.status_code == 200:
                token = resp.json()['token']
                self.main_window = MainWindow(token)
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed: {e}")

class MainWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.headers = {'Authorization': f'Token {token}'}
        self.setWindowTitle("ChemData Visualizer")
        self.resize(1000, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        
        # Sidebar
        self.sidebar_layout = QVBoxLayout()
        self.btn_upload = QPushButton("Upload New CSV")
        self.btn_upload.clicked.connect(self.upload_csv)
        self.sidebar_layout.addWidget(self.btn_upload)
        
        self.list_datasets = QListWidget()
        self.list_datasets.itemClicked.connect(self.load_dataset)
        self.sidebar_layout.addWidget(self.list_datasets)
        
        self.layout.addLayout(self.sidebar_layout, 1)
        
        # Main Area
        self.tabs = QTabWidget()
        self.tab_data = QWidget()
        self.tab_charts = QWidget()
        self.tab_summary = QWidget()
        
        self.tabs.addTab(self.tab_data, "Data")
        self.tabs.addTab(self.tab_charts, "Charts")
        self.tabs.addTab(self.tab_summary, "Summary")
        
        self.layout.addWidget(self.tabs, 3)
        
        # Data Tab Setup
        self.data_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.data_layout.addWidget(self.table)
        self.btn_pdf = QPushButton("Download PDF")
        self.btn_pdf.clicked.connect(self.download_pdf)
        self.data_layout.addWidget(self.btn_pdf)
        self.tab_data.setLayout(self.data_layout)
        
        # Charts Tab Setup
        self.charts_layout = QVBoxLayout()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.charts_layout.addWidget(self.canvas)
        self.tab_charts.setLayout(self.charts_layout)
        
        # Summary Tab Setup
        self.summary_layout = QVBoxLayout()
        self.lbl_stats = QLabel("Select a dataset to view statistics.")
        self.summary_layout.addWidget(self.lbl_stats)
        self.tab_summary.setLayout(self.summary_layout)
        
        self.current_dataset_id = None
        self.refresh_datasets()

    def refresh_datasets(self):
        try:
            resp = requests.get(API_URL + "datasets/", headers=self.headers)
            if resp.status_code == 200:
                self.list_datasets.clear()
                data = resp.json()
                results = data.get('results', data) # Handle both pagination and list
                for ds in results:
                    # Storing ID in text is easier for now
                    self.list_datasets.addItem(f"{ds['id']}: {ds['file']}")
        except Exception as e:
            print(e)
            
    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            files = {'file': open(file_path, 'rb')}
            try:
                resp = requests.post(API_URL + "upload/", headers=self.headers, files=files)
                if resp.status_code == 201:
                    QMessageBox.information(self, "Success", "Upload successful")
                    self.refresh_datasets()
                else:
                    QMessageBox.warning(self, "Error", f"Upload failed: {resp.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def load_dataset(self, item):
        dataset_id = item.text().split(':')[0]
        self.current_dataset_id = dataset_id
        
        self.load_data(dataset_id)
        self.load_stats(dataset_id)

    def load_data(self, id):
        try:
            resp = requests.get(f"{API_URL}datasets/{id}/data/", headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                if 'results' in data: data = data['results']
                
                self.table.setRowCount(len(data))
                self.table.setColumnCount(5)
                self.table.setHorizontalHeaderLabels(["Name", "Type", "Flow", "Press", "Temp"])
                
                for i, row in enumerate(data):
                    self.table.setItem(i, 0, QTableWidgetItem(str(row['equipment_name'])))
                    self.table.setItem(i, 1, QTableWidgetItem(str(row['equipment_type'])))
                    self.table.setItem(i, 2, QTableWidgetItem(str(row['flowrate'])))
                    self.table.setItem(i, 3, QTableWidgetItem(str(row['pressure'])))
                    self.table.setItem(i, 4, QTableWidgetItem(str(row['temperature'])))
        except Exception as e:
            print(e)

    def load_stats(self, id):
        try:
            resp = requests.get(f"{API_URL}datasets/{id}/stats/", headers=self.headers)
            if resp.status_code == 200:
                 stats = resp.json()
                 text = f"Total Count: {stats['total_count']}\n" \
                        f"Avg Flow: {stats['average_flowrate']}\n" \
                        f"Avg Press: {stats['average_pressure']}\n" \
                        f"Avg Temp: {stats['average_temperature']}"
                 self.lbl_stats.setText(text)
                 
                 self.figure.clear()
                 ax = self.figure.add_subplot(111)
                 types = list(stats['type_distribution'].keys())
                 counts = list(stats['type_distribution'].values())
                 ax.bar(types, counts)
                 ax.set_title("Equipment Type Distribution")
                 self.canvas.draw()
        except Exception as e:
            print(e)
            
    def download_pdf(self):
        if not self.current_dataset_id: return
        try:
            resp = requests.get(f"{API_URL}datasets/{self.current_dataset_id}/pdf/", headers=self.headers)
            if resp.status_code == 200:
                path, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"report_{self.current_dataset_id}.pdf", "PDF Files (*.pdf)")
                if path:
                    with open(path, 'wb') as f:
                        f.write(resp.content)
                    QMessageBox.information(self, "Success", "PDF Saved")
        except Exception as e:
             QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())

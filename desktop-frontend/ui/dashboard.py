import requests
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
                             QFileDialog, QTabWidget, QMessageBox, QListWidget, QListWidgetItem,
                             QFrame, QGridLayout, QHeaderView, QAbstractItemView, QStackedWidget, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from config import API_URL

class MainWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.headers = {'Authorization': f'Token {token}'}
        self.setWindowTitle("ChemViz Desktop")
        self.resize(1300, 850)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- LEFT SIDEBAR ---
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet("background-color: white; border-right: 1px solid #e2e8f0;")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(24, 32, 24, 24)
        sidebar_layout.setSpacing(16)
        
        # Brand
        lbl_brand = QLabel("ChemViz")
        lbl_brand.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")
        sidebar_layout.addWidget(lbl_brand)
        
        sidebar_layout.addSpacing(20)
        
        # Menu Group
        lbl_menu = QLabel("MY DATASETS")
        lbl_menu.setStyleSheet("font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 1.2px;")
        sidebar_layout.addWidget(lbl_menu)
        
        self.list_datasets = QListWidget()
        self.list_datasets.setCursor(Qt.PointingHandCursor)
        self.list_datasets.itemClicked.connect(self.load_dataset)
        sidebar_layout.addWidget(self.list_datasets)
        
        # Upload Button
        self.btn_upload = QPushButton("Upload New CSV")
        self.btn_upload.setCursor(Qt.PointingHandCursor)
        self.btn_upload.clicked.connect(self.upload_csv)
        sidebar_layout.addWidget(self.btn_upload)

        # Logout Link (Bottom)
        sidebar_layout.addStretch()
        lbl_user = QLabel("Logged In")
        lbl_user.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600;")
        sidebar_layout.addWidget(lbl_user)
        
        main_layout.addWidget(sidebar)
        
        # --- RIGHT CONTENT ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        self.lbl_page_title = QLabel("Dashboard Overview")
        self.lbl_page_title.setObjectName("Heading")
        header_layout.addWidget(self.lbl_page_title)
        
        self.btn_pdf = QPushButton("Export Report")
        self.btn_pdf.setObjectName("secondary")
        self.btn_pdf.setFixedWidth(140)
        self.btn_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.download_pdf)
        self.btn_pdf.setVisible(False)
        header_layout.addWidget(self.btn_pdf)
        
        content_layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tab_summary = QWidget()
        self.tab_data = QWidget()
        
        self.tabs.addTab(self.tab_summary, "Analysis Dashboard")
        self.tabs.addTab(self.tab_data, "Data Logs")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content_area)
        
        # --- TAB: DASHBOARD (Updated with QStackedWidget) ---
        self.tab_summary.setLayout(QVBoxLayout())
        self.tab_summary.layout().setContentsMargins(0, 0, 0, 0) # Zero margins for stack
        
        self.content_stack = QStackedWidget()
        self.tab_summary.layout().addWidget(self.content_stack)
        
        # PAGE 0: Empty State
        self.page_empty = QWidget()
        empty_layout = QVBoxLayout(self.page_empty)
        empty_layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_empty = QLabel("Select a dataset to view analytics")
        self.lbl_empty.setStyleSheet("font-size: 16px; color: #94a3b8;")
        empty_layout.addWidget(self.lbl_empty)
        
        self.content_stack.addWidget(self.page_empty)
        
        # PAGE 1: Dashboard Stats
        self.page_stats = QWidget()
        stats_layout_container = QVBoxLayout(self.page_stats)
        stats_layout_container.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area for Stats
        self.summary_scroll = QScrollArea()
        self.summary_scroll.setWidgetResizable(True)
        self.summary_scroll.setFrameShape(QFrame.NoFrame)
        self.summary_scroll.setStyleSheet("background: transparent;")
        
        self.scroll_content = QWidget()
        self.dashboard_layout = QVBoxLayout(self.scroll_content)
        self.dashboard_layout.setAlignment(Qt.AlignTop)
        self.dashboard_layout.setContentsMargins(20, 20, 20, 20)
        self.dashboard_layout.setSpacing(20)
        
        self.summary_scroll.setWidget(self.scroll_content)
        stats_layout_container.addWidget(self.summary_scroll)
        
        self.content_stack.addWidget(self.page_stats)
        
        # --- TAB: DATA ---
        data_layout = QVBoxLayout()
        data_layout.setContentsMargins(0, 20, 0, 0)
        
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        
        data_layout.addWidget(self.table)
        self.tab_data.setLayout(data_layout)
        
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
                    # Clean display of filename
                    fname = ds['file'].split('/')[-1][:20]
                    item = QListWidgetItem(f"📄 {fname}")
                    item.setToolTip(f"Dataset #{ds['id']} - {ds['uploaded_at']}")
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
        self.lbl_page_title.setText(f"Analysis: {item.text()}")
        self.btn_pdf.setVisible(True)
        
        # Switch stack to stats page
        self.content_stack.setCurrentIndex(1)
        
        self.load_data(dataset_id)
        self.load_stats(dataset_id)

    def load_data(self, id):
        try:
            resp = requests.get(f"{API_URL}datasets/{id}/data/", headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and 'results' in data: 
                    data = data['results']
                
                self.table.setRowCount(len(data))
                self.table.setColumnCount(5)
                self.table.setHorizontalHeaderLabels(["EQUIPMENT NAME", "TYPE", "FLOWRATE (L/min)", "PRESSURE (PSI)", "TEMP (°C)"])
                
                header = self.table.horizontalHeader()
                header.setSectionResizeMode(0, QHeaderView.Stretch)
                header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
                
                for i, row in enumerate(data):
                    self.table.setItem(i, 0, QTableWidgetItem(str(row['equipment_name'])))
                    
                    # Colored Type Badge Logic (Simulated with text color for now, custom widget is complex)
                    type_item = QTableWidgetItem(str(row['equipment_type']))
                    type_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, 1, type_item)
                    
                    self.table.setItem(i, 2, QTableWidgetItem(f"{row['flowrate']:.1f}"))
                    self.table.setItem(i, 3, QTableWidgetItem(f"{row['pressure']:.1f}"))
                    
                    # Temp with alert color
                    temp_item = QTableWidgetItem(f"{row['temperature']:.1f}")
                    if row['temperature'] > 100:
                        temp_item.setForeground(QBrush(QColor('#ef4444'))) # Red
                        temp_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                    self.table.setItem(i, 4, temp_item)
                    
        except Exception as e:
            print(f"Error loading data: {e}")

    def load_stats(self, id):
        try:
            resp = requests.get(f"{API_URL}datasets/{id}/stats/", headers=self.headers)
            if resp.status_code == 200:
                 stats = resp.json()
                 
                 # Clear existing dashboard
                 while self.dashboard_layout.count():
                     item = self.dashboard_layout.takeAt(0)
                     if item.widget(): item.widget().deleteLater()
                 
                 # --- KPI SECTION ---
                 # Wrap in container widget for clean deletion
                 kpi_container = QWidget()
                 kpi_grid = QGridLayout(kpi_container)
                 kpi_grid.setContentsMargins(0, 0, 0, 0)
                 kpi_grid.setSpacing(20)
                 
                 def create_kpi(label, value, unit, color):
                     card = QFrame()
                     card.setObjectName("Card")
                     layout = QVBoxLayout(card)
                     layout.setContentsMargins(20, 20, 20, 20)
                     
                     lbl_label = QLabel(label)
                     lbl_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase;")
                     
                     lbl_val = QLabel(str(value))
                     lbl_val.setStyleSheet("color: #0f172a; font-size: 28px; font-weight: 700; margin-top: 4px;")
                     
                     lbl_unit = QLabel(unit)
                     lbl_unit.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 700;")
                     
                     layout.addWidget(lbl_label)
                     layout.addWidget(lbl_val)
                     layout.addWidget(lbl_unit)
                     return card

                 kpi_grid.addWidget(create_kpi("Total Records", stats['total_count'], "Rows Processed", "#0d9488"), 0, 0)
                 kpi_grid.addWidget(create_kpi("Avg Flowrate", f"{stats['average_flowrate']:.1f}", "L/min", "#0f766e"), 0, 1)
                 kpi_grid.addWidget(create_kpi("Avg Pressure", f"{stats['average_pressure']:.1f}", "PSI", "#f59e0b"), 0, 2)
                 kpi_grid.addWidget(create_kpi("Avg Temperature", f"{stats['average_temperature']:.1f}", "°C", "#ef4444"), 0, 3)
                 
                 self.dashboard_layout.addWidget(kpi_container)
                 
                 # --- CHARTS SECTION ---
                 # Wrap in container widget
                 charts_container = QWidget()
                 charts_row = QHBoxLayout(charts_container)
                 charts_row.setContentsMargins(0, 0, 0, 0)
                 charts_row.setSpacing(20)
                 
                 # 1. PROCESS TRENDS (Line Chart)
                 trend_card = QFrame()
                 trend_card.setObjectName("Card")
                 trend_layout = QVBoxLayout(trend_card)
                 
                 lbl_trend = QLabel("Process Trends (Live Monitoring)")
                 lbl_trend.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 10px;")
                 trend_layout.addWidget(lbl_trend)
                 
                 trend_fig = Figure(figsize=(8, 4), dpi=100)
                 trend_fig.patch.set_facecolor('white')
                 trend_canvas = FigureCanvas(trend_fig)
                 
                 # Fetch full records for trend
                 rec_resp = requests.get(f"{API_URL}datasets/{id}/data/", headers=self.headers)
                 records = rec_resp.json()
                 if isinstance(records, dict) and 'results' in records:
                     records = records['results']
                 
                 ax = trend_fig.add_subplot(111)
                 flow = [r['flowrate'] for r in records]
                 press = [r['pressure'] for r in records]
                 x = range(len(records))
                 
                 ax.plot(x, flow, label='Flowrate', color='#0d9488', linewidth=2)
                 ax.fill_between(x, flow, color='#0d9488', alpha=0.1)
                 ax.plot(x, press, label='Pressure', color='#f59e0b', linestyle='--', linewidth=2)
                 
                 ax.set_facecolor('white')
                 ax.grid(True, linestyle=':', alpha=0.6)
                 ax.legend(loc='upper right', frameon=False)
                 for spine in ax.spines.values(): spine.set_visible(False)
                 
                 trend_layout.addWidget(trend_canvas)
                 charts_row.addWidget(trend_card, stretch=2)
                 
                 # 2. DISTRIBUTION (Donut Chart)
                 dist_card = QFrame()
                 dist_card.setObjectName("Card")
                 dist_layout = QVBoxLayout(dist_card)
                 
                 lbl_dist = QLabel("Equipment Types")
                 lbl_dist.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 10px;")
                 dist_layout.addWidget(lbl_dist)
                 
                 dist_fig = Figure(figsize=(4, 4), dpi=100)
                 dist_fig.patch.set_facecolor('white')
                 dist_canvas = FigureCanvas(dist_fig)
                 
                 ax2 = dist_fig.add_subplot(111)
                 counts = list(stats['type_distribution'].values())
                 labels = list(stats['type_distribution'].keys())
                 colors = ['#0f766e', '#0d9488', '#14b8a6', '#2dd4bf', '#5eead4']
                 
                 wedges, texts, autotexts = ax2.pie(counts, labels=labels, autopct='%1.0f%%', 
                                                    startangle=90, colors=colors[:len(counts)], pctdistance=0.8)
                 
                 # Donut Hole
                 centre_circle = plt.Circle((0,0),0.65,fc='white')
                 ax2.add_artist(centre_circle)
                 
                 plt.setp(autotexts, size=8, weight="bold", color="white")
                 
                 dist_layout.addWidget(dist_canvas)
                 charts_row.addWidget(dist_card, stretch=1)
                 
                 self.dashboard_layout.addWidget(charts_container)
                 
                 self.dashboard_layout.addStretch()

        except Exception as e:
            print(f"Error loading stats: {e}")
            if 'resp' in locals():
                print(f"Response Content: {resp.text}")

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

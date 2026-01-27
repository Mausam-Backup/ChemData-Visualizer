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

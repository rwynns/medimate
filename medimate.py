import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea,
                            QGridLayout, QSpacerItem, QSizePolicy, QLineEdit, QStackedWidget,
                            QDialog, QComboBox, QSpinBox, QTextEdit, QTimeEdit, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QFileSystemWatcher, QTime, QTimer, QUrl
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QPen, QLinearGradient
from datetime import datetime
import os
import json

class MedicineManager:
    def __init__(self):
        # Gunakan path absolut untuk file data
        self.data_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.data_dir, "medicines.json")
        self.medicines = self.load_medicines()
        print(f"Loaded {len(self.medicines)} medicines from {self.data_file}")
    
    def load_medicines(self):
        """Load medicines from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Pastikan data adalah list
                    if isinstance(data, list):
                        return data
                    return []
            else:
                print(f"Data file not found: {self.data_file}")
                return []
        except Exception as e:
            print(f"Error loading medicines: {e}")
            return []
    
    def save_medicines(self):
        """Save medicines to JSON file"""
        try:
            # Pastikan direktori ada
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.medicines, f, ensure_ascii=False, indent=2)
            
            print(f"Saved {len(self.medicines)} medicines to {self.data_file}")
            return True
        except Exception as e:
            print(f"Error saving medicines: {e}")
            return False
    
    def add_medicine(self, medicine_data):
        """Add new medicine"""
        # Generate unique ID if not exists
        if 'id' not in medicine_data:
            # Find highest existing ID
            max_id = 0
            for med in self.medicines:
                if 'id' in med and med['id'] > max_id:
                    max_id = med['id']
            medicine_data['id'] = max_id + 1
        
        # Add timestamps
        medicine_data['created_at'] = datetime.now().isoformat()
        
        self.medicines.append(medicine_data)
        success = self.save_medicines()
        
        print(f"Medicine saved: {medicine_data}")
        return success
    
    def edit_medicine(self, medicine_id, updated_data):
        """Update existing medicine by ID"""
        for i, medicine in enumerate(self.medicines):
            if medicine.get('id') == medicine_id:
                # Preserve some fields from original entry
                updated_data['id'] = medicine_id
                updated_data['created_at'] = medicine.get('created_at')
                updated_data['updated_at'] = datetime.now().isoformat()
                
                # Update the medicine
                self.medicines[i] = updated_data
                print(f"Medicine updated: {updated_data}")
                return self.save_medicines()
                
        print(f"Medicine with ID {medicine_id} not found for update")
        return False
    
    def delete_medicine(self, medicine_id):
        """Delete medicine by ID"""
        for i, medicine in enumerate(self.medicines):
            if medicine.get('id') == medicine_id:
                deleted = self.medicines.pop(i)
                print(f"Medicine deleted: {deleted}")
                return self.save_medicines()
                
        print(f"Medicine with ID {medicine_id} not found for deletion")
        return False
    
    def get_medicine_by_id(self, medicine_id):
        """Get medicine data by ID"""
        for medicine in self.medicines:
            if medicine.get('id') == medicine_id:
                return medicine
        return None
    
    def get_medicines_count(self):
        """Get total number of medicines"""
        return len(self.medicines)
    
    def get_today_schedule(self):
        """Get today's medicine schedule"""
        schedule = []
        for medicine in self.medicines:
            for time in medicine.get('times', []):
                schedule.append({
                    'time': time,
                    'medicine': f"{medicine['name']} - {medicine['dose']}",
                    'status': 'Belum Diminum'  # Default status
                })
        # Sort by time
        schedule.sort(key=lambda x: x['time'])
        return schedule
    
    def get_low_stock_medicines(self):
        """Get medicines with low stock (less than 10)"""
        return [med for med in self.medicines if med.get('stock', 0) < 10]

class StatCard(QFrame):
    def __init__(self, value, title, gradient_colors=("#FF6B9D", "#C44569"), icon="📊"):
        super().__init__()
        self.setFixedSize(280, 180)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {gradient_colors[0]}, stop:1 {gradient_colors[1]});
                border-radius: 25px;
                border: none;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(20, 25, 20, 25)
        layout.setSpacing(15)  # Spacing lebih besar karena tidak ada icon
        
        # Value label - Pastikan background transparan
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Segoe UI", 52, QFont.Weight.Bold))  # Ukuran lebih besar karena fokus utama
        value_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: white;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        # Title label - Pastikan background transparan
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Medium))  # Font lebih besar karena lebih ruang
        title_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: rgba(255, 255, 255, 0.95);
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        title_label.setWordWrap(True)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        self.setLayout(layout)

class MedicationRow(QFrame):
    def __init__(self, time, medication, status):
        super().__init__()
        self.setFixedHeight(105)  # Tinggi diperbesar lagi
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid rgba(226, 232, 240, 0.8);
                margin: 8px 0px;
                border-radius: 15px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(25, 12, 25, 12)  # Vertical padding dikurangi
        layout.setSpacing(20)
        
        # Time container
        time_container = QFrame()
        time_container.setFixedSize(80, 60)
        time_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                border: none;
            }
        """)
        
        time_layout = QVBoxLayout(time_container)
        time_layout.setContentsMargins(5, 5, 5, 5)
        time_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        time_label = QLabel(time)
        time_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        time_label.setStyleSheet("color: white; background: transparent; border: none;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_layout.addWidget(time_label)
        
        # Container untuk medication label
        med_container = QFrame()
        med_container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        med_container_layout = QVBoxLayout(med_container)
        med_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # PERUBAHAN: Menghapus vertical alignment untuk membiarkan teks menggunakan semua ruang
        # med_container_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Medication label
        med_label = QLabel(medication)
        med_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Medium))
        med_label.setStyleSheet("""
            color: #2D3748; 
            background: transparent; 
            border: none;
            padding: 2px 0px;
        """)
        med_label.setWordWrap(True)
        
        # PERUBAHAN: Size policy yang lebih tepat untuk label
        med_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        
        med_container_layout.addWidget(med_label)
        
        # Status button
        status_btn = QPushButton(status)
        status_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        status_btn.setFixedSize(140, 40)
        
        if status == "Sudah Diminum":
            status_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #48BB78, stop:1 #38A169);
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #38A169, stop:1 #2F855A);
                }
            """)
        else:
            status_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #F56565, stop:1 #E53E3E);
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #E53E3E, stop:1 #C53030);
                }
            """)
        
        layout.addWidget(time_container)
        layout.addWidget(med_container)
        layout.addStretch()
        layout.addWidget(status_btn)
        
        self.setLayout(layout)

class SidebarButton(QPushButton):
    def __init__(self, text, icon="", is_active=False):
        super().__init__(f"  {icon}  {text}")
        self.setFixedHeight(55)
        self.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        
        if is_active:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 15px;
                    text-align: left;
                    padding-left: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5a67d8, stop:1 #6b46c1);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #4A5568;
                    border: none;
                    border-radius: 15px;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(102, 126, 234, 0.1), stop:1 rgba(118, 75, 162, 0.1));
                    color: #2D3748;
                }
            """)

class MediMateApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💊 MediMate - Smart Medicine Companion")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f093fb, stop:0.5 #f5576c, stop:1 #4facfe);
            }
        """)
        
        # Initialize medicine manager
        self.medicine_manager = MedicineManager()
        
        # File watcher for auto-reload
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(__file__)
        self.file_watcher.fileChanged.connect(self.file_changed)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        
        # Initialize current page
        self.current_page = "Dashboard"
        
        # Create sidebar
        self.create_sidebar(main_layout)
        
        # Content container yang akan berisi berbagai halaman
        self.content_container = QFrame()
        self.content_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget untuk mengelola halaman
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)
        
        # Buat halaman Dashboard
        self.dashboard_page = QWidget()
        self.create_dashboard(self.dashboard_page)
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # Buat halaman Daftar Obat
        self.medicine_list_page = QWidget()
        self.create_medicine_list(self.medicine_list_page)
        self.stacked_widget.addWidget(self.medicine_list_page)
        
        # Buat halaman Jadwal Hari Ini
        self.today_schedule_page = QWidget()
        self.create_today_schedule_page(self.today_schedule_page)
        self.stacked_widget.addWidget(self.today_schedule_page)
        
        # Tambahkan content container ke main layout
        main_layout.addWidget(self.content_container)
        
        # Alarm system
        self.active_alarms = set()
        self.sound_effect = QSoundEffect()
        self.sound_effect.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), "alarm.mp3")))
        self.sound_effect.setLoopCount(-2)  # -2 artinya infinite loop
        self.sound_effect.setVolume(0.7)
        self.alarm_timer = QTimer(self)
        self.alarm_timer.timeout.connect(self.check_alarm_schedule)
        self.alarm_timer.start(1000 * 30)  # cek setiap 30 detik
    
    def check_alarm_schedule(self):
        now = datetime.now().strftime("%H:%M")
        today_schedule = self.medicine_manager.get_today_schedule()
        for item in today_schedule:
            key = f"{item['time']}|{item['medicine']}"
            if item['time'] == now and item['status'] == 'Belum Diminum' and key not in self.active_alarms:
                self.active_alarms.add(key)
                self.show_alarm_notification(item, key)

    def show_alarm_notification(self, item, alarm_key):
        alarm_path = os.path.join(os.path.dirname(__file__), "alarm.wav")
        if not os.path.exists(alarm_path):
            print("[WARNING] File alarm.wav tidak ditemukan. Alarm tidak akan berbunyi.")
        else:
            self.sound_effect.setSource(QUrl.fromLocalFile(alarm_path))
            self.sound_effect.play()
        dlg = AlarmDialog(self, item, lambda: self.stop_alarm(item, alarm_key))
        dlg.exec()

    def stop_alarm(self, item, alarm_key):
        self.sound_effect.stop()
        # Update status di medicines.json
        for med in self.medicine_manager.medicines:
            if f"{med['name']} - {med['dose']}" == item['medicine']:
                # Update semua jadwal pada jam itu jadi Sudah Diminum
                if 'taken_times' not in med:
                    med['taken_times'] = []
                if item['time'] not in med['taken_times']:
                    med['taken_times'].append(item['time'])
                # Update status per waktu (opsional, untuk future proof)
                if 'status_per_time' not in med:
                    med['status_per_time'] = {}
                med['status_per_time'][item['time']] = 'Sudah Diminum'
                break
        self.medicine_manager.save_medicines()
        self.active_alarms.discard(alarm_key)
        self.refresh_pages()
    
    def create_sidebar(self, main_layout):
        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(25, 35, 25, 35)
        sidebar_layout.setSpacing(15)
        
        # Logo and title
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(0)
        
        logo_label = QLabel("💊")
        logo_label.setFont(QFont("Segoe UI Emoji", 24))
        logo_label.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("MediMate")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            margin-left: 5px;
        """)
        title_label.setContentsMargins(0, 0, 0, 0)
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        logo_layout.addStretch()
        
        sidebar_layout.addLayout(logo_layout)
        sidebar_layout.addSpacing(40)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", "🏠", self.current_page == "Dashboard"),
            ("Daftar Obat", "💊", self.current_page == "Daftar Obat"),
            ("Jadwal Hari Ini", "📅", self.current_page == "Jadwal Hari Ini")
        ]
        
        # Store buttons to update active state later
        self.nav_buttons_dict = {}
        
        for text, icon, is_active in nav_buttons:
            btn = SidebarButton(text, icon, is_active)
            btn.clicked.connect(lambda checked, page=text: self.change_page(page))
            sidebar_layout.addWidget(btn)
            self.nav_buttons_dict[text] = btn
        
        sidebar_layout.addStretch()
        
        # User section
        user_frame = QFrame()
        user_frame.setFixedHeight(80)
        user_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.1), stop:1 rgba(118, 75, 162, 0.1));
                border-radius: 15px;
                padding: 15px;
            }
        """)
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(15, 15, 15, 15)
        
        user_info = QVBoxLayout()
        user_info.setSpacing(4)
        user_name = QLabel("John Doe")
        user_name.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        user_name.setStyleSheet("color: #2D3748;")
        
        user_status = QLabel("Premium User")
        user_status.setFont(QFont("Segoe UI", 11))
        user_status.setStyleSheet("color: #667eea;")
        
        user_info.addWidget(user_name)
        user_info.addWidget(user_status)
        
        user_avatar = QLabel("👤")
        user_avatar.setFont(QFont("Segoe UI Emoji", 24))
        user_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        user_layout.addLayout(user_info)
        user_layout.addStretch()
        user_layout.addWidget(user_avatar)
        
        sidebar_layout.addWidget(user_frame)
        main_layout.addWidget(sidebar)
    
    def create_dashboard(self, page):
        # Content layout for dashboard
        content_layout = QVBoxLayout(page)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Dashboard title
        title_label = QLabel("Dashboard")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #2D3748, stop:1 #4A5568);
        """)
        
        # Date and time
        date_time = QLabel(datetime.now().strftime("%A, %B %d, %Y"))
        date_time.setFont(QFont("Segoe UI", 13))
        date_time.setStyleSheet("color: #718096;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(date_time)
        content_layout.addLayout(header_layout)
        
        # Stats cards with dynamic data
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Get dynamic data
        total_medicines = self.medicine_manager.get_medicines_count()
        today_schedule = self.medicine_manager.get_today_schedule()
        low_stock_count = len(self.medicine_manager.get_low_stock_medicines())
        
        # Create stat cards with dynamic data
        cards_data = [
            (total_medicines, "Total Obat\nAktif", ("#FF6B9D", "#C44569"), "💊"),
            (len(today_schedule), "Jadwal\nHari Ini", ("#4FACFE", "#00F2FE"), "📅"),
            (low_stock_count, "Obat Hampir\nHabis", ("#FA709A", "#FEE140"), "⚠️")
        ]
        
        for value, title, colors, icon in cards_data:
            card = StatCard(value, title, colors, icon)
            stats_layout.addWidget(card)
        
        content_layout.addLayout(stats_layout)
        
        # Today's schedule section dengan data dinamis
        schedule_frame = QFrame()
        schedule_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9), stop:1 rgba(247, 250, 252, 0.9));
                border-radius: 20px;
                border: 1px solid rgba(226, 232, 240, 0.5);
            }
        """)
        
        schedule_layout = QVBoxLayout(schedule_frame)
        schedule_layout.setContentsMargins(30, 25, 30, 25)
        
        # Schedule header
        schedule_header = QHBoxLayout()
        schedule_title = QLabel("📋 Jadwal Hari Ini")
        schedule_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        schedule_title.setStyleSheet("color: #2D3748; margin-bottom: 10px;")
        
        view_all_btn = QPushButton("Lihat Semua")
        view_all_btn.setFont(QFont("Segoe UI", 11))
        view_all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
        """)
        
        schedule_header.addWidget(schedule_title)
        schedule_header.addStretch()
        schedule_header.addWidget(view_all_btn)
        schedule_layout.addLayout(schedule_header)
        
        # Add elegant separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            border: none;
            height: 2px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(102, 126, 234, 0.3), stop:0.5 rgba(118, 75, 162, 0.3), stop:1 rgba(102, 126, 234, 0.3));
            margin: 10px 0px;
        """)
        schedule_layout.addWidget(separator)
        
        # Display today's schedule dynamically
        if today_schedule:
            for schedule_item in today_schedule:
                med_row = MedicationRow(
                    schedule_item['time'], 
                    schedule_item['medicine'], 
                    schedule_item['status']
                )
                schedule_layout.addWidget(med_row)
        else:
            # Show message when no schedule
            no_schedule_label = QLabel("📅 Belum ada jadwal obat untuk hari ini")
            no_schedule_label.setFont(QFont("Segoe UI", 14))
            no_schedule_label.setStyleSheet("""
                color: #718096;
                text-align: center;
                padding: 40px;
            """)
            no_schedule_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            schedule_layout.addWidget(no_schedule_label)
        
        content_layout.addWidget(schedule_frame)
        content_layout.addStretch()
    
    def create_medicine_list(self, page):
        # Content layout for medicine list
        content_layout = QVBoxLayout(page)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Page title
        title_label = QLabel("Daftar Obat")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #2D3748, stop:1 #4A5568);
        """)
        
        # Add medicine button
        add_btn = QPushButton("+ Tambah Obat")
        add_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #43E97B, stop:1 #38F9D7);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #38D86A, stop:1 #32E5C4);
            }
        """)
        add_btn.clicked.connect(self.show_add_medicine_dialog)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        content_layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 10, 0, 20)
        
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Cari obat...")
        search_bar.setFont(QFont("Segoe UI", 12))
        search_bar.setFixedHeight(45)
        search_bar.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 8px 15px;
                color: #2D3748;
            }
            QLineEdit:focus {
                border: 1px solid #667eea;
                color: #2D3748;
            }
            QLineEdit::placeholder {
                color: #A0AEC0;
            }
        """)
        
        search_layout.addWidget(search_bar)
        content_layout.addLayout(search_layout)
        
        # Medicine list frame
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid rgba(226, 232, 240, 0.8);
            }
        """)
        
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(25, 25, 25, 25)
        list_layout.setSpacing(15)
        
        # Headers
        headers_layout = QHBoxLayout()
        headers = ["Nama Obat", "Dosis", "Stok", "Jadwal", "Aksi"]
        widths = [3, 2, 1, 3, 2]
        
        for i, header in enumerate(headers):
            header_label = QLabel(header)
            header_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            header_label.setStyleSheet("color: #4A5568;")
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.addWidget(header_label)
            
            if i < len(headers) - 1:  # Don't add stretch to last header
                header_layout.addStretch()
            
            headers_layout.addLayout(header_layout, widths[i])
        
        list_layout.addLayout(headers_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            border: none;
            height: 2px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(226, 232, 240, 0.5), stop:1 rgba(226, 232, 240, 0.8));
            margin: 5px 0px 15px 0px;
        """)
        list_layout.addWidget(separator)
        
        # Medicine rows - display from saved data
        medicines = self.medicine_manager.medicines
        
        if medicines:
            for medicine in medicines:
                row_layout = QHBoxLayout()
                
                # Name
                name_label = QLabel(medicine['name'])
                name_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
                name_label.setStyleSheet("color: #2D3748;")
                name_layout = QHBoxLayout()
                name_layout.addWidget(name_label)
                name_layout.addStretch()
                
                # Dose
                dose_label = QLabel(medicine['dose'])
                dose_label.setFont(QFont("Segoe UI", 13))
                dose_label.setStyleSheet("color: #4A5568;")
                dose_layout = QHBoxLayout()
                dose_layout.addWidget(dose_label)
                dose_layout.addStretch()
                
                # Stock
                stock_text = f"{medicine['stock']} {medicine.get('stock_unit', 'tablet')}"
                stock_label = QLabel(stock_text)
                stock_label.setFont(QFont("Segoe UI", 13))
                stock_label.setStyleSheet("color: #4A5568;")
                stock_layout = QHBoxLayout()
                stock_layout.addWidget(stock_label)
                stock_layout.addStretch()
                
                # Schedule
                schedule_text = ", ".join(medicine.get('times', []))
                schedule_label = QLabel(schedule_text)
                schedule_label.setFont(QFont("Segoe UI", 13))
                schedule_label.setStyleSheet("color: #4A5568;")
                schedule_layout = QHBoxLayout()
                schedule_layout.addWidget(schedule_label)
                schedule_layout.addStretch()
                
                # Actions
                action_layout = QHBoxLayout()
                
                edit_btn = QPushButton("Edit")
                edit_btn.setFont(QFont("Segoe UI", 11))
                edit_btn.setFixedSize(70, 35)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background: #EDF2F7;
                        color: #4A5568;
                        border: none;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background: #E2E8F0;
                    }
                """)
                # Tambahkan koneksi tombol edit
                edit_btn.clicked.connect(lambda checked, med=medicine: self.show_edit_medicine_dialog(med))
                delete_btn = QPushButton("Hapus")
                delete_btn.setFont(QFont("Segoe UI", 11))
                delete_btn.setFixedSize(70, 35)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background: #FED7D7;
                        color: #E53E3E;
                        border: none;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background: #FEB2B2;
                    }
                """)
                # Tambahkan koneksi tombol hapus
                delete_btn.clicked.connect(lambda checked, med=medicine: self.delete_medicine_with_confirm(med))
                
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(delete_btn)
                
                # Add all to row
                row_layout.addLayout(name_layout, widths[0])
                row_layout.addLayout(dose_layout, widths[1])
                row_layout.addLayout(stock_layout, widths[2])
                row_layout.addLayout(schedule_layout, widths[3])
                row_layout.addLayout(action_layout, widths[4])
                
                # Add row to list
                list_layout.addLayout(row_layout)
                
                # Add separator between rows
                if medicines.index(medicine) < len(medicines) - 1:
                    row_separator = QFrame()
                    row_separator.setFrameShape(QFrame.Shape.HLine)
                    row_separator.setStyleSheet("""
                        border: none;
                        height: 1px;
                        background: #E2E8F0;
                        margin: 8px 0px;
                    """)
                    list_layout.addWidget(row_separator)
        else:
            # Show message when no medicines
            no_medicine_label = QLabel("💊 Belum ada obat yang ditambahkan")
            no_medicine_label.setFont(QFont("Segoe UI", 14))
            no_medicine_label.setStyleSheet("""
                color: #718096;
                text-align: center;
                padding: 40px;
            """)
            no_medicine_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            list_layout.addWidget(no_medicine_label)
        
        content_layout.addWidget(list_frame)
        content_layout.addStretch()
    
    def create_today_schedule_page(self, page):
        content_layout = QVBoxLayout(page)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Jadwal Hari Ini")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2D3748, stop:1 #4A5568);")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)

        # Ambil jadwal hari ini
        today_schedule = self.medicine_manager.get_today_schedule()

        # Frame utama
        schedule_frame = QFrame()
        schedule_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9), stop:1 rgba(247, 250, 252, 0.9));
                border-radius: 20px;
                border: 1px solid rgba(226, 232, 240, 0.5);
            }
        """)
        schedule_layout = QVBoxLayout(schedule_frame)
        schedule_layout.setContentsMargins(30, 25, 30, 25)
        schedule_layout.setSpacing(15)

        # Judul
        schedule_title = QLabel("📋 Jadwal Obat Hari Ini")
        schedule_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        schedule_title.setStyleSheet("color: #2D3748; margin-bottom: 10px;")
        schedule_layout.addWidget(schedule_title)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            border: none;
            height: 2px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(102, 126, 234, 0.3), stop:0.5 rgba(118, 75, 162, 0.3), stop:1 rgba(102, 126, 234, 0.3));
            margin: 10px 0px;
        """)
        schedule_layout.addWidget(separator)

        # Daftar jadwal
        if today_schedule:
            for item in today_schedule:
                row = QFrame()
                row.setStyleSheet("""
                    QFrame {
                        background: white;
                        border-radius: 12px;
                        border: 1px solid #E2E8F0;
                        margin-bottom: 10px;
                    }
                """)
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(18, 10, 18, 10)
                row_layout.setSpacing(20)
                time_label = QLabel(item['time'])
                time_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
                time_label.setStyleSheet("color: #667eea;")
                med_label = QLabel(item['medicine'])
                med_label.setFont(QFont("Segoe UI", 14))
                med_label.setStyleSheet("color: #2D3748;")
                
                # Badge status
                status = 'Sudah Diminum' if self.is_time_taken(item) else item['status']
                status_badge = QLabel(status)
                status_badge.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                if status == 'Belum Diminum':
                    status_badge.setStyleSheet("""
                        QLabel {
                            background: #FFF5F5;
                            color: #E53E3E;
                            border: 1.5px solid #FEB2B2;
                            border-radius: 12px;
                            padding: 4px 16px;
                            min-width: 90px;
                            text-align: center;
                        }
                    """)
                else:
                    status_badge.setStyleSheet("""
                        QLabel {
                            background: #F0FFF4;
                            color: #38A169;
                            border: 1.5px solid #68D391;
                            border-radius: 12px;
                            padding: 4px 16px;
                            min-width: 90px;
                            text-align: center;
                        }
                    """)
                row_layout.addWidget(time_label, 1)
                row_layout.addWidget(med_label, 4)
                row_layout.addWidget(status_badge, 2)
                schedule_layout.addWidget(row)
        else:
            no_schedule_label = QLabel("Tidak ada jadwal obat untuk hari ini.")
            no_schedule_label.setFont(QFont("Segoe UI", 14))
            no_schedule_label.setStyleSheet("color: #718096; text-align: center; padding: 40px;")
            no_schedule_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            schedule_layout.addWidget(no_schedule_label)

        content_layout.addWidget(schedule_frame)
        content_layout.addStretch()

    def show_add_medicine_dialog(self):
        dialog = AddMedicineDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get medicine data from dialog
            medicine_data = dialog.get_medicine_data()
            
            print(f"Adding medicine to manager: {medicine_data}")
            
            if self.medicine_manager.add_medicine(medicine_data):
                # Show success message
                QMessageBox.information(self, "Berhasil", "Obat berhasil ditambahkan!")
                
                # Refresh dashboard and medicine list
                self.refresh_pages()
            else:
                # Show error message
                QMessageBox.critical(self, "Error", "Gagal menyimpan obat!")
    
    def show_edit_medicine_dialog(self, medicine):
        dialog = EditMedicineDialog(self, medicine)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_medicine_data()
            updated_data['id'] = medicine.get('id')
            updated_data['created_at'] = medicine.get('created_at')
            if self.medicine_manager.edit_medicine(medicine.get('id'), updated_data):
                QMessageBox.information(self, "Berhasil", "Obat berhasil diupdate!")
                self.refresh_pages()
            else:
                QMessageBox.critical(self, "Error", "Gagal mengupdate obat!")
    
    def refresh_pages(self):
        # Refresh dashboard
        self.stacked_widget.removeWidget(self.dashboard_page)
        self.dashboard_page = QWidget()
        self.create_dashboard(self.dashboard_page)
        self.stacked_widget.insertWidget(0, self.dashboard_page)
        
        # Refresh medicine list
        self.stacked_widget.removeWidget(self.medicine_list_page)
        self.medicine_list_page = QWidget()
        self.create_medicine_list(self.medicine_list_page)
        self.stacked_widget.insertWidget(1, self.medicine_list_page)
        
        # Refresh today schedule page
        self.stacked_widget.removeWidget(self.today_schedule_page)
        self.today_schedule_page = QWidget()
        self.create_today_schedule_page(self.today_schedule_page)
        self.stacked_widget.insertWidget(2, self.today_schedule_page)
        
        # Set current page
        if self.current_page == "Dashboard":
            self.stacked_widget.setCurrentIndex(0)
        elif self.current_page == "Daftar Obat":
            self.stacked_widget.setCurrentIndex(1)
        elif self.current_page == "Jadwal Hari Ini":
            self.stacked_widget.setCurrentIndex(2)
    
    def change_page(self, page_name):
        # Update current page
        self.current_page = page_name
        
        # Set stacked widget index
        if page_name == "Dashboard":
            self.stacked_widget.setCurrentIndex(0)
        elif page_name == "Daftar Obat":
            self.stacked_widget.setCurrentIndex(1)
        elif page_name == "Jadwal Hari Ini":
            self.stacked_widget.setCurrentIndex(2)
        # Add more pages as needed
        
        # Update sidebar button states
        for name, btn in self.nav_buttons_dict.items():
            if name == page_name:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #667eea, stop:1 #764ba2);
                        color: white;
                        border: none;
                        border-radius: 15px;
                        text-align: left;
                        padding-left: 20px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #5a67d8, stop:1 #6b46c1);
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #4A5568;
                        border: none;
                        border-radius: 15px;
                        text-align: left;
                        padding-left: 20px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(102, 126, 234, 0.1), stop:1 rgba(118, 75, 162, 0.1));
                        color: #2D3748;
                    }
                """)
    
    def file_changed(self):
        print("File changed, restarting...")
        QApplication.quit()
        os.execv(sys.executable, ['python'] + sys.argv)

    def delete_medicine_with_confirm(self, medicine):
        reply = QMessageBox.question(self, "Konfirmasi Hapus", f"Yakin ingin menghapus obat '{medicine['name']}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.medicine_manager.delete_medicine(medicine.get('id')):
                QMessageBox.information(self, "Berhasil", "Obat berhasil dihapus!")
                self.refresh_pages()
            else:
                QMessageBox.critical(self, "Error", "Gagal menghapus obat!")

    def is_time_taken(self, item):
        for med in self.medicine_manager.medicines:
            if f"{med['name']} - {med['dose']}" == item['medicine']:
                return 'taken_times' in med and item['time'] in med['taken_times']
        return False

class AlarmDialog(QDialog):
    def __init__(self, parent, item, stop_callback):
        super().__init__(parent)
        self.setWindowTitle("Alarm Obat!")
        self.setModal(True)
        self.setFixedSize(420, 260)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f093fb, stop:0.5 #f5576c, stop:1 #4facfe);
                border-radius: 20px;
            }
        """)
        main = QVBoxLayout(self)
        main.setContentsMargins(30, 30, 30, 30)
        main.setSpacing(18)
        icon = QLabel("⏰")
        icon.setFont(QFont("Segoe UI Emoji", 48))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(icon)
        title = QLabel("Waktunya Minum Obat!")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2D3748;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(title)
        info = QLabel(f"{item['medicine']}\nJam: {item['time']}")
        info.setFont(QFont("Segoe UI", 14))
        info.setStyleSheet("color: #4A5568;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(info)
        btn = QPushButton("Sudah Diminum & Matikan Alarm")
        btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #43E97B, stop:1 #38F9D7);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 18px;
                font-size: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #38D86A, stop:1 #32E5C4);
            }
        """)
        btn.clicked.connect(self.accept)
        main.addWidget(btn)
        self.accepted.connect(stop_callback)

class AddMedicineDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Obat Baru")
        self.setFixedSize(500, 750)
        self.setModal(True)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f093fb, stop:0.5 #f5576c, stop:1 #4facfe);
            }
        """)
        
        # Main container
        main_container = QFrame()
        main_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(main_container)
          # Form layout
        form_layout = QVBoxLayout(main_container)
        form_layout.setContentsMargins(30, 25, 30, 25)
        form_layout.setSpacing(18)
          # Title
        title_label = QLabel("💊 Tambah Obat Baru")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            margin: 5px 0px 15px 0px;
            padding: 0px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(title_label)
        
        # Medicine name
        self.create_form_field(form_layout, "Nama Obat:", "medicine_name", "Masukkan nama obat...")
        
        # Dose
        self.create_form_field(form_layout, "Dosis:", "dose", "Contoh: 500mg, 2 tablet, dll...")
        
        # Stock
        stock_layout = QHBoxLayout()
        stock_label = QLabel("Stok:")
        stock_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        stock_label.setStyleSheet("color: #2D3748;")
        
        self.stock_spinbox = QSpinBox()
        self.stock_spinbox.setRange(1, 9999)
        self.stock_spinbox.setValue(30)
        self.stock_spinbox.setStyleSheet(self.get_input_style())
        self.stock_spinbox.setFixedHeight(40)
        
        stock_unit = QComboBox()
        stock_unit.addItems(["tablet", "kapsul", "ml", "mg", "vial", "sachet"])
        stock_unit.setStyleSheet(self.get_input_style())
        stock_unit.setFixedHeight(40)
        
        stock_layout.addWidget(stock_label, 1)
        stock_layout.addWidget(self.stock_spinbox, 2)
        stock_layout.addWidget(stock_unit, 1)
        form_layout.addLayout(stock_layout)
        
        # Schedule section
        schedule_label = QLabel("Jadwal Konsumsi:")
        schedule_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        schedule_label.setStyleSheet("color: #2D3748; margin-top: 10px;")
        form_layout.addWidget(schedule_label)
        
        # Times container
        self.times_container = QFrame()
        self.times_layout = QVBoxLayout(self.times_container)
        self.times_layout.setContentsMargins(0, 0, 0, 0)
        self.times_layout.setSpacing(10)
        
        # Initial time input
        self.add_time_input()
        
        form_layout.addWidget(self.times_container)
        
        # Add time button
        add_time_btn = QPushButton("+ Tambah Waktu")
        add_time_btn.setFont(QFont("Segoe UI", 11))
        add_time_btn.setStyleSheet("""
            QPushButton {
                background: #E2E8F0;
                color: #4A5568;
                border: none;
                border-radius: 10px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background: #CBD5E0;
            }
        """)
        add_time_btn.clicked.connect(self.add_time_input)
        form_layout.addWidget(add_time_btn)
        
        # Notes
        notes_label = QLabel("Catatan (Opsional):")
        notes_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        notes_label.setStyleSheet("color: #2D3748;")
        form_layout.addWidget(notes_label)
        
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Catatan tambahan untuk obat ini...")
        self.notes_text.setFixedHeight(80)
        self.notes_text.setStyleSheet(self.get_input_style())
        form_layout.addWidget(self.notes_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        cancel_btn.setFixedHeight(45)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #F7FAFC;
                color: #4A5568;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: #EDF2F7;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Simpan Obat")
        save_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        save_btn.setFixedHeight(45)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #43E97B, stop:1 #38F9D7);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #38D86A, stop:1 #32E5C4);
            }
        """)
        save_btn.clicked.connect(self.save_medicine)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        form_layout.addLayout(button_layout)
    
    def create_form_field(self, layout, label_text, field_name, placeholder):
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        label.setStyleSheet("color: #2D3748;")
        layout.addWidget(label)
        
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFont(QFont("Segoe UI", 11))
        field.setFixedHeight(40)
        field.setStyleSheet(self.get_input_style())
        setattr(self, field_name, field)
        layout.addWidget(field)
    
    def get_input_style(self):
        return """
            QLineEdit, QComboBox, QTextEdit {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 11pt;
                color: #2D3748;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 2px solid #667eea;
                color: #2D3748;
            }
            QLineEdit::placeholder, QTextEdit::placeholder {
                color: #A0AEC0;
            }
            
            QSpinBox, QTimeEdit {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 11pt;
                color: #2D3748;
            }
            QSpinBox:focus, QTimeEdit:focus {
                border: 2px solid #667eea;
                color: #2D3748;
            }
        """
    
    def add_time_input(self):
        time_layout = QHBoxLayout()
        time_layout.setSpacing(10)
        
        time_edit = QTimeEdit()
        time_edit.setTime(QTime(8, 0))
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setStyleSheet(self.get_input_style())
        time_edit.setFixedHeight(40)
        
        remove_btn = QPushButton("Hapus")
        remove_btn.setFixedSize(70, 40)
        remove_btn.setStyleSheet("""
            QPushButton {
                background: #FED7D7;
                color: #E53E3E;
                border: none;
                border-radius: 8px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: #FEB2B2;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_time_input(time_layout))
        
        time_layout.addWidget(time_edit, 3)
        time_layout.addWidget(remove_btn, 1)
        
        self.times_layout.addLayout(time_layout)
    
    def remove_time_input(self, layout_to_remove):
        # Only remove if there's more than one time input
        if self.times_layout.count() > 1:
            # Remove all widgets in the layout
            while layout_to_remove.count():
                widget = layout_to_remove.takeAt(0).widget()
                if widget:
                    widget.deleteLater()
            # Remove the layout itself
            self.times_layout.removeItem(layout_to_remove)
    
    def save_medicine(self):
        # Get medicine data
        medicine_data = self.get_medicine_data()
        
        # Print for debugging
        print(f"Saving medicine: {medicine_data}")
        
        # Basic validation
        if not medicine_data['name'] or not medicine_data['dose']:
            QMessageBox.warning(self, "Peringatan", "Nama obat dan dosis harus diisi!")
            return
        
        if not medicine_data['times']:
            QMessageBox.warning(self, "Peringatan", "Minimal satu jadwal waktu harus diisi!")
            return
        
        self.accept()
    
    def get_medicine_data(self):
        # Get stock unit
        stock_unit = self.findChild(QComboBox).currentText()
        
        # Collect data from form
        medicine_data = {
            'name': self.medicine_name.text(),
            'dose': self.dose.text(),
            'stock': self.stock_spinbox.value(),
            'stock_unit': stock_unit,
            'times': [],
            'notes': self.notes_text.toPlainText()
        }
        
        # Collect all time inputs
        for i in range(self.times_layout.count()):
            layout = self.times_layout.itemAt(i).layout()
            if layout:
                time_edit = layout.itemAt(0).widget()
                if isinstance(time_edit, QTimeEdit):
                    medicine_data['times'].append(time_edit.time().toString("HH:mm"))
        
        return medicine_data

class EditMedicineDialog(AddMedicineDialog):
    def __init__(self, parent=None, medicine_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Obat")
        # Ubah judul
        self.findChild(QLabel).setText("💊 Edit Obat")
        # Isi field dengan data lama
        if medicine_data:
            self.medicine_name.setText(medicine_data.get('name', ''))
            self.dose.setText(medicine_data.get('dose', ''))
            self.stock_spinbox.setValue(medicine_data.get('stock', 1))
            # Set stock_unit
            stock_unit = self.findChild(QComboBox)
            idx = stock_unit.findText(medicine_data.get('stock_unit', 'tablet'))
            if idx >= 0:
                stock_unit.setCurrentIndex(idx)
            # Set times
            # Hapus time input default
            while self.times_layout.count():
                layout = self.times_layout.takeAt(0)
                if layout:
                    l = layout.layout()
                    if l:
                        while l.count():
                            w = l.takeAt(0).widget()
                            if w:
                                w.deleteLater()
            for t in medicine_data.get('times', []):
                self.add_time_input()
                layout = self.times_layout.itemAt(self.times_layout.count()-1).layout()
                if layout:
                    time_edit = layout.itemAt(0).widget()
                    if isinstance(time_edit, QTimeEdit):
                        h, m = map(int, t.split(":"))
                        time_edit.setTime(QTime(h, m))
            self.notes_text.setPlainText(medicine_data.get('notes', ''))

    def save_medicine(self):
        # Get medicine data
        medicine_data = self.get_medicine_data()
        print(f"Saving medicine: {medicine_data}")
        # Basic validation
        if not medicine_data['name'] or not medicine_data['dose']:
            QMessageBox.warning(self, "Peringatan", "Nama obat dan dosis harus diisi!")
            return
        if not medicine_data['times']:
            QMessageBox.warning(self, "Peringatan", "Minimal satu jadwal waktu harus diisi!")
            return
        # Tidak perlu set id/created_at di sini, akan diatur di MediMateApp
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MediMateApp()
    window.show()
    sys.exit(app.exec())
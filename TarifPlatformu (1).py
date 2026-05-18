import sys
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QLabel,
    QLineEdit, QComboBox, QMessageBox, QTabWidget, QFrame, QSpinBox,
    QHeaderView, QGridLayout, QTextEdit, QStackedWidget, QToolBar
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QColor, QIcon, QPalette, QLinearGradient, QBrush, QPainter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ===================== VERİTABANI YÖNETİCİSİ =====================

class DatabaseManager:
    def __init__(self, db_name="yemek_tarif.db"):
        self.db_name = db_name
        self.create_tables()
        self.ornek_veri_ekle()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tarifler (
                    tarif_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL,
                    kategori TEXT NOT NULL,
                    hazirlama_suresi INTEGER NOT NULL,
                    talimat TEXT,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS malzemeler (
                    malzeme_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarif_id INTEGER NOT NULL,
                    malzeme_adi TEXT NOT NULL,
                    miktar TEXT NOT NULL,
                    FOREIGN KEY (tarif_id) REFERENCES tarifler(tarif_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kullanicilar (
                    kullanici_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL,
                    soyad TEXT NOT NULL,
                    email TEXT UNIQUE,
                    kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS degerlendirmeler (
                    degerlendirme_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarif_id INTEGER NOT NULL,
                    kullanici_id INTEGER NOT NULL,
                    puan INTEGER NOT NULL,
                    yorum TEXT,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tarif_id) REFERENCES tarifler(tarif_id),
                    FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kategoriler (
                    kategori_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kategori_adi TEXT UNIQUE NOT NULL
                )
            ''')

            kategoriler = ['Türk Mutfağı', 'İtalyan Mutfağı', 'Çin Mutfağı', 'Tatlılar', 'Çorbalar', 'Salatalar', 'Ana Yemek', 'Kahvaltılık', 'Vegan', 'Glutensiz']
            for kategori in kategoriler:
                cursor.execute('INSERT OR IGNORE INTO kategoriler (kategori_adi) VALUES (?)', (kategori,))

    def ornek_veri_ekle(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM tarifler')
            if cursor.fetchone()[0] == 0:
                ornek_tarifler = [
                    ("Mercimek Çorbası", "Çorbalar", 30, "Mercimek, soğan, havuç, salça, baharatlar ile hazırlanır."),
                    ("Mantı", "Türk Mutfağı", 90, "Hamur yoğrulur, küçük karelere kesilir, içine kıymalı harç konur."),
                    ("İskender Kebap", "Türk Mutfağı", 60, "Pide üzerine döner, domates sosu ve yoğurt ile servis edilir."),
                    ("Tiramisu", "İtalyan Mutfağı", 45, "Kahve, mascarpone peyniri, pandispanya ve kakao ile hazırlanır."),
                    ("Çin Usulü Pilav", "Çin Mutfağı", 35, "Pirinç, yumurta, soya sosu, sebzeler ile yapılır."),
                    ("Menemen", "Kahvaltılık", 15, "Yumurta, domates, biber, soğan ile hazırlanır."),
                    ("Baklava", "Tatlılar", 120, "Yufka, ceviz, şerbet ile yapılır."),
                    ("Tarator", "Salatalar", 10, "Ceviz, yoğurt, sarımsak, dereotu ile hazırlanır."),
                    ("Izgara Somon", "Ana Yemek", 25, "Somon fileto, limon, tuz, karabiber ile ızgarada pişirilir."),
                    ("Vegan Burger", "Vegan", 30, "Nohut köftesi, marul, domates, vegan sos ile servis edilir."),
                ]
                for tarif in ornek_tarifler:
                    cursor.execute('''
                        INSERT INTO tarifler (ad, kategori, hazirlama_suresi, talimat)
                        VALUES (?, ?, ?, ?)
                    ''', tarif)

                ornek_malzemeler = [
                    (1, "Mercimek", "2 su bardağı"),
                    (1, "Soğan", "1 adet"),
                    (1, "Havuç", "1 adet"),
                    (2, "Un", "3 su bardağı"),
                    (2, "Kıyma", "250 gr"),
                    (2, "Soğan", "1 adet"),
                    (3, "Döner", "300 gr"),
                    (3, "Yoğurt", "1 kase"),
                    (3, "Domates Sosu", "1 kase"),
                    (4, "Mascarpone", "250 gr"),
                    (4, "Kahve", "1 fincan"),
                    (4, "Kakao", "2 yemek kaşığı"),
                ]
                for malzeme in ornek_malzemeler:
                    cursor.execute('''
                        INSERT INTO malzemeler (tarif_id, malzeme_adi, miktar)
                        VALUES (?, ?, ?)
                    ''', malzeme)

                ornek_kullanicilar = [
                    ("Ahmet", "Yılmaz", "ahmet@email.com"),
                    ("Ayşe", "Demir", "ayse@email.com"),
                    ("Mehmet", "Kaya", "mehmet@email.com"),
                    ("Zeynep", "Çelik", "zeynep@email.com"),
                ]
                for kullanici in ornek_kullanicilar:
                    cursor.execute('''
                        INSERT INTO kullanicilar (ad, soyad, email)
                        VALUES (?, ?, ?)
                    ''', kullanici)

    def tarif_ekle(self, ad, kategori, hazirlama_suresi, talimat):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tarifler (ad, kategori, hazirlama_suresi, talimat)
                VALUES (?, ?, ?, ?)
            ''', (ad, kategori, hazirlama_suresi, talimat))
            return cursor.lastrowid

    def tarif_sil(self, tarif_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM malzemeler WHERE tarif_id = ?', (tarif_id,))
            cursor.execute('DELETE FROM degerlendirmeler WHERE tarif_id = ?', (tarif_id,))
            cursor.execute('DELETE FROM tarifler WHERE tarif_id = ?', (tarif_id,))
            return True

    def tarifleri_getir(self, kategori=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if kategori and kategori != "Tümü":
                cursor.execute('SELECT * FROM tarifler WHERE kategori = ? ORDER BY ad', (kategori,))
            else:
                cursor.execute('SELECT * FROM tarifler ORDER BY ad')
            return [dict(row) for row in cursor.fetchall()]

    def tarif_bul(self, tarif_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tarifler WHERE tarif_id = ?', (tarif_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def malzeme_ekle(self, tarif_id, malzeme_adi, miktar):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO malzemeler (tarif_id, malzeme_adi, miktar)
                VALUES (?, ?, ?)
            ''', (tarif_id, malzeme_adi, miktar))
            return cursor.lastrowid

    def malzemeleri_getir(self, tarif_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM malzemeler WHERE tarif_id = ? ORDER BY malzeme_id', (tarif_id,))
            return [dict(row) for row in cursor.fetchall()]

    def kullanici_ekle(self, ad, soyad, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO kullanicilar (ad, soyad, email)
                VALUES (?, ?, ?)
            ''', (ad, soyad, email))
            return cursor.lastrowid

    def kullanici_sil(self, kullanici_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM degerlendirmeler WHERE kullanici_id = ?', (kullanici_id,))
            cursor.execute('DELETE FROM kullanicilar WHERE kullanici_id = ?', (kullanici_id,))
            return True

    def kullanicilari_getir(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM kullanicilar ORDER BY kayit_tarihi DESC')
            return [dict(row) for row in cursor.fetchall()]

    def degerlendirme_ekle(self, tarif_id, kullanici_id, puan, yorum):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO degerlendirmeler (tarif_id, kullanici_id, puan, yorum)
                VALUES (?, ?, ?, ?)
            ''', (tarif_id, kullanici_id, puan, yorum))
            return cursor.lastrowid

    def degerlendirmeleri_getir(self, tarif_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT d.*, k.ad, k.soyad
                FROM degerlendirmeler d
                JOIN kullanicilar k ON d.kullanici_id = k.kullanici_id
                WHERE d.tarif_id = ?
                ORDER BY d.tarih DESC
            ''', (tarif_id,))
            return [dict(row) for row in cursor.fetchall()]

    def ortalama_puan(self, tarif_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT AVG(puan) as ortalama FROM degerlendirmeler WHERE tarif_id = ?', (tarif_id,))
            row = cursor.fetchone()
            return round(row['ortalama'], 1) if row['ortalama'] else 0

    def kategorileri_getir(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT kategori_adi FROM kategoriler ORDER BY kategori_adi')
            return [row['kategori_adi'] for row in cursor.fetchall()]

    def istatistikler(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as toplam_tarif FROM tarifler')
            toplam_tarif = cursor.fetchone()['toplam_tarif']

            cursor.execute('SELECT COUNT(*) as toplam_kategori FROM kategoriler')
            toplam_kategori = cursor.fetchone()['toplam_kategori']

            cursor.execute('SELECT COUNT(*) as toplam_kullanici FROM kullanicilar')
            toplam_kullanici = cursor.fetchone()['toplam_kullanici']

            cursor.execute('SELECT COUNT(*) as toplam_degerlendirme FROM degerlendirmeler')
            toplam_degerlendirme = cursor.fetchone()['toplam_degerlendirme']

            cursor.execute('''
                SELECT kategori, COUNT(*) as sayi
                FROM tarifler GROUP BY kategori ORDER BY sayi DESC
            ''')
            kategori_dagilimi = [dict(row) for row in cursor.fetchall()]

            return {
                "toplam_tarif": toplam_tarif,
                "toplam_kategori": toplam_kategori,
                "toplam_kullanici": toplam_kullanici,
                "toplam_degerlendirme": toplam_degerlendirme,
                "kategori_dagilimi": kategori_dagilimi
            }


# ===================== ÖZEL BUTON SINIFI =====================

class LuxuryButton(QPushButton):
    def __init__(self, text, color="#f5a623", parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 #1a1a2e);
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 25px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 {color});
            }}
        """)

    def enterEvent(self, event):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        rect = self.geometry()
        self.animation.setStartValue(rect)
        rect.setWidth(rect.width() + 10)
        self.animation.setEndValue(rect)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        rect = self.geometry()
        self.animation.setStartValue(rect)
        rect.setWidth(rect.width() - 10)
        self.animation.setEndValue(rect)
        self.animation.start()
        super().leaveEvent(event)


# ===================== DİALOG PENCERELERİ =====================

class TarifEkleDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("✨ Yeni Tarif Ekle")
        self.setGeometry(100, 100, 600, 650)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #2d2d3a);
                border-radius: 20px;
            }
            QLabel {
                color: #f5a623;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit, QComboBox, QSpinBox, QTextEdit {
                background-color: #0f0f1a;
                color: #ffffff;
                border: 2px solid #f5a623;
                border-radius: 12px;
                padding: 12px;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #4CAF50; }
        """)
        self.result = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        baslik = QLabel("✨ YENİ TARİF EKLE")
        baslik.setFont(QFont("Arial", 20, QFont.Bold))
        baslik.setStyleSheet("color: #f5a623;")
        baslik.setAlignment(Qt.AlignCenter)
        layout.addWidget(baslik)

        grid = QGridLayout()
        grid.setSpacing(15)

        grid.addWidget(QLabel("📖 Tarif Adı:"), 0, 0)
        self.ad_input = QLineEdit()
        self.ad_input.setPlaceholderText("Tarif adını girin")
        grid.addWidget(self.ad_input, 0, 1)

        grid.addWidget(QLabel("📚 Kategori:"), 1, 0)
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItems(self.db.kategorileri_getir())
        grid.addWidget(self.kategori_combo, 1, 1)

        grid.addWidget(QLabel("⏱️ Hazırlama Süresi (dk):"), 2, 0)
        self.sure_input = QSpinBox()
        self.sure_input.setRange(1, 600)
        self.sure_input.setValue(30)
        grid.addWidget(self.sure_input, 2, 1)

        grid.addWidget(QLabel("👨‍🍳 Talimat:"), 3, 0)
        self.talimat_input = QTextEdit()
        self.talimat_input.setMaximumHeight(150)
        self.talimat_input.setPlaceholderText("Tarifin yapılış adımlarını yazın...")
        grid.addWidget(self.talimat_input, 3, 1)

        layout.addLayout(grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        ekle_btn = LuxuryButton("✅ TARİF EKLE", "#4CAF50")
        ekle_btn.clicked.connect(self.ekle)
        iptal_btn = LuxuryButton("❌ İPTAL", "#e63946")
        iptal_btn.clicked.connect(self.reject)

        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(iptal_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def ekle(self):
        ad = self.ad_input.text().strip()
        if not ad:
            QMessageBox.warning(self, "Hata", "Tarif adı giriniz!")
            return
        self.result = (ad, self.kategori_combo.currentText(), self.sure_input.value(), self.talimat_input.toPlainText().strip())
        self.accept()


class MalzemeEkleDialog(QDialog):
    def __init__(self, db, tarif_id, tarif_adi, parent=None):
        super().__init__(parent)
        self.db = db
        self.tarif_id = tarif_id
        self.setWindowTitle(f"🥕 Malzeme Ekle - {tarif_adi}")
        self.setGeometry(100, 100, 450, 380)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #2d2d3a);
                border-radius: 20px;
            }
            QLabel {
                color: #4CAF50;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #0f0f1a;
                color: #ffffff;
                border: 2px solid #4CAF50;
                border-radius: 12px;
                padding: 12px;
                font-size: 12px;
            }
            QLineEdit:focus { border: 2px solid #f5a623; }
        """)
        self.result = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        baslik = QLabel("🥕 YENİ MALZEME")
        baslik.setFont(QFont("Arial", 18, QFont.Bold))
        baslik.setStyleSheet("color: #4CAF50;")
        baslik.setAlignment(Qt.AlignCenter)
        layout.addWidget(baslik)

        grid = QGridLayout()
        grid.setSpacing(15)

        grid.addWidget(QLabel("Malzeme Adı:"), 0, 0)
        self.malzeme_input = QLineEdit()
        self.malzeme_input.setPlaceholderText("Örn: Domates, Un, Yumurta")
        grid.addWidget(self.malzeme_input, 0, 1)

        grid.addWidget(QLabel("Miktar:"), 1, 0)
        self.miktar_input = QLineEdit()
        self.miktar_input.setPlaceholderText("Örn: 2 su bardağı, 250 gr")
        grid.addWidget(self.miktar_input, 1, 1)

        layout.addLayout(grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        ekle_btn = LuxuryButton("✅ MALZEME EKLE", "#4CAF50")
        ekle_btn.clicked.connect(self.ekle)
        iptal_btn = LuxuryButton("❌ İPTAL", "#e63946")
        iptal_btn.clicked.connect(self.reject)

        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(iptal_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def ekle(self):
        malzeme = self.malzeme_input.text().strip()
        miktar = self.miktar_input.text().strip()
        if not malzeme or not miktar:
            QMessageBox.warning(self, "Hata", "Malzeme adı ve miktar giriniz!")
            return
        self.result = (self.tarif_id, malzeme, miktar)
        self.accept()


class KullaniciEkleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("👤 Yeni Kullanıcı Ekle")
        self.setGeometry(100, 100, 450, 400)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #2d2d3a);
                border-radius: 20px;
            }
            QLabel {
                color: #f5a623;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #0f0f1a;
                color: #ffffff;
                border: 2px solid #f5a623;
                border-radius: 12px;
                padding: 12px;
                font-size: 12px;
            }
            QLineEdit:focus { border: 2px solid #4CAF50; }
        """)
        self.result = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        baslik = QLabel("👤 YENİ KULLANICI")
        baslik.setFont(QFont("Arial", 18, QFont.Bold))
        baslik.setStyleSheet("color: #f5a623;")
        baslik.setAlignment(Qt.AlignCenter)
        layout.addWidget(baslik)

        grid = QGridLayout()
        grid.setSpacing(15)

        grid.addWidget(QLabel("Ad:"), 0, 0)
        self.ad_input = QLineEdit()
        grid.addWidget(self.ad_input, 0, 1)

        grid.addWidget(QLabel("Soyad:"), 1, 0)
        self.soyad_input = QLineEdit()
        grid.addWidget(self.soyad_input, 1, 1)

        grid.addWidget(QLabel("Email:"), 2, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@email.com")
        grid.addWidget(self.email_input, 2, 1)

        layout.addLayout(grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        ekle_btn = LuxuryButton("✅ KULLANICI EKLE", "#4CAF50")
        ekle_btn.clicked.connect(self.ekle)
        iptal_btn = LuxuryButton("❌ İPTAL", "#e63946")
        iptal_btn.clicked.connect(self.reject)

        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(iptal_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def ekle(self):
        ad = self.ad_input.text().strip()
        soyad = self.soyad_input.text().strip()
        email = self.email_input.text().strip()
        if not ad or not soyad:
            QMessageBox.warning(self, "Hata", "Ad ve Soyad zorunludur!")
            return
        if email and "@" not in email:
            QMessageBox.warning(self, "Hata", "Geçerli bir email giriniz!")
            return
        self.result = (ad, soyad, email if email else None)
        self.accept()


class DegerlendirmeDialog(QDialog):
    def __init__(self, db, tarif_id, tarif_adi, parent=None):
        super().__init__(parent)
        self.db = db
        self.tarif_id = tarif_id
        self.setWindowTitle(f"⭐ Değerlendir - {tarif_adi}")
        self.setGeometry(100, 100, 450, 450)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #2d2d3a);
                border-radius: 20px;
            }
            QLabel {
                color: #f5a623;
                font-weight: bold;
                font-size: 12px;
            }
            QComboBox, QTextEdit {
                background-color: #0f0f1a;
                color: #ffffff;
                border: 2px solid #f5a623;
                border-radius: 12px;
                padding: 12px;
                font-size: 12px;
            }
            QComboBox:focus { border: 2px solid #4CAF50; }
        """)
        self.result = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        baslik = QLabel("⭐ TARİFİ DEĞERLENDİR")
        baslik.setFont(QFont("Arial", 18, QFont.Bold))
        baslik.setStyleSheet("color: #f5a623;")
        baslik.setAlignment(Qt.AlignCenter)
        layout.addWidget(baslik)

        grid = QGridLayout()
        grid.setSpacing(15)

        grid.addWidget(QLabel("Kullanıcı:"), 0, 0)
        self.kullanici_combo = QComboBox()
        for k in self.db.kullanicilari_getir():
            self.kullanici_combo.addItem(f"{k['ad']} {k['soyad']}", k['kullanici_id'])
        grid.addWidget(self.kullanici_combo, 0, 1)

        grid.addWidget(QLabel("Puan (1-5):"), 1, 0)
        self.puan_combo = QComboBox()
        self.puan_combo.addItems(["⭐⭐⭐⭐⭐ (5)", "⭐⭐⭐⭐ (4)", "⭐⭐⭐ (3)", "⭐⭐ (2)", "⭐ (1)"])
        grid.addWidget(self.puan_combo, 1, 1)

        grid.addWidget(QLabel("Yorum:"), 2, 0)
        self.yorum_input = QTextEdit()
        self.yorum_input.setMaximumHeight(100)
        self.yorum_input.setPlaceholderText("Tarif hakkında yorumunuz...")
        grid.addWidget(self.yorum_input, 2, 1)

        layout.addLayout(grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        kaydet_btn = LuxuryButton("✅ DEĞERLENDİR", "#4CAF50")
        kaydet_btn.clicked.connect(self.kaydet)
        iptal_btn = LuxuryButton("❌ İPTAL", "#e63946")
        iptal_btn.clicked.connect(self.reject)

        button_layout.addWidget(kaydet_btn)
        button_layout.addWidget(iptal_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def kaydet(self):
        puan_text = self.puan_combo.currentText()
        puan = int(puan_text.split("(")[1].split(")")[0])
        self.result = (self.tarif_id, self.kullanici_combo.currentData(), puan, self.yorum_input.toPlainText().strip())
        self.accept()


# ===================== GRAFİKLER =====================

class StatisticsWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.figure = Figure(figsize=(12, 5), dpi=100, facecolor='#1a1a2e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #1a1a2e; border-radius: 20px;")
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_charts(self):
        self.figure.clear()
        istatistikler = self.db.istatistikler()

        ax1 = self.figure.add_subplot(121)
        ax1.set_facecolor('#2d2d3a')
        if istatistikler['kategori_dagilimi']:
            kategoriler = [k['kategori'][:12] for k in istatistikler['kategori_dagilimi']]
            sayilar = [k['sayi'] for k in istatistikler['kategori_dagilimi']]
            colors = ['#f5a623', '#4CAF50', '#2196F3', '#e63946', '#9c27b0', '#00BCD4', '#795548', '#E91E63', '#607D8B']
            wedges, texts, autotexts = ax1.pie(sayilar, labels=kategoriler, autopct='%1.1f%%',
                                                colors=colors[:len(kategoriler)], startangle=90)
            for text in texts:
                text.set_color('#ffffff')
                text.set_fontsize(9)
            for autotext in autotexts:
                autotext.set_color('#ffffff')
                autotext.set_fontweight('bold')
            ax1.set_title('📊 Tarif Kategori Dağılımı', fontsize=12, fontweight='bold', color='#f5a623')

        ax2 = self.figure.add_subplot(122)
        ax2.set_facecolor('#2d2d3a')
        labels = ['📖 Tarifler', '📚 Kategoriler', '👥 Kullanıcılar', '⭐ Değerlendirmeler']
        values = [istatistikler['toplam_tarif'], istatistikler['toplam_kategori'],
                  istatistikler['toplam_kullanici'], istatistikler['toplam_degerlendirme']]
        colors = ['#f5a623', '#4CAF50', '#2196F3', '#e63946']
        bars = ax2.bar(labels, values, color=colors, edgecolor='none', width=0.6)
        ax2.set_title('📈 Sistem İstatistikleri', fontsize=12, fontweight='bold', color='#f5a623')
        ax2.set_ylabel('Sayı', fontsize=10, fontweight='bold', color='#ffffff')
        ax2.tick_params(axis='y', colors='#ffffff')
        ax2.tick_params(axis='x', colors='#ffffff', labelsize=10)

        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.3, f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold', fontsize=11, color='#f5a623')

        self.figure.tight_layout()
        self.canvas.draw()


# ===================== ANA PENCERE =====================

class YemekTarifPlatformu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setWindowTitle("🍽️ YEMEK TARİF PLATFORMU | LUXURY EDITION")
        self.setGeometry(50, 50, 1450, 900)

        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0f1a, stop:1 #1a1a2e);
            }
            QWidget {
                background-color: transparent;
            }
            QLabel {
                color: #ffffff;
            }
            QTableWidget {
                background-color: #2d2d3a;
                alternate-background-color: #3d3d4a;
                color: #ffffff;
                gridline-color: #4CAF50;
                border: none;
                border-radius: 15px;
            }
            QTableWidget::item {
                padding: 12px;
                color: #ffffff;
            }
            QTableWidget::item:selected {
                background-color: #f5a623;
                color: #1a1a2e;
            }
            QHeaderView::section {
                background-color: #1a1a2e;
                color: #f5a623;
                font-weight: bold;
                padding: 12px;
                border: none;
            }
            QComboBox, QLineEdit, QSpinBox, QTextEdit {
                background-color: #1a1a2e;
                border: 2px solid #f5a623;
                border-radius: 12px;
                padding: 10px;
                color: #ffffff;
                font-size: 12px;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a2e;
                color: #ffffff;
                selection-background-color: #f5a623;
            }
            QScrollBar:vertical {
                background-color: #2d2d3a;
                border-radius: 10px;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background-color: #f5a623;
                border-radius: 10px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4CAF50;
            }
        """)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # LUXURY HEADER
        header_widget = QFrame()
        header_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:0.3 #2d2d3a, stop:0.7 #2d2d3a, stop:1 #1a1a2e);
                border-radius: 25px;
                border: 1px solid #f5a623;
            }
        """)
        header_widget.setFixedHeight(100)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(40, 0, 40, 0)

        # Logo ve başlık
        logo_label = QLabel("🍽️")
        logo_label.setFont(QFont("Arial", 40))
        logo_label.setStyleSheet("color: #f5a623;")
        header_layout.addWidget(logo_label)

        title_layout = QVBoxLayout()
        title_label = QLabel("YEMEK TARİF PLATFORMU")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: #f5a623;")
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("LUXURY RECIPE MANAGEMENT SYSTEM")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #4CAF50; letter-spacing: 2px;")
        title_layout.addWidget(subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Sağ tarafta istatistik ve tarih
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)

        istatistik_label = QLabel("🍽️ 10+ Tarif | 📚 10 Kategori | 👥 4+ Kullanıcı")
        istatistik_label.setFont(QFont("Arial", 11))
        istatistik_label.setStyleSheet("color: #ffffff; background-color: #2d2d3a; padding: 8px 15px; border-radius: 20px;")
        right_layout.addWidget(istatistik_label)

        tarih_label = QLabel(datetime.now().strftime("%d %B %Y - %H:%M"))
        tarih_label.setFont(QFont("Arial", 11))
        tarih_label.setStyleSheet("color: #f5a623; background-color: #1a1a2e; padding: 8px 15px; border-radius: 20px;")
        right_layout.addWidget(tarih_label)

        right_widget.setLayout(right_layout)
        header_layout.addWidget(right_widget)

        header_widget.setLayout(header_layout)

        # DASHBOARD KARTLARI
        dashboard_layout = QHBoxLayout()
        dashboard_layout.setSpacing(20)

        self.tarif_card = self.create_luxury_card("📖 TOPLAM TARİFLER", "0", "#f5a623", "✨ Lezzetli Tarifler")
        self.kategori_card = self.create_luxury_card("📚 KATEGORİLER", "0", "#4CAF50", "🌸 Zengin Çeşitlilik")
        self.kullanici_card = self.create_luxury_card("👥 KULLANICILAR", "0", "#2196F3", "🌟 Aktif Kullanıcılar")
        self.puan_card = self.create_luxury_card("⭐ DEĞERLENDİRMELER", "0", "#e63946", "💬 Kullanıcı Yorumları")

        dashboard_layout.addWidget(self.tarif_card)
        dashboard_layout.addWidget(self.kategori_card)
        dashboard_layout.addWidget(self.kullanici_card)
        dashboard_layout.addWidget(self.puan_card)

        # LUXURY MENU (Yatay Butonlar - Sekme yerine)
        menu_widget = QFrame()
        menu_widget.setStyleSheet("""
            QFrame {
                background-color: #2d2d3a;
                border-radius: 20px;
            }
        """)
        menu_widget.setFixedHeight(60)
        menu_layout = QHBoxLayout()
        menu_layout.setContentsMargins(20, 0, 20, 0)
        menu_layout.setSpacing(10)

        self.menu_buttons = {}
        menu_items = [
            ("📖 TARİFLER", self.show_tarifler),
            ("👥 KULLANICILAR", self.show_kullanicilar),
            ("⭐ DEĞERLENDİRMELER", self.show_degerlendirmeler),
            ("📊 İSTATİSTİKLER", self.show_istatistikler)
        ]

        for text, func in menu_items:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #ffffff;
                    border: none;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px 30px;
                }
                QPushButton:hover {
                    background-color: #f5a623;
                    color: #1a1a2e;
                }
                QPushButton:checked {
                    background-color: #f5a623;
                    color: #1a1a2e;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(func)
            menu_layout.addWidget(btn)
            self.menu_buttons[text] = btn

        menu_layout.addStretch()
        menu_widget.setLayout(menu_layout)

        # STACKED WIDGET (Sekmeler için)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: transparent;
            }
        """)

        self.tarif_page = self.create_tarif_page()
        self.kullanici_page = self.create_kullanici_page()
        self.degerlendirme_page = self.create_degerlendirme_page()
        self.stats_page = StatisticsWidget(self.db)

        self.stacked_widget.addWidget(self.tarif_page)
        self.stacked_widget.addWidget(self.kullanici_page)
        self.stacked_widget.addWidget(self.degerlendirme_page)
        self.stacked_widget.addWidget(self.stats_page)

        # İlk butonu seçili yap
        self.menu_buttons["📖 TARİFLER"].setChecked(True)

        main_layout.addWidget(header_widget)
        main_layout.addLayout(dashboard_layout)
        main_layout.addWidget(menu_widget)
        main_layout.addWidget(self.stacked_widget)

        central_widget.setLayout(main_layout)

        # TIMER
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(5000)

    def create_luxury_card(self, title, value, color, subtitle):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d2d3a, stop:1 #1a1a2e);
                border-radius: 20px;
                border-left: 8px solid {color};
            }}
        """)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        title_label.setStyleSheet(f"color: {color};")

        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 32, QFont.Bold))
        value_label.setStyleSheet("color: #ffffff;")
        value_label.setObjectName("value_label")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Arial", 9))
        subtitle_label.setStyleSheet("color: #4CAF50;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        card.setLayout(layout)
        return card

    def show_tarifler(self):
        self.stacked_widget.setCurrentWidget(self.tarif_page)
        for btn in self.menu_buttons.values():
            btn.setChecked(False)
        self.menu_buttons["📖 TARİFLER"].setChecked(True)
        self.tarifleri_listele()

    def show_kullanicilar(self):
        self.stacked_widget.setCurrentWidget(self.kullanici_page)
        for btn in self.menu_buttons.values():
            btn.setChecked(False)
        self.menu_buttons["👥 KULLANICILAR"].setChecked(True)
        self.kullanicilari_listele()

    def show_degerlendirmeler(self):
        self.stacked_widget.setCurrentWidget(self.degerlendirme_page)
        for btn in self.menu_buttons.values():
            btn.setChecked(False)
        self.menu_buttons["⭐ DEĞERLENDİRMELER"].setChecked(True)
        self.degerlendirmeleri_listele()

    def show_istatistikler(self):
        self.stacked_widget.setCurrentWidget(self.stats_page)
        for btn in self.menu_buttons.values():
            btn.setChecked(False)
        self.menu_buttons["📊 İSTATİSTİKLER"].setChecked(True)
        self.stats_page.update_charts()

    def create_tarif_page(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Üst butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        ekle_btn = LuxuryButton("➕ YENİ TARİF", "#4CAF50")
        ekle_btn.clicked.connect(self.tarif_ekle)

        sil_btn = LuxuryButton("🗑️ TARİF SİL", "#e63946")
        sil_btn.clicked.connect(self.tarif_sil)

        malzeme_btn = LuxuryButton("🥕 MALZEME EKLE", "#2196F3")
        malzeme_btn.clicked.connect(self.malzeme_ekle)

        degerlendir_btn = LuxuryButton("⭐ DEĞERLENDİR", "#f5a623")
        degerlendir_btn.clicked.connect(self.degerlendir)

        yenile_btn = LuxuryButton("🔄 YENİLE", "#4CAF50")
        yenile_btn.clicked.connect(self.tarifleri_listele)

        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(sil_btn)
        button_layout.addWidget(malzeme_btn)
        button_layout.addWidget(degerlendir_btn)
        button_layout.addWidget(yenile_btn)
        button_layout.addStretch()

        # Kategori filtresi
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("🔍 Kategori Filtresi:"))
        self.kategori_filter = QComboBox()
        self.kategori_filter.addItem("📌 Tümü")
        self.kategori_filter.addItems(self.db.kategorileri_getir())
        self.kategori_filter.currentTextChanged.connect(self.tarifleri_listele)
        filter_layout.addWidget(self.kategori_filter)
        filter_layout.addStretch()

        # Tablo
        self.tarif_table = QTableWidget()
        self.tarif_table.setColumnCount(6)
        self.tarif_table.setHorizontalHeaderLabels(["ID", "TARİF ADI", "KATEGORİ", "SÜRE", "PUAN", "TALİMAT"])
        self.tarif_table.setAlternatingRowColors(True)
        self.tarif_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addLayout(button_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.tarif_table)
        widget.setLayout(layout)
        return widget

    def create_kullanici_page(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        ekle_btn = LuxuryButton("➕ YENİ KULLANICI", "#4CAF50")
        ekle_btn.clicked.connect(self.kullanici_ekle)

        sil_btn = LuxuryButton("🗑️ KULLANICI SİL", "#e63946")
        sil_btn.clicked.connect(self.kullanici_sil)

        yenile_btn = LuxuryButton("🔄 YENİLE", "#4CAF50")
        yenile_btn.clicked.connect(self.kullanicilari_listele)

        button_layout.addWidget(ekle_btn)
        button_layout.addWidget(sil_btn)
        button_layout.addWidget(yenile_btn)
        button_layout.addStretch()

        self.kullanici_table = QTableWidget()
        self.kullanici_table.setColumnCount(4)
        self.kullanici_table.setHorizontalHeaderLabels(["ID", "AD", "SOYAD", "EMAIL"])
        self.kullanici_table.setAlternatingRowColors(True)
        self.kullanici_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addLayout(button_layout)
        layout.addWidget(self.kullanici_table)
        widget.setLayout(layout)
        return widget

    def create_degerlendirme_page(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        yenile_btn = LuxuryButton("🔄 YENİLE", "#4CAF50")
        yenile_btn.clicked.connect(self.degerlendirmeleri_listele)

        self.degerlendirme_table = QTableWidget()
        self.degerlendirme_table.setColumnCount(5)
        self.degerlendirme_table.setHorizontalHeaderLabels(["TARİF", "KULLANICI", "PUAN", "YORUM", "TARİH"])
        self.degerlendirme_table.setAlternatingRowColors(True)
        self.degerlendirme_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(yenile_btn)
        layout.addWidget(self.degerlendirme_table)
        widget.setLayout(layout)
        return widget

    def load_data(self):
        self.tarifleri_listele()
        self.kullanicilari_listele()
        self.degerlendirmeleri_listele()
        self.update_dashboard()

    def refresh_all(self):
        self.tarifleri_listele()
        self.kullanicilari_listele()
        self.degerlendirmeleri_listele()
        self.update_dashboard()
        if self.stacked_widget.currentWidget() == self.stats_page:
            self.stats_page.update_charts()

    def update_dashboard(self):
        istatistikler = self.db.istatistikler()
        self.tarif_card.findChild(QLabel, "value_label").setText(str(istatistikler["toplam_tarif"]))
        self.kategori_card.findChild(QLabel, "value_label").setText(str(istatistikler["toplam_kategori"]))
        self.kullanici_card.findChild(QLabel, "value_label").setText(str(istatistikler["toplam_kullanici"]))
        self.puan_card.findChild(QLabel, "value_label").setText(str(istatistikler["toplam_degerlendirme"]))

    def tarifleri_listele(self):
        kategori = self.kategori_filter.currentText()
        tarifler = self.db.tarifleri_getir(kategori if kategori != "📌 Tümü" else None)
        self.tarif_table.setRowCount(0)

        for t in tarifler:
            row = self.tarif_table.rowCount()
            self.tarif_table.insertRow(row)

            puan = self.db.ortalama_puan(t['tarif_id'])

            self.tarif_table.setItem(row, 0, QTableWidgetItem(str(t['tarif_id'])))
            self.tarif_table.setItem(row, 1, QTableWidgetItem(t['ad']))
            self.tarif_table.setItem(row, 2, QTableWidgetItem(t['kategori']))
            self.tarif_table.setItem(row, 3, QTableWidgetItem(f"{t['hazirlama_suresi']} dk"))

            puan_item = QTableWidgetItem(f"⭐ {puan}" if puan > 0 else "⭐ Değerlendirilmemiş")
            if puan >= 4:
                puan_item.setForeground(QColor("#4CAF50"))
            elif puan >= 3:
                puan_item.setForeground(QColor("#f5a623"))
            else:
                puan_item.setForeground(QColor("#e63946"))
            self.tarif_table.setItem(row, 4, puan_item)

            self.tarif_table.setItem(row, 5, QTableWidgetItem(t['talimat'][:50] + "..." if t['talimat'] and len(t['talimat']) > 50 else t['talimat'] or '-'))

    def tarif_ekle(self):
        dialog = TarifEkleDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted and dialog.result:
            self.db.tarif_ekle(*dialog.result)
            QMessageBox.information(self, "Başarılı", "✅ Tarif başarıyla eklendi!")
            self.tarifleri_listele()
            self.update_dashboard()
            self.stats_page.update_charts()

    def tarif_sil(self):
        row = self.tarif_table.currentRow()
        if row >= 0:
            tarif_id = int(self.tarif_table.item(row, 0).text())
            tarif_adi = self.tarif_table.item(row, 1).text()
            reply = QMessageBox.question(self, "Silme Onayı", f"'{tarif_adi}' tarifini silmek istediğinize emin misiniz?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.tarif_sil(tarif_id)
                QMessageBox.information(self, "Başarılı", "✅ Tarif silindi!")
                self.tarifleri_listele()
                self.update_dashboard()
                self.stats_page.update_charts()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek tarifi seçin!")

    def malzeme_ekle(self):
        row = self.tarif_table.currentRow()
        if row >= 0:
            tarif_id = int(self.tarif_table.item(row, 0).text())
            tarif_adi = self.tarif_table.item(row, 1).text()

            dialog = MalzemeEkleDialog(self.db, tarif_id, tarif_adi, self)
            if dialog.exec_() == QDialog.Accepted and dialog.result:
                self.db.malzeme_ekle(*dialog.result)
                QMessageBox.information(self, "Başarılı", "✅ Malzeme başarıyla eklendi!")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir tarif seçin!")

    def kullanicilari_listele(self):
        kullanicilar = self.db.kullanicilari_getir()
        self.kullanici_table.setRowCount(0)
        for k in kullanicilar:
            row = self.kullanici_table.rowCount()
            self.kullanici_table.insertRow(row)
            self.kullanici_table.setItem(row, 0, QTableWidgetItem(str(k['kullanici_id'])))
            self.kullanici_table.setItem(row, 1, QTableWidgetItem(k['ad']))
            self.kullanici_table.setItem(row, 2, QTableWidgetItem(k['soyad']))
            self.kullanici_table.setItem(row, 3, QTableWidgetItem(k['email'] or '-'))

    def kullanici_ekle(self):
        dialog = KullaniciEkleDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.result:
            try:
                self.db.kullanici_ekle(*dialog.result)
                QMessageBox.information(self, "Başarılı", "✅ Kullanıcı başarıyla eklendi!")
                self.kullanicilari_listele()
                self.update_dashboard()
                self.stats_page.update_charts()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Hata", "Bu email adresi zaten kayıtlı!")

    def kullanici_sil(self):
        row = self.kullanici_table.currentRow()
        if row >= 0:
            kullanici_id = int(self.kullanici_table.item(row, 0).text())
            kullanici_adi = f"{self.kullanici_table.item(row, 1).text()} {self.kullanici_table.item(row, 2).text()}"
            reply = QMessageBox.question(self, "Silme Onayı", f"'{kullanici_adi}' kullanıcısını silmek istediğinize emin misiniz?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.kullanici_sil(kullanici_id)
                QMessageBox.information(self, "Başarılı", "✅ Kullanıcı silindi!")
                self.kullanicilari_listele()
                self.degerlendirmeleri_listele()
                self.update_dashboard()
                self.stats_page.update_charts()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek kullanıcıyı seçin!")

    def degerlendir(self):
        row = self.tarif_table.currentRow()
        if row >= 0:
            tarif_id = int(self.tarif_table.item(row, 0).text())
            tarif_adi = self.tarif_table.item(row, 1).text()

            if not self.db.kullanicilari_getir():
                QMessageBox.warning(self, "Uyarı", "Önce kullanıcı ekleyin!")
                return

            dialog = DegerlendirmeDialog(self.db, tarif_id, tarif_adi, self)
            if dialog.exec_() == QDialog.Accepted and dialog.result:
                self.db.degerlendirme_ekle(*dialog.result)
                QMessageBox.information(self, "Başarılı", "✅ Değerlendirme başarıyla kaydedildi!")
                self.tarifleri_listele()
                self.degerlendirmeleri_listele()
                self.update_dashboard()
                self.stats_page.update_charts()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir tarif seçin!")

    def degerlendirmeleri_listele(self):
        self.degerlendirme_table.setRowCount(0)
        tarifler = self.db.tarifleri_getir()
        for tarif in tarifler:
            degerlendirmeler = self.db.degerlendirmeleri_getir(tarif['tarif_id'])
            for d in degerlendirmeler:
                row = self.degerlendirme_table.rowCount()
                self.degerlendirme_table.insertRow(row)
                self.degerlendirme_table.setItem(row, 0, QTableWidgetItem(tarif['ad']))
                self.degerlendirme_table.setItem(row, 1, QTableWidgetItem(f"{d['ad']} {d['soyad']}"))

                puan_item = QTableWidgetItem(f"{'⭐' * d['puan']} ({d['puan']}/5)")
                if d['puan'] >= 4:
                    puan_item.setForeground(QColor("#4CAF50"))
                elif d['puan'] >= 3:
                    puan_item.setForeground(QColor("#f5a623"))
                else:
                    puan_item.setForeground(QColor("#e63946"))
                self.degerlendirme_table.setItem(row, 2, puan_item)
                self.degerlendirme_table.setItem(row, 3, QTableWidgetItem(d['yorum'][:40] + "..." if d['yorum'] and len(d['yorum']) > 40 else d['yorum'] or '-'))
                self.degerlendirme_table.setItem(row, 4, QTableWidgetItem(d['tarih'][:16]))


# ===================== MAIN =====================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = YemekTarifPlatformu()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
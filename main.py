from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                           QTableWidget, QTableWidgetItem, QComboBox, 
                           QMessageBox, QFileDialog, QDialog, QScrollArea, 
                           QGridLayout, QTextEdit, QTreeWidget, QTreeWidgetItem, 
                           QTabWidget, QGroupBox, QHeaderView, QCheckBox, 
                           QStackedWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont
import sys
import json
import pandas as pd
from datetime import datetime
import os
from PIL import Image, ImageDraw
import io
from currency_manager import CurrencyManager
from category_manager import CategoryTreeDialog
from trendyol_scraper import get_trendyol_categories

# Sabitler
PRODUCTS_FILE = "products.json"
MAX_IMAGES = 10
TRENDYOL_IMAGE_SIZE = (800, 1200)  # Trendyol'un önerdiği boyut
NO_IMAGE_PATH = "assets/no-image.png"  # Bu dosyayı projenizin assets klasörüne eklemelisiniz
CATEGORIES_FILE = "categories.json"

class ECommerceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        create_no_image()
        self.setWindowTitle("E-Ticaret Yönetim Paneli")
        self.setGeometry(100, 100, 1200, 800)
        
        # Stil tanımlamaları
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 8px;
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                background-color: #2196f3;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Üst panel
        top_panel = QHBoxLayout()
        
        # Arama kutusu
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ürün ara...")
        self.search_input.textChanged.connect(self.filter_products)
        top_panel.addWidget(self.search_input)
        
        # Kategori filtresi
        self.category_filter = QComboBox()
        self.category_filter.addItems(["Tüm Kategoriler", "Elektronik", "Giyim", "Ev & Yaşam"])
        self.category_filter.currentTextChanged.connect(self.filter_products)
        top_panel.addWidget(self.category_filter)
        
        # Butonlar
        add_button = QPushButton("Yeni Ürün Ekle")
        add_button.clicked.connect(self.show_add_product_dialog)
        top_panel.addWidget(add_button)
        
        import_button = QPushButton("Toplu Ürün Yükle")
        import_button.clicked.connect(self.import_products)
        top_panel.addWidget(import_button)
        
        # Döviz yöneticisi
        self.currency_manager = CurrencyManager()
        self.currency_manager.rates_updated.connect(self.update_currency_display)
        
        # Üst panel güncellemesi
        currency_button = QPushButton("Güncel Döviz Kurları")
        currency_button.clicked.connect(self.show_currency_rates)
        top_panel.addWidget(currency_button)
        
        # Kategori yönetimi
        manage_categories_button = QPushButton("Kategorileri Yönet")
        manage_categories_button.clicked.connect(self.show_category_manager)
        top_panel.addWidget(manage_categories_button)
        
        # Düşük stok kontrolü
        QTimer.singleShot(0, self.check_low_stock)
        
        layout.addLayout(top_panel)
        
        # Ürün tablosu
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(9)
        self.product_table.setHorizontalHeaderLabels([
            "Görsel", "ID", "Ürün Adı", "SKU", "Fiyat", "Stok", 
            "Kategori", "Etiketler", "İşlemler"
        ])
        
        # Sütun genişliklerini ayarla
        self.product_table.setColumnWidth(0, 100)  # Görsel
        self.product_table.setColumnWidth(1, 50)   # ID
        self.product_table.setColumnWidth(2, 200)  # Ürün Adı
        self.product_table.setColumnWidth(3, 100)  # SKU
        self.product_table.setColumnWidth(4, 100)  # Fiyat
        self.product_table.setColumnWidth(5, 80)   # Stok
        self.product_table.setColumnWidth(6, 150)  # Kategori
        self.product_table.setColumnWidth(7, 150)  # Etiketler
        self.product_table.setColumnWidth(8, 200)  # İşlemler
        
        # Sıralama özelliğini aktifleştir
        self.product_table.setSortingEnabled(True)
        
        # Satır yüksekliğini ayarla
        self.product_table.verticalHeader().setDefaultSectionSize(90)
        
        # Çift tıklama olayını bağla
        self.product_table.itemDoubleClicked.connect(self.show_product_details)
        
        # Tablo başlık stilini ayarla
        self.product_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #2196f3;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.product_table)
        
        # Ürünleri yükle
        self.load_products()
        
        # Alt bilgi paneli
        bottom_panel = QHBoxLayout()
        
        # Sol alt - Şirket bilgisi
        company_label = QLabel("© Easyso Connection Entegration")
        company_label.setStyleSheet("color: gray;")
        bottom_panel.addWidget(company_label)
        
        # Sağ alt - Saat ve tarih
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("color: gray;")
        bottom_panel.addWidget(self.datetime_label, alignment=Qt.AlignRight)
        
        # Saat güncelleyici
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Her saniye güncelle
        
        layout.addLayout(bottom_panel)
        
    def load_products(self):
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                products = json.load(f)
        else:
            # Örnek ürünler
            products = [
                {
                    "id": 1,
                    "name": "Akıllı Telefon X",
                    "sku": "SKU001",
                    "price": 5999.99,
                    "stock": 50,
                    "categories": ["Elektronik"],
                    "tags": ["Yeni", "Çok Satan"]
                },
                {
                    "id": 2,
                    "name": "Spor Ayakkabı Y",
                    "sku": "SKU002",
                    "price": 899.99,
                    "stock": 100,
                    "categories": ["Giyim"],
                    "tags": ["İndirimli"]
                }
            ]
            self.save_products(products)
        
        self.update_table(products)

    def save_products(self, products):
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
    def update_table(self, products):
        self.product_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Görsel önizleme
            img_label = QLabel()
            img_label.setFixedSize(80, 80)
            img_label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 2px;
                }
            """)
            
            if "images" in product and product["images"]:
                try:
                    img_data = bytes.fromhex(product["images"][0])
                    pixmap = QPixmap()
                    pixmap.loadFromData(img_data)
                    scaled_pixmap = pixmap.scaled(76, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                except Exception as e:
                    print(f"Görsel yükleme hatası: {e}")
                    scaled_pixmap = QPixmap(NO_IMAGE_PATH).scaled(76, 76, Qt.KeepAspectRatio)
            else:
                scaled_pixmap = QPixmap(NO_IMAGE_PATH).scaled(76, 76, Qt.KeepAspectRatio)
            
            img_label.setPixmap(scaled_pixmap)
            img_label.setAlignment(Qt.AlignCenter)
            self.product_table.setCellWidget(row, 0, img_label)
            
            # Diğer sütunlar için hizalama
            for col, value in enumerate([
                str(product["id"]),
                product["name"],
                product["sku"],
                f"₺{product['price']:.2f}",
                str(product["stock"]),
                ", ".join(product["categories"]),
                ", ".join(product["tags"])
            ], start=1):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.product_table.setItem(row, col, item)
            
            # Stok sütunu
            stock_item = QTableWidgetItem(str(product["stock"]))
            if product["stock"] <= 50:
                stock_item.setForeground(Qt.red)
                stock_item.setFont(QFont("", -1, QFont.Bold))
            stock_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.product_table.setItem(row, 5, stock_item)
            
            # Fiyat gösterimi
            price = product["price"]
            currency = product.get("currency", "TRY")
            
            if currency == "TRY":
                price_text = f"₺{price:.2f}"
            else:
                try:
                    # Döviz kurunu al ve TL karşılığını hesapla
                    tl_price = self.currency_manager.convert_to_try(price, currency)
                    
                    # Para birimi sembollerini belirle
                    currency_symbols = {
                        "USD": "$",
                        "EUR": "€",
                        "GBP": "£"
                    }
                    symbol = currency_symbols.get(currency, "")
                    
                    # Formatı: 250USD (7.525,00 TL)
                    price_text = f"{symbol}{price:.2f}{currency} ({tl_price:,.2f} TL)"
                    
                    # Binlik ayracını nokta, ondalık ayracını virgül yap
                    price_text = price_text.replace(",", "~").replace(".", ",").replace("~", ".")
                    
                except Exception as e:
                    print(f"Döviz çevirme hatası: {e}")
                    price_text = f"{symbol}{price:.2f} {currency}"
            
            price_item = QTableWidgetItem(price_text)
            price_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.product_table.setItem(row, 4, price_item)
            
            # İşlem butonları
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)  # Kenar boşluklarını kaldır
            
            # Detay butonu
            detail_button = QPushButton("Detaylar")
            detail_button.clicked.connect(lambda checked, p_id=product["id"]: self.show_product_details(p_id))
            actions_layout.addWidget(detail_button)
            
            # Silme butonu
            delete_button = QPushButton("Sil")
            delete_button.clicked.connect(lambda checked, p_id=product["id"]: self.delete_product(p_id))
            actions_layout.addWidget(delete_button)
            
            self.product_table.setCellWidget(row, 8, actions_widget)
            
    def delete_product(self, product_id):
        reply = QMessageBox.question(
            self, 
            'Ürün Silme', 
            'Bu ürünü silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            products = self.get_all_products()
            products = [p for p in products if p["id"] != product_id]
            self.save_products(products)
            self.update_table(products)
            
    def filter_products(self):
        search_text = self.search_input.text().lower()
        category = self.category_filter.currentText()
        
        all_products = self.get_all_products()
        filtered_products = []
        
        for product in all_products:
            name_match = search_text in product["name"].lower()
            sku_match = search_text in product["sku"].lower()
            category_match = (category == "Tüm Kategoriler" or 
                            category in product["categories"])
            
            if (name_match or sku_match) and category_match:
                filtered_products.append(product)
                
        self.update_table(filtered_products)
        
    def show_add_product_dialog(self):
        """Yeni ürün ekleme dialog'unu göster"""
        try:
            dialog = ProductDialog(self)  # AddProductDialog yerine ProductDialog kullan
            if dialog.exec_() == QDialog.Accepted:  # Dialog kabul edildiyse
                new_product = dialog.product  # get_product_data() yerine product özelliğini kullan
                if new_product:
                    all_products = self.get_all_products()
                    
                    # Yeni ID ve tarih bilgileri
                    max_id = max([p["id"] for p in all_products]) if all_products else 0
                    new_product.update({
                        "id": max_id + 1,
                        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "history": [f"Ürün oluşturuldu - {datetime.now().strftime('%d/%m/%Y %H:%M')}"]
                    })
                    
                    all_products.append(new_product)
                    self.save_products(all_products)
                    self.update_table(all_products)
                    
                    QMessageBox.information(self, "Başarılı", "Ürün başarıyla eklendi!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ürün eklenirken bir hata oluştu: {str(e)}")

    def import_products(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Excel/CSV Dosyası Seç",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
        )
        
        if file_name:
            try:
                if file_name.endswith('.csv'):
                    df = pd.read_csv(file_name)
                else:
                    df = pd.read_excel(file_name)
                    
                all_products = self.get_all_products()
                max_id = max([p["id"] for p in all_products]) if all_products else 0
                
                imported_products = []
                for _, row in df.iterrows():
                    max_id += 1
                    product = {
                        "id": max_id,
                        "name": row["name"],
                        "sku": row["sku"],
                        "price": float(row["price"]),
                        "stock": int(row["stock"]),
                        "categories": row.get("categories", "").split(","),
                        "tags": row.get("tags", "").split(",")
                    }
                    imported_products.append(product)
                    
                all_products.extend(imported_products)
                self.save_products(all_products)
                self.update_table(all_products)
                
                QMessageBox.information(
                    self,
                    "Başarılı",
                    f"{len(imported_products)} ürün başarıyla içe aktarıldı."
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Hata",
                    f"Dosya yüklenirken bir hata oluştu: {str(e)}"
                )
                
    def get_all_products(self):
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def update_datetime(self):
        current = datetime.now()
        time_str = current.strftime("%H:%M")
        date_str = current.strftime("%d/%m/%Y")
        self.datetime_label.setText(f"{time_str} | {date_str}")

    def show_product_details(self, product_id):
        try:
            product = next((p for p in self.get_all_products() if p["id"] == product_id), None)
            if product:
                details_dialog = ProductDetailsDialog(product, self)
                details_dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ürün detayları gösterilirken bir hata oluştu: {str(e)}")

    def check_low_stock(self):
        low_stock_products = [
            p for p in self.get_all_products()
            if p["stock"] <= 50
        ]
        
        if low_stock_products:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Düşük Stok Uyarısı")
            msg.setText("Aşağıdaki ürünlerin stok seviyesi düşük:")
            msg.setInformativeText("\n".join(
                f"• {p['name']} (Stok: {p['stock']})"
                for p in low_stock_products
            ))
            
            # 5 saniye sonra otomatik kapanma
            QTimer.singleShot(5000, msg.close)
            msg.show()
    
    def show_currency_rates(self):
        rates = self.currency_manager.rates
        last_update = self.currency_manager.last_update
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Güncel Döviz Kurları")
        msg.setText("Döviz Kurları:\n\n" + "\n".join(
            f"{currency}: {rate:.4f} TL"
            for currency, rate in rates.items()
        ))
        msg.setInformativeText(f"\nSon Güncelleme: {last_update.strftime('%H:%M:%S')}")
        msg.show()
    
    def show_category_manager(self):
        try:
            dialog = CategoryTreeDialog(self.get_categories(), self)
            if dialog.exec_() == QDialog.Accepted:  # Dialog kabul edildiyse
                self.save_categories(dialog.categories)
                self.update_category_filter(dialog.categories)
                QMessageBox.information(self, "Başarılı", "Kategoriler başarıyla kaydedildi!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kategori yönetimi sırasında bir hata oluştu: {str(e)}")

    def update_currency_display(self, rates):
        """Döviz kurları güncellendiğinde çağrılır"""
        try:
            # Fiyat sütunundaki tüm ürünleri güncelle
            all_products = self.get_all_products()
            for row in range(self.product_table.rowCount()):
                product = next((p for p in all_products if str(p["id"]) == self.product_table.item(row, 1).text()), None)
                if product:
                    # Ürünün para birimi ve fiyatı
                    price = product["price"]
                    currency = product.get("currency", "TRY")
                    
                    if currency == "TRY":
                        price_text = f"₺{price:,.2f}".replace(",", "~").replace(".", ",").replace("~", ".")
                    else:
                        try:
                            # Döviz kurunu al ve TL karşılığını hesapla
                            tl_price = self.currency_manager.convert_to_try(price, currency)
                            
                            # Para birimi sembollerini belirle
                            currency_symbols = {
                                "USD": "$",
                                "EUR": "€",
                                "GBP": "£"
                            }
                            symbol = currency_symbols.get(currency, "")
                            
                            # Formatı: $250,00USD (7.525,00 TL)
                            price_text = f"{symbol}{price:,.2f}{currency} ({tl_price:,.2f} TL)"
                            # Binlik ayracını nokta, ondalık ayracını virgül yap
                            price_text = price_text.replace(",", "~").replace(".", ",").replace("~", ".")
                            
                        except Exception as e:
                            print(f"Döviz çevirme hatası: {e}")
                            price_text = f"{symbol}{price:,.2f} {currency}".replace(",", "~").replace(".", ",").replace("~", ".")
                    
                    # Fiyat gösterimini güncelle
                    price_item = self.product_table.item(row, 4)
                    if price_item:
                        price_item.setText(price_text)
                        price_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        
        except Exception as e:
            print(f"Döviz kuru güncelleme hatası: {e}")

    def get_categories(self):
        """Kategorileri getir"""
        try:
            # Önce parent'tan kategorileri almayı dene
            if hasattr(self.parent(), 'get_categories'):
                return self.parent().get_categories()
            
            # Parent'ta yoksa varsayılan kategorileri döndür
            return [
                "Genel",
                "Elektronik",
                "Elektronik/Powerbank",
                "Elektronik/Telefon Aksesuarları",
                "Giyim",
                "Ev & Yaşam"
            ]
        except Exception as e:
            print(f"Kategori getirme hatası: {e}")
            return ["Genel"]  # Hata durumunda en azından bir kategori döndür

    def save_categories(self, categories):
        try:
            with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(categories, f, ensure_ascii=False, indent=2)
            # Kategori filtresini güncelle
            self.update_category_filter(categories)
        except Exception as e:
            print(f"Kategori kaydetme hatası: {e}")

    def update_category_filter(self, categories):
        self.category_filter.clear()
        self.category_filter.addItem("Tüm Kategoriler")
        
        def add_category_to_filter(category, prefix=""):
            if isinstance(category, dict):
                self.category_filter.addItem(f"{prefix}{category['name']}")
                for sub in category.get('sub_categories', []):
                    if isinstance(sub, dict):
                        add_category_to_filter(sub, prefix + "  ")
                    else:
                        self.category_filter.addItem(f"{prefix}  {sub}")
            else:
                self.category_filter.addItem(f"{prefix}{category}")
        
        for category in categories:
            add_category_to_filter(category)

    def switch_tab(self, tab_name):
        """Sekmeler arası geçiş"""
        if tab_name == "Genel Bilgiler":
            self.stack.setCurrentIndex(0)
        elif tab_name == "Resimler":
            if not hasattr(self, 'images_page'):
                self.setup_images_page()
            self.stack.setCurrentIndex(1)
        elif tab_name == "Uyumluluklar":
            if not hasattr(self, 'compatibility_page'):
                self.setup_compatibility_page()
            self.stack.setCurrentIndex(2)
        elif tab_name == "Önceki Satışlar":
            if not hasattr(self, 'sales_page'):
                self.setup_sales_page()
            self.stack.setCurrentIndex(3)

    def setup_images_page(self):
        """Resimler sekmesini oluştur"""
        self.images_page = QWidget()
        layout = QVBoxLayout(self.images_page)
        
        # Görsel yükleme alanı
        upload_group = QGroupBox("Görsel Yükleme")
        upload_layout = QVBoxLayout()
        
        # Sürükle-bırak alanı
        drop_area = QLabel("Görselleri buraya sürükleyin veya seçmek için tıklayın")
        drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                padding: 40px;
                background-color: #f8f9fa;
                color: #6c757d;
            }
        """)
        drop_area.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(drop_area)
        
        # Görsel seçme butonu
        select_btn = QPushButton("Görsel Seç")
        select_btn.clicked.connect(self.select_images)
        upload_layout.addWidget(select_btn)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        # Yüklenen görseller grid'i
        self.images_grid = QGridLayout()
        self.images_grid.setSpacing(10)
        
        images_group = QGroupBox("Yüklenen Görseller")
        images_group.setLayout(self.images_grid)
        layout.addWidget(images_group)
        
        self.stack.addWidget(self.images_page)

    def setup_compatibility_page(self):
        """Uyumluluklar sekmesini oluştur"""
        self.compatibility_page = QWidget()
        layout = QVBoxLayout(self.compatibility_page)
        
        # Uyumlu platformlar
        platforms_group = QGroupBox("Uyumlu Platformlar")
        platforms_layout = QVBoxLayout()
        
        platforms = ["N11", "Trendyol", "HepsiBurada", "GittiGidiyor", "Amazon"]
        self.platform_checkboxes = {}
        
        for platform in platforms:
            cb = QCheckBox(platform)
            self.platform_checkboxes[platform] = cb
            platforms_layout.addWidget(cb)
        
        platforms_group.setLayout(platforms_layout)
        layout.addWidget(platforms_group)
        
        # Platform özellikleri
        settings_group = QGroupBox("Platform Özellikleri")
        settings_layout = QGridLayout()
        
        # Platform bazlı özellikler...
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        self.stack.addWidget(self.compatibility_page)

    def setup_sales_page(self):
        """Önceki Satışlar sekmesini oluştur"""
        self.sales_page = QWidget()
        layout = QVBoxLayout(self.sales_page)
        
        # Satış istatistikleri
        stats_group = QGroupBox("Satış İstatistikleri")
        stats_layout = QGridLayout()
        
        stats = [
            ("Toplam Satış", "0"),
            ("Toplam Ciro", "0 TL"),
            ("Ortalama Satış Fiyatı", "0 TL"),
            ("İlk Satış Tarihi", "-"),
            ("Son Satış Tarihi", "-")
        ]
        
        for i, (label, value) in enumerate(stats):
            stats_layout.addWidget(QLabel(label), i, 0)
            stats_layout.addWidget(QLabel(value), i, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Satış geçmişi tablosu
        history_group = QGroupBox("Satış Geçmişi")
        history_layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Tarih", "Platform", "Miktar", "Birim Fiyat", "Toplam"
        ])
        
        history_layout.addWidget(table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        self.stack.addWidget(self.sales_page)

    def select_images(self):
        """Görsel seçme dialog'unu göster"""
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Görsel Seç",
            "",
            "Resim Dosyaları (*.png *.jpg *.jpeg)"
        )
        
        if file_names:
            self.add_images(file_names)

    def add_images(self, file_paths):
        """Seçilen görselleri grid'e ekle"""
        row = col = 0
        max_col = 4
        
        for path in file_paths:
            if col >= max_col:
                col = 0
                row += 1
            
            try:
                # Görsel container
                img_container = QWidget()
                container_layout = QVBoxLayout(img_container)
                
                # Görsel
                img_label = QLabel()
                img_label.setFixedSize(150, 150)
                pixmap = QPixmap(path).scaled(
                    146, 146,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                img_label.setPixmap(pixmap)
                img_label.setAlignment(Qt.AlignCenter)
                
                # Dosya adı
                name_label = QLabel(os.path.basename(path))
                name_label.setAlignment(Qt.AlignCenter)
                
                # Sil butonu
                delete_btn = QPushButton("Sil")
                delete_btn.clicked.connect(
                    lambda checked, w=img_container: w.deleteLater()
                )
                
                container_layout.addWidget(img_label)
                container_layout.addWidget(name_label)
                container_layout.addWidget(delete_btn)
                
                self.images_grid.addWidget(img_container, row, col)
                col += 1
                
            except Exception as e:
                print(f"Görsel yükleme hatası: {e}")

    def show_category_tree(self):
        """Kategori ağacını göster"""
        try:
            # Parent'tan kategorileri al
            categories = self.parent().get_categories() if hasattr(self.parent(), 'get_categories') else []
            
            dialog = CategoryTreeDialog(categories, self)
            if dialog.exec_() == QDialog.Accepted:
                selected = dialog.get_selected_category()
                if selected:
                    index = self.category_combo.findText(selected)
                    if index >= 0:
                        self.category_combo.setCurrentIndex(index)
                    else:
                        self.category_combo.addItem(selected)
                        self.category_combo.setCurrentText(selected)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kategori ağacı gösterilirken bir hata oluştu: {str(e)}")

    def get_parent_categories(self):
        """Ana kategorileri getir"""
        try:
            if os.path.exists(CATEGORIES_FILE):
                with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                    categories = json.load(f)
                    return [cat['name'] if isinstance(cat, dict) else cat for cat in categories]
            return ["Genel", "Elektronik", "Giyim", "Ev & Yaşam", "Powerbank"]
        except Exception as e:
            print(f"Ana kategori getirme hatası: {e}")
            return ["Genel", "Elektronik", "Giyim", "Ev & Yaşam", "Powerbank"]

    def show_critical_price_info(self):
        """Kritik fiyat bilgilendirmesi göster"""
        QMessageBox.information(
            self,
            "Kritik Fiyat Bilgisi",
            "Bu fiyat şu an için bu üründeki minimum satılabilir fiyattır. "
            "Bu fiyatın altında teklif verilemez."
        )

    def show_kdv_info(self):
        """KDV bilgilendirmesi göster"""
        QMessageBox.information(
            self,
            "KDV Bilgisi",
            "KDV dahil ise check box işaretlenir. "
            "KDV hariç fiyat ise check box boş bırakılır."
        )

    def limit_text(self, text_edit, max_length):
        """Text uzunluğunu sınırla"""
        text = text_edit.toPlainText()
        if len(text) > max_length:
            text_edit.setPlainText(text[:max_length])
            cursor = text_edit.textCursor()
            cursor.setPosition(max_length)
            text_edit.setTextCursor(cursor)

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product or {}
        self.setWindowTitle("Yeni Ürün" if not product else "Ürün Düzenle")
        self.setMinimumWidth(1000)
        self.setMinimumHeight(800)
        
        # Ana layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Üst buton grubu
        button_group = QHBoxLayout()
        buttons = ["Genel Bilgiler", "Resimler", "Uyumluluklar", "Önceki Satışlar"]
        
        for text in buttons:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 12px 24px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                    font-weight: bold;
                    min-width: 150px;
                }
                QPushButton:checked {
                    background-color: #0d6efd;
                    color: white;
                    border-color: #0a58ca;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                }
                QPushButton:checked:hover {
                    background-color: #0a58ca;
                }
            """)
            if text == "Genel Bilgiler":
                btn.setChecked(True)
            button_group.addWidget(btn)
            btn.clicked.connect(lambda checked, b=text: self.switch_tab(b))
        
        layout.addLayout(button_group)
        
        # Stacked widget for different tabs
        self.stack = QStackedWidget()
        
        # Genel Bilgiler sayfası
        general_page = QWidget()
        general_layout = QVBoxLayout(general_page)
        general_layout.setSpacing(20)
        
        # Zorunlu Alanlar Grubu
        required_group = QGroupBox("Zorunlu Alanlar")
        required_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #495057;
                padding: 0 10px;
                background-color: white;
                font-weight: bold;
            }
        """)
        required_layout = QGridLayout()
        required_layout.setSpacing(15)
        
        # Ürün Adı
        required_layout.addWidget(QLabel("Ürün Adı *"), 0, 0)
        self.name_input = QTextEdit()  # QLineEdit yerine QTextEdit kullan
        self.name_input.setMaximumHeight(100)  # Maksimum yükseklik
        self.name_input.setPlaceholderText("Ürün adını girin (maksimum 300 karakter)")
        self.name_input.textChanged.connect(lambda: self.limit_text(self.name_input, 300))
        required_layout.addWidget(self.name_input, 0, 1)
        
        # Stok Kodu
        required_layout.addWidget(QLabel("Stok Kodu *"), 1, 0)
        self.sku_input = QLineEdit()
        self.sku_input.setMaxLength(30)
        self.sku_input.setFixedWidth(200)
        self.sku_input.setPlaceholderText("Stok kodunu girin")
        required_layout.addWidget(self.sku_input, 1, 1)
        
        # Durum
        required_layout.addWidget(QLabel("Durum *"), 2, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Aktif", "Pasif"])
        self.status_combo.setFixedWidth(200)
        required_layout.addWidget(self.status_combo, 2, 1)
        
        # Kategori
        cat_layout = QHBoxLayout()
        required_layout.addWidget(QLabel("Kategori *"), 3, 0)
        self.category_combo = QComboBox()
        self.category_combo.setFixedWidth(200)
        self.category_combo.addItems(self.get_categories())
        cat_layout.addWidget(self.category_combo)
        
        cat_tree_btn = QPushButton("K")
        cat_tree_btn.setFixedSize(30, 30)
        cat_tree_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cat_tree_btn.clicked.connect(self.show_category_tree)
        cat_layout.addWidget(cat_tree_btn)
        cat_layout.addStretch()
        required_layout.addLayout(cat_layout, 3, 1)
        
        # Kampanya
        required_layout.addWidget(QLabel("Kampanya *"), 4, 0)
        self.campaign_combo = QComboBox()
        self.campaign_combo.addItems(["Hayır", "Evet"])
        self.campaign_combo.setFixedWidth(200)
        self.campaign_combo.currentTextChanged.connect(self.toggle_campaign_date)
        required_layout.addWidget(self.campaign_combo, 4, 1)
        
        # Kampanya Bitiş Tarihi
        self.campaign_date_label = QLabel("Kampanya Bitiş Tarihi *")
        self.campaign_date_label.hide()
        required_layout.addWidget(self.campaign_date_label, 5, 0)
        self.campaign_date = QLineEdit()
        self.campaign_date.setPlaceholderText("GG/AA/YYYY")
        self.campaign_date.setFixedWidth(200)
        self.campaign_date.hide()
        required_layout.addWidget(self.campaign_date, 5, 1)
        
        required_group.setLayout(required_layout)
        general_layout.addWidget(required_group)
        
        # Ek Alanlar Grubu
        extra_group = QGroupBox("Ek Alanlar")
        extra_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #495057;
                padding: 0 10px;
                background-color: white;
                font-weight: bold;
            }
        """)
        extra_layout = QGridLayout()
        extra_layout.setSpacing(15)

        extra_fields = {
            "Barkod": 30,
            "GTIN": 30,
            "MPN": 30,
            "GTIP": 30
        }

        self.extra_inputs = {}
        for i, (field, max_length) in enumerate(extra_fields.items()):
            extra_layout.addWidget(QLabel(field), i, 0)
            input_field = QLineEdit()
            input_field.setMaxLength(max_length)
            input_field.setFixedWidth(200)
            input_field.setPlaceholderText(f"{field} girin (max {max_length} karakter)")
            self.extra_inputs[field] = input_field
            extra_layout.addWidget(input_field, i, 1)

        extra_group.setLayout(extra_layout)
        general_layout.addWidget(extra_group)

        # Fiyatlar Grubu
        price_group = QGroupBox("Fiyatlar")
        price_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #495057;
                padding: 0 10px;
                background-color: white;
                font-weight: bold;
            }
        """)
        price_layout = QVBoxLayout()

        # Fiyat tablosu
        self.price_table = QTableWidget()
        self.price_table.setColumnCount(7)  # Kritik Fiyat + 5 Fiyat + KDV
        self.price_table.setRowCount(4)  # TRL, USD, EUR, GBP
        self.price_table.setHorizontalHeaderLabels([
            "Para Birimi", "Kritik Fiyat", "Fiyat 1", "Fiyat 2", 
            "Fiyat 3", "Fiyat 4", "KDV Dahil"
        ])
        self.price_table.setVerticalHeaderLabels(["TRL", "USD", "EUR", "GBP"])

        # Tablo stilini ayarla
        self.price_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        # Her para birimi için satırları oluştur
        for row in range(4):
            # Para birimi
            currency_item = QTableWidgetItem(["TRL", "USD", "EUR", "GBP"][row])
            currency_item.setTextAlignment(Qt.AlignCenter)
            self.price_table.setItem(row, 0, currency_item)
            
            # Kritik Fiyat (soru işareti ile)
            critical_widget = QWidget()
            critical_layout = QHBoxLayout(critical_widget)
            critical_layout.setContentsMargins(4, 0, 4, 0)
            critical_layout.setSpacing(4)
            
            critical_input = QLineEdit()
            critical_input.setFixedWidth(80)
            critical_layout.addWidget(critical_input)
            
            info_btn = QPushButton("?")
            info_btn.setFixedSize(20, 20)
            info_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            info_btn.clicked.connect(self.show_critical_price_info)
            critical_layout.addWidget(info_btn)
            
            self.price_table.setCellWidget(row, 1, critical_widget)
            
            # Fiyat kolonları
            for col in range(2, 6):
                price_input = QLineEdit()
                price_input.setFixedWidth(80)
                price_input.setAlignment(Qt.AlignCenter)
                self.price_table.setCellWidget(row, col, price_input)
            
            # KDV Dahil checkbox ve soru işareti
            kdv_widget = QWidget()
            kdv_layout = QHBoxLayout(kdv_widget)
            kdv_layout.setContentsMargins(4, 0, 4, 0)
            kdv_layout.setSpacing(4)
            
            checkbox = QCheckBox()
            checkbox.setChecked(True)  # Varsayılan olarak işaretli
            kdv_layout.addWidget(checkbox, alignment=Qt.AlignCenter)
            
            kdv_info_btn = QPushButton("?")
            kdv_info_btn.setFixedSize(20, 20)
            kdv_info_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            kdv_info_btn.clicked.connect(self.show_kdv_info)
            kdv_layout.addWidget(kdv_info_btn)
            
            self.price_table.setCellWidget(row, 6, kdv_widget)

        # Sütun genişliklerini ayarla
        self.price_table.setColumnWidth(0, 100)  # Para Birimi
        self.price_table.setColumnWidth(1, 120)  # Kritik Fiyat
        for i in range(2, 6):
            self.price_table.setColumnWidth(i, 100)  # Fiyatlar
        self.price_table.setColumnWidth(6, 120)  # KDV Dahil

        price_layout.addWidget(self.price_table)
        price_group.setLayout(price_layout)
        general_layout.addWidget(price_group)

        # Kaydet ve İptal butonları
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("İptal")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Kaydet")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_btn.clicked.connect(self.save_product)
        buttons_layout.addWidget(save_btn)

        general_layout.addLayout(buttons_layout)
        self.stack.addWidget(general_page)
        layout.addWidget(self.stack)

    def save_product(self):
        """Ürün verilerini doğrula ve kaydet"""
        # Zorunlu alanları kontrol et
        if not self.name_input.toPlainText().strip():
            self.name_input.setStyleSheet("border: 1px solid red;")
            QMessageBox.warning(self, "Uyarı", "Lütfen ürün adını girin!")
            return
        
        if not self.sku_input.text().strip():
            self.sku_input.setStyleSheet("border: 1px solid red;")
            QMessageBox.warning(self, "Uyarı", "Lütfen stok kodunu girin!")
            return
        
        # Kampanya tarihini kontrol et
        if self.campaign_combo.currentText() == "Evet":
            if not self.campaign_date.text().strip():
                self.campaign_date.setStyleSheet("border: 1px solid red;")
                QMessageBox.warning(self, "Uyarı", "Lütfen kampanya bitiş tarihini girin!")
                return
            try:
                datetime.strptime(self.campaign_date.text().strip(), "%d/%m/%Y")
            except ValueError:
                self.campaign_date.setStyleSheet("border: 1px solid red;")
                QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir tarih girin (GG/AA/YYYY)!")
                return
        
        try:
            # Ürün verilerini topla
            self.product = {
                "name": self.name_input.toPlainText().strip(),
                "sku": self.sku_input.text().strip(),
                "status": self.status_combo.currentText(),
                "category": self.category_combo.currentText(),
                "campaign": {
                    "active": self.campaign_combo.currentText() == "Evet",
                    "end_date": self.campaign_date.text().strip() if self.campaign_combo.currentText() == "Evet" else None
                },
                "extra_fields": {
                    field: widget.text().strip()
                    for field, widget in self.extra_inputs.items()
                },
                "prices": self.get_price_data()
            }
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ürün kaydedilirken bir hata oluştu: {str(e)}")

    def get_price_data(self):
        """Fiyat tablosundaki verileri al"""
        prices = {}
        currencies = ["TRL", "USD", "EUR", "GBP"]
        
        for row, currency in enumerate(currencies):
            prices[currency] = {
                "critical_price": self.get_cell_value(row, 1),
                "price1": self.get_cell_value(row, 2),
                "price2": self.get_cell_value(row, 3),
                "price3": self.get_cell_value(row, 4),
                "price4": self.get_cell_value(row, 5),
                "kdv_included": self.is_kdv_checked(row)
            }
        
        return prices

    def get_cell_value(self, row, col):
        """Tablodaki hücre değerini al"""
        try:
            widget = self.price_table.cellWidget(row, col)
            if isinstance(widget, QWidget):
                # Kritik Fiyat veya normal fiyat input'u
                input_widget = widget.layout().itemAt(0).widget()
                if isinstance(input_widget, QLineEdit):
                    value = input_widget.text().strip()
                    return float(value) if value else 0
            return 0
        except Exception:
            return 0

    def is_kdv_checked(self, row):
        """KDV checkbox durumunu kontrol et"""
        try:
            kdv_widget = self.price_table.cellWidget(row, 6)
            if kdv_widget:
                checkbox = kdv_widget.layout().itemAt(0).widget()
                return checkbox.isChecked()
            return False
        except Exception:
            return False

def create_no_image():
    """No-image placeholder oluştur"""
    if not os.path.exists('assets'):
        os.makedirs('assets')
        
    if not os.path.exists(NO_IMAGE_PATH):
        # 100x100 beyaz bir görsel oluştur
        img = Image.new('RGB', (100, 100), 'white')
        draw = ImageDraw.Draw(img)
        
        # Kenarlık çiz
        draw.rectangle([0, 0, 99, 99], outline='gray')
        
        # "No Image" yazısı ekle
        draw.text((20, 40), "No Image", fill='gray')
        
        # Görseli kaydet
        img.save(NO_IMAGE_PATH)

# Ana uygulama başlatma kodu
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = ECommerceApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Uygulama başlatılırken hata oluştu: {e}")

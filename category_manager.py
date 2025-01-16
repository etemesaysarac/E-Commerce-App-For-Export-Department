from PyQt5.QtWidgets import (QDialog, QTreeWidget, QTreeWidgetItem, QPushButton,
                           QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox)

class CategoryTreeDialog(QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kategori Ağacı")
        self.setMinimumSize(400, 500)
        self.categories = categories or []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Kategori ağacı
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Kategoriler")
        layout.addWidget(self.tree)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        add_main = QPushButton("Ana Kategori Ekle")
        add_main.clicked.connect(self.add_main_category)
        
        add_sub = QPushButton("Alt Kategori Ekle")
        add_sub.clicked.connect(self.add_sub_category)
        
        delete_btn = QPushButton("Kategori Sil")
        delete_btn.clicked.connect(self.delete_category)
        
        button_layout.addWidget(add_main)
        button_layout.addWidget(add_sub)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        # Kaydet ve İptal butonları
        save_cancel_layout = QHBoxLayout()
        save_btn = QPushButton("Kaydet")
        save_btn.clicked.connect(self.save_and_close)
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        
        save_cancel_layout.addWidget(cancel_btn)
        save_cancel_layout.addWidget(save_btn)
        layout.addLayout(save_cancel_layout)
        
        # Mevcut kategorileri yükle
        self.load_categories()
    
    def load_categories(self):
        def add_category_to_tree(category, parent=None):
            if isinstance(category, dict):
                item = QTreeWidgetItem([category['name']])
                if parent:
                    parent.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)
                for sub in category.get('sub_categories', []):
                    add_category_to_tree(sub, item)
            else:
                item = QTreeWidgetItem([category])
                if parent:
                    parent.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)
        
        for category in self.categories:
            add_category_to_tree(category)
    
    def add_main_category(self):
        name, ok = QInputDialog.getText(self, "Yeni Kategori", "Kategori Adı:")
        if ok and name:
            item = QTreeWidgetItem([name])
            self.tree.addTopLevelItem(item)
    
    def add_sub_category(self):
        current = self.tree.currentItem()
        if not current:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir kategori seçin!")
            return
        
        name, ok = QInputDialog.getText(self, "Yeni Alt Kategori", "Kategori Adı:")
        if ok and name:
            item = QTreeWidgetItem([name])
            current.addChild(item)
    
    def delete_category(self):
        current = self.tree.currentItem()
        if not current:
            return
            
        reply = QMessageBox.question(
            self, "Kategori Sil",
            "Bu kategoriyi silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if current.parent():
                current.parent().removeChild(current)
            else:
                self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(current))
            self.save_categories()
    
    def save_categories(self):
        def get_category_data(item):
            if item.childCount() > 0:
                return {
                    'name': item.text(0),
                    'sub_categories': [
                        get_category_data(item.child(i))
                        for i in range(item.childCount())
                    ]
                }
            return item.text(0)
        
        categories = []
        for i in range(self.tree.topLevelItemCount()):
            categories.append(get_category_data(self.tree.topLevelItem(i)))
        
        self.categories = categories
        return categories 
    
    def save_and_close(self):
        """Kategorileri kaydet ve pencereyi kapat"""
        self.categories = self.save_categories()
        self.accept()  # Dialog'u kabul et ve kapat 
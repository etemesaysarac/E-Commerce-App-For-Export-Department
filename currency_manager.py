from PyQt5.QtCore import QObject, pyqtSignal
import requests
from datetime import datetime
import json
import os

class CurrencyManager(QObject):
    rates_updated = pyqtSignal(dict)  # Kurlar güncellendiğinde sinyal gönder

    def __init__(self):
        super().__init__()
        self.rates = {
            "USD": 0.0,
            "EUR": 0.0,
            "GBP": 0.0
        }
        self.last_update = None
        self.load_cached_rates()
        self.update_rates()

    def load_cached_rates(self):
        """Kaydedilmiş kurları yükle"""
        try:
            if os.path.exists('cached_rates.json'):
                with open('cached_rates.json', 'r') as f:
                    data = json.load(f)
                    self.rates = data['rates']
                    self.last_update = datetime.fromisoformat(data['last_update'])
        except Exception as e:
            print(f"Kur cache yükleme hatası: {e}")

    def save_cached_rates(self):
        """Güncel kurları kaydet"""
        try:
            with open('cached_rates.json', 'w') as f:
                json.dump({
                    'rates': self.rates,
                    'last_update': self.last_update.isoformat()
                }, f)
        except Exception as e:
            print(f"Kur cache kaydetme hatası: {e}")

    def update_rates(self):
        """Döviz kurlarını güncelle"""
        try:
            # TCMB API'den güncel kurları al
            response = requests.get('https://api.exchangerate-api.com/v4/latest/TRY')
            data = response.json()
            
            # Kurları güncelle
            self.rates = {
                "USD": 1 / data['rates']['USD'],
                "EUR": 1 / data['rates']['EUR'],
                "GBP": 1 / data['rates']['GBP']
            }
            
            self.last_update = datetime.now()
            self.save_cached_rates()
            self.rates_updated.emit(self.rates)
            
        except Exception as e:
            print(f"Kur güncelleme hatası: {e}")
            # Hata durumunda varsayılan kurları kullan
            if not self.rates['USD']:
                self.rates = {
                    "USD": 31.50,
                    "EUR": 34.20,
                    "GBP": 39.80
                }

    def convert_to_try(self, amount, from_currency):
        """Dövizi TL'ye çevir"""
        if from_currency == "TRY":
            return amount
        
        rate = self.rates.get(from_currency)
        if rate:
            return amount * rate
        return amount  # Kur bulunamazsa aynı değeri döndür

    def convert_currency(self, amount, from_currency, to_currency):
        """Dövizler arası çevrim"""
        if from_currency == to_currency:
            return amount
            
        # Önce TL'ye çevir
        try_amount = self.convert_to_try(amount, from_currency)
        
        # TL'den hedef dövize çevir
        if to_currency == "TRY":
            return try_amount
            
        rate = self.rates.get(to_currency)
        if rate:
            return try_amount / rate
        return amount 
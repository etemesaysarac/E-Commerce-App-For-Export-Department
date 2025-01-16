import requests
from datetime import datetime
from PyQt5.QtCore import QTimer, pyqtSignal, QObject

class CurrencyManager(QObject):
    rates_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.base_currency = "TRY"
        self.currencies = ["USD", "EUR", "GBP"]
        self.rates = {}
        self.last_update = None
        
        # TCMB API endpoint
        self.api_url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        
        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_rates)
        self.timer.start(10000)  # 10 saniye
        
        # İlk güncelleme
        self.update_rates()
    
    def update_rates(self):
        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                # XML parse işlemi
                from xml.etree import ElementTree
                root = ElementTree.fromstring(response.content)
                
                new_rates = {}
                for currency in root.findall(".//Currency"):
                    code = currency.get('Kod')
                    if code in self.currencies:
                        rate = float(currency.find('ForexBuying').text)
                        new_rates[code] = rate
                
                self.rates = new_rates
                self.last_update = datetime.now()
                self.rates_updated.emit(self.rates)
        except Exception as e:
            print(f"Döviz kuru güncelleme hatası: {e}")
    
    def convert_to_try(self, amount, currency):
        if currency == "TRY":
            return amount
        return amount * self.rates.get(currency, 0)
    
    def convert_from_try(self, amount, currency):
        if currency == "TRY":
            return amount
        return amount / self.rates.get(currency, 1) 
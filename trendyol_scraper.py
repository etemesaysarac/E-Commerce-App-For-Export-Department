import requests
from bs4 import BeautifulSoup

def get_trendyol_categories():
    try:
        url = "https://www.trendyol.com/butik/liste/1/kadin"
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = []
        
        # Ana kategoriler
        main_categories = soup.select('nav.category-nav ul.category-nav-list > li')
        
        for main_cat in main_categories:
            main_name = main_cat.find('a').text.strip()
            sub_categories = []
            
            # Alt kategoriler
            sub_cats = main_cat.select('div.sub-category-list a')
            for sub_cat in sub_cats:
                sub_categories.append(sub_cat.text.strip())
            
            categories.append({
                'name': main_name,
                'sub_categories': sub_categories
            })
        
        return categories
    except Exception as e:
        print(f"Kategori çekme hatası: {e}")
        return [] 
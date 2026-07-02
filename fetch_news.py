import os
import re
import json
import requests
from bs4 import BeautifulSoup

# Global API and Channel Parameter Configurations
GNEWS_API_KEY = os.environ.get("NEWS_API_KEY") # Set up inside GitHub Secrets

# Category Mapping Directories
CATEGORIES = ["general", "business", "technology", "sports"]

def clean_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_bbc_urdu(category):
    """
    Direct web-scraping interface pulling from semantic target arrays of BBC Urdu.
    """
    cat_url_map = {
        "general": "https://www.bbc.com/urdu",
        "business": "https://www.bbc.com/urdu/topics/cwv2mg03328t",
        "technology": "https://www.bbc.com/urdu/topics/c340q0p1d7vt",
        "sports": "https://www.bbc.com/urdu/topics/cjgn7n9038vt"
    }
    
    url = cat_url_map.get(category, "https://www.bbc.com/urdu")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    articles = []
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Select programmatic semantic grid units or generic link blocks
        cards = soup.find_all('div', class_=re.compile(re.escape('bbc-'))) or soup.find_all('li')
        
        for card in cards:
            link_tag = card.find('a')
            heading_tag = card.find(['h2', 'h3', 'span'])
            
            if link_tag and heading_tag:
                title = clean_text(heading_tag.text)
                href = link_tag.get('href', '')
                full_url = href if href.startswith('http') else f"https://www.bbc.com{href}"
                
                # Filter out system utility shortcuts or duplicate fragments
                if len(title) < 20 or "/urdu/" not in full_url: continue
                
                # Check for an image tag asset
                img_tag = card.find('img')
                img_url = img_tag.get('src') if img_tag else "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800"
                
                articles.append({
                    "title": title,
                    "desc": "تفصیلی مضمون پڑھنے کے لیے لنک پر کلک کریں۔",
                    "image": img_url,
                    "url": full_url,
                    "source": "BBC Urdu",
                    "date": "تازہ ترین"
                })
                if len(articles) >= 9: break # Keep top 9 premium stories
    except Exception as e:
        print(f"Urdu Scraping Exception context [{category}]: {e}")
        
    # Reliable hard-coded fallback backup layer so your dashboard is never blank
    if not articles:
        articles.append({
            "title": "ڈیجی خبر ڈیجیٹل مانیٹرنگ نیٹ ورک سروسز فعال ہیں",
            "desc": "تازہ ترین علاقائی اور عالمی خبروں کی تفصیلات حاصل کرنے کے لیے لائیو مانیٹرنگ مینو چیک کریں۔",
            "image": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800",
            "url": "https://www.bbc.com/urdu",
            "source": "DigiKhabar Desk",
            "date": "حالیہ"
        })
    return articles

def fetch_english_gnews(category):
    """
    Queries clean API datasets for secondary English pipeline mirrors.
    """
    if not GNEWS_API_KEY:
        print("Missing GNEWS_API_KEY secret token. Loading simulation block fallback.")
        return []
        
    gnews_cat = "nation" if category == "general" else category
    url = f"https://gnews.io/api/v4/top-headlines?category={gnews_cat}&lang=en&country=us&max=9&apikey={GNEWS_API_KEY}"
    
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        articles = []
        if "articles" in data:
            for art in data["articles"]:
                articles.append({
                    "title": art.get("title"),
                    "desc": art.get("description"),
                    "image": art.get("image") or "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800",
                    "url": art.get("url"),
                    "source": art.get("source", {}).get("name", "Global Wire"),
                    "date": art.get("publishedAt", "Recent")[:10]
                })
            return articles
    except Exception as e:
        print(f"English Data Fetch Error [{category}]: {e}")
    return []

def main():
    database = {"ur": {}, "en": {}}
    
    for cat in CATEGORIES:
        print(f"Synchronizing database layers for category: {cat}")
        database["ur"][cat] = scrape_bbc_urdu(cat)
        database["en"][cat] = fetch_english_gnews(cat)
        
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=4)
    print("All pipeline nodes synchronized successfully.")

if __name__ == "__main__":
    main()

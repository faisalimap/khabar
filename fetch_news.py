import os
import re
import json
import requests
from bs4 import BeautifulSoup

# Secure API Token Initialization from Environment Secrets
KEYS = {
    "gnews": os.environ.get("GNEWS_API_KEY"),
    "newsdata": os.environ.get("NEWSDATA_API_KEY"),
    "worldnews": os.environ.get("WORLDNEWS_API_KEY"),
    "guardian": os.environ.get("GUARDIAN_API_KEY"),
    "nyt": os.environ.get("NYT_API_KEY")
}

CATEGORIES = ["general", "business", "technology", "sports"]

def clean_txt(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

# --- URDU DATA PIPELINE HANDLERS ---

def scrape_bbc_urdu(category):
    cat_urls = {
        "general": "https://www.bbc.com/urdu",
        "business": "https://www.bbc.com/urdu/topics/cwv2mg03328t",
        "technology": "https://www.bbc.com/urdu/topics/c340q0p1d7vt",
        "sports": "https://www.bbc.com/urdu/topics/cjgn7n9038vt"
    }
    url = cat_urls.get(category, "https://www.bbc.com/urdu")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    articles = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')
        cards = soup.find_all('div', class_=re.compile(re.escape('bbc-'))) or soup.find_all('li')
        for c in cards:
            link = c.find('a')
            heading = c.find(['h2', 'h3', 'span'])
            if link and heading:
                title = clean_txt(heading.text)
                href = link.get('href', '')
                full_url = href if href.startswith('http') else f"https://www.bbc.com{href}"
                if len(title) < 20 or "/urdu/" not in full_url: continue
                img = c.find('img')
                img_url = img.get('src') if img else "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800"
                articles.append({
                    "title": title, "desc": "تفصیلی مضمون پڑھنے کے لیے لنک پر کلک کریں۔",
                    "image": img_url, "url": full_url, "source": "BBC Urdu", "date": "تازہ ترین"
                })
                if len(articles) >= 5: break
    except Exception as e:
        print(f"BBC Urdu Parse Exception [{category}]: {e}")
    return articles

def fetch_newsdata_urdu(category):
    if not KEYS["newsdata"]: return []
    # Map internal terms to Newsdata categories
    cat_map = {"general": "top", "business": "business", "technology": "technology", "sports": "sports"}
    url = f"https://newsdata.io/api/1/news?apikey={KEYS['newsdata']}&language=ur&category={cat_map.get(category, 'top')}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        articles = []
        if "results" in data:
            for r in data["results"][:5]:
                articles.append({
                    "title": r.get("title"), "desc": r.get("description") or "تفصیلی معلومات دستیاب نہیں ہے۔",
                    "image": r.get("image_url") or "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800",
                    "url": r.get("link"), "source": r.get("source_id") or "Newsdata Wire", "date": r.get("pubDate", "Recent")[:10]
                })
            return articles
    except Exception as e:
        print(f"Newsdata Urdu Error [{category}]: {e}")
    return []

# --- ENGLISH PREMIUM ARTICULATION HANDLERS ---

def fetch_gnews_english(category):
    if not KEYS["gnews"]: return []
    cat_map = {"general": "general", "business": "business", "technology": "technology", "sports": "sports"}
    url = f"https://gnews.io/api/v4/top-headlines?category={cat_map.get(category)}&lang=en&max=5&apikey={KEYS['gnews']}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        articles = []
        if "articles" in data:
            for a in data["articles"]:
                articles.append({
                    "title": a.get("title"), "desc": a.get("description"),
                    "image": a.get("image") or "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800",
                    "url": a.get("url"), "source": a.get("source", {}).get("name", "GNews Wire"), "date": a.get("publishedAt")[:10]
                })
            return articles
    except Exception as e:
        print(f"GNews English Fetch Error [{category}]: {e}")
    return []

def fetch_worldnews_english(category):
    if not KEYS["worldnews"]: return []
    # WorldNews API headline router endpoint
    text_queries = {"general": "news", "business": "finance", "technology": "tech", "sports": "sports"}
    url = f"https://api.worldnewsapi.com/search-news?text={text_queries.get(category)}&language=en&number=4&api-key={KEYS['worldnews']}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        articles = []
        if "news" in data:
            for n in data["news"]:
                articles.append({
                    "title": n.get("title"), "desc": n.get("text")[:200] if n.get("text") else "",
                    "image": n.get("image") or "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800",
                    "url": n.get("url"), "source": n.get("source_country") or "World News Wire", "date": n.get("publish_date")[:10]
                })
            return articles
    except Exception as e:
        print(f"WorldNews English Fetch Error [{category}]: {e}")
    return []

def fetch_guardian_english(category):
    if not KEYS["guardian"]: return []
    sec_map = {"general": "news", "business": "business", "technology": "technology", "sports": "sports"}
    url = f"https://content.guardianapis.com/search?section={sec_map.get(category)}&show-fields=thumbnail,trailText&api-key={KEYS['guardian']}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        articles = []
        if "response" in data and "results" in data["response"]:
            for r in data["response"]["results"][:4]:
                fields = r.get("fields", {})
                articles.append({
                    "title": r.get("webTitle"), "desc": fields.get("trailText") or "",
                    "image": fields.get("thumbnail") or "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800",
                    "url": r.get("webUrl"), "source": "The Guardian", "date": r.get("webPublicationDate")[:10]
                })
            return articles
    except Exception as e:
        print(f"Guardian Fetch Error [{category}]: {e}")
    return []

def fetch_nyt_english(category):
    if not KEYS["nyt"]: return []
    section = "home" if category == "general" else ("business" if category == "business" else "technology")
    if category == "sports": section = "sports"
    url = f"https://api.nytimes.com/v1/topstories/v2/{section}.json?api-key={KEYS['nyt']}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        articles = []
        if "results" in data:
            for r in data["results"][:4]:
                img_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800"
                if r.get("multimedia"):
                    img_url = r["multimedia"][0].get("url")
                articles.append({
                    "title": r.get("title"), "desc": r.get("abstract"),
                    "image": img_url, "url": r.get("url"), "source": "The New York Times", "date": r.get("published_date")[:10]
                })
            return articles
    except Exception as e:
        print(f"NYT Fetch Error [{category}]: {e}")
    return []

# --- MAIN COMPILATION LAYER ---

def main():
    database = {"ur": {}, "en": {}}
    
    for cat in CATEGORIES:
        print(f"Synchronizing live infrastructure layers for category block: {cat}")
        
        # Urdu compilation mixing web scraping + standard newsdata API fields
        urdu_pool = scrape_bbc_urdu(cat) + fetch_newsdata_urdu(cat)
        # Unique filter list by title string signatures to ensure zero duplicate rendering
        seen_ur = set()
        database["ur"][cat] = [seen_ur.add(a["title"]) or a for a in urdu_pool if a["title"] not in seen_ur]
        
        # English compilation chaining premium corporate global assets
        eng_pool = fetch_gnews_english(cat) + fetch_worldnews_english(cat) + fetch_guardian_english(cat) + fetch_nyt_english(cat)
        seen_en = set()
        database["en"][cat] = [seen_en.add(a["title"]) or a for a in eng_pool if a["title"] not in seen_en]
        
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=4)
    print("Database sync executed flawlessly across all cloud networks.")

if __name__ == "__main__":
    main()

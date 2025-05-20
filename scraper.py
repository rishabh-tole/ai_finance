import requests
import feedparser
from bs4 import BeautifulSoup
import re
from textblob import TextBlob

# RSS Feeds
RSS_FEEDS = [
    "https://www.energyintel.com/rss-feed",
]

EXCLUDED_DOMAINS = ["facebook.com", "twitter.com", "linkedin.com", "youtube.com", "x.com", "flickr.com"]

# List of top energy stocks (ticker symbols and full forms)
ENERGY_STOCKS = {
    "XOM": "Exxon Mobil",
    "CVX": "Chevron",
    "COP": "ConocoPhillips",
    "EOG": "EOG Resources",
    "PXD": "Pioneer Natural Resources",
    "MPC": "Marathon Petroleum",
    "PSX": "Phillips 66",
    "OXY": "Occidental Petroleum",
    "VLO": "Valero Energy",
    "HES": "Hess Corporation",
    "SLB": "Schlumberger",
    "BKR": "Baker Hughes",
    "HAL": "Halliburton",
    "FANG": "Diamondback Energy",
    "WMB": "Williams Companies",
    "KMI": "Kinder Morgan",
    "OKE": "ONEOK",
    "ET": "Energy Transfer",
    "EPD": "Enterprise Products Partners",
    "LNG": "Cheniere Energy",
    "MRO": "Marathon Oil",
    "DVN": "Devon Energy",
    "APA": "APA Corporation",
    "CTRA": "Coterra Energy",
    "BCEI": "Bonanza Creek Energy",
    "ENB": "Enbridge",
    "TRP": "TC Energy",
    "TELL": "Tellurian",
    "CHX": "ChampionX Corporation",
    "CVE": "Cenovus Energy",
    "SU": "Suncor Energy",
    "IMO": "Imperial Oil",
    "RRC": "Range Resources",
    "SWN": "Southwestern Energy",
    "AR": "Antero Resources",
    "EQT": "EQT Corporation"
}

def extract_links_from_rss():
    """Extracts article links from RSS feeds and filters out junk links."""
    links = []
    for feed_url in RSS_FEEDS:
        print(f"Fetching RSS feed: {feed_url}")
        response = requests.get(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            feed = feedparser.parse(response.text)
            if not feed.entries:
                print(f"No entries found in {feed_url}, checking HTML.")
                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    if "http" in link["href"] and not any(domain in link["href"] for domain in EXCLUDED_DOMAINS):
                        links.append(link["href"])
            else:
                for entry in feed.entries:
                    if not any(domain in entry.link for domain in EXCLUDED_DOMAINS):
                        links.append(entry.link)
        else:
            print(f"Failed to fetch {feed_url}, status code: {response.status_code}")
    return links

def scrape_article(url):
    """Scrapes full text from an article URL."""
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

def analyze_sentiment(text):
    """Performs sentiment analysis on energy stock mentions."""
    stock_mentions = {stock: text.count(stock) for stock in ENERGY_STOCKS if stock in text or ENERGY_STOCKS[stock] in text}
    sentiment_results = {}
    
    for stock, mentions in stock_mentions.items():
        sentiment_score = TextBlob(text).sentiment.polarity
        
        if sentiment_score > 0.3:
            indicator = "Strong Bullish"
            decision = "BUY"
        elif 0.1 <= sentiment_score <= 0.3:
            indicator = "Moderate Bullish"
            decision = "CONSIDER BUYING"
        elif -0.1 <= sentiment_score <= 0.1:
            indicator = "Neutral"
            decision = "STANDBY"
        elif -0.3 <= sentiment_score < -0.1:
            indicator = "Moderate Bearish"
            decision = "CONSIDER SELLING"
        else:
            indicator = "Strong Bearish"
            decision = "SELL"
        
        sentiment_results[stock] = {
            "mentions": mentions,
            "sentiment_score": sentiment_score,
            "indicator": indicator,
            "suggested_action": decision
        }
    return sentiment_results

def main():
    print("📡 Fetching RSS feeds...")
    links = extract_links_from_rss()
    print(f"🔗 Found {len(links)} articles.")
    
    full_texts = []
    i=0
    for link in links:
        i+=1
        print(f"Scraping link {i}: {link}")
        article_text = scrape_article(link)
        if article_text:
            full_texts.append(article_text)
    
    print("📊 Performing sentiment analysis...")
    sentiment_scores = analyze_sentiment("\n\n".join(full_texts))
    
    for stock, data in sentiment_scores.items():
        print(f"\n📊 Sentiment Analysis for {stock} ({ENERGY_STOCKS[stock]}):")
        print(f"   - Mentions: {data['mentions']}")
        print(f"   - Sentiment Score: {data['sentiment_score']:.2f}")
        print(f"   - Market Indicator: {data['indicator']}")
        print(f"   - Suggested Action: {data['suggested_action']}")

if __name__ == "__main__":
    main()

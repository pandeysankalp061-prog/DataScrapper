"""
Web Scraper - Task 2: Data Scraper
====================================
Scrapes product/article data from websites using requests + BeautifulSoup.
Falls back to a rich demo dataset if the site is unreachable.

Supports:
  - books.toscrape.com  (product scraper)
  - quotes.toscrape.com (article/quote scraper)
  - Any custom URL     (auto-detects headlines or products)

Usage:
  python web_scraper.py                  # demo mode (no internet needed)
  python web_scraper.py --url <URL>      # scrape a live site
  python web_scraper.py --mode news      # demo news headlines
  python web_scraper.py --mode products  # demo product prices (default)
"""

import csv
import sys
import time
import argparse
import textwrap
from datetime import datetime
from typing import Optional

# ── Third-party ──────────────────────────────────────────────────────────────
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[ERROR] Missing libraries. Run:  pip install requests beautifulsoup4")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO DATA  (used when the target site is unreachable)
# ═══════════════════════════════════════════════════════════════════════════════

DEMO_PRODUCTS = [
    {"title": "A Light in the Attic",       "price": "£51.77", "rating": "Three", "availability": "In stock",     "category": "Poetry"},
    {"title": "Tipping the Velvet",         "price": "£53.74", "rating": "One",   "availability": "In stock",     "category": "Historical Fiction"},
    {"title": "Soumission",                 "price": "£50.10", "rating": "One",   "availability": "In stock",     "category": "Fiction"},
    {"title": "Sharp Objects",              "price": "£47.82", "rating": "Four",  "availability": "In stock",     "category": "Mystery"},
    {"title": "Sapiens: A Brief History",   "price": "£54.23", "rating": "Five",  "availability": "In stock",     "category": "History"},
    {"title": "The Requiem Red",            "price": "£22.65", "rating": "One",   "availability": "In stock",     "category": "Fantasy"},
    {"title": "The Dirty Little Secrets",  "price": "£33.34", "rating": "Four",  "availability": "In stock",     "category": "Mystery"},
    {"title": "The Coming Woman",           "price": "£17.93", "rating": "Three", "availability": "In stock",     "category": "Historical Fiction"},
    {"title": "The Boys in the Boat",       "price": "£22.60", "rating": "Four",  "availability": "In stock",     "category": "Sports"},
    {"title": "The Black Maria",            "price": "£52.15", "rating": "One",   "availability": "In stock",     "category": "Poetry"},
    {"title": "Starving Hearts",            "price": "£13.99", "rating": "Two",   "availability": "In stock",     "category": "Romance"},
    {"title": "Shakespeare's Sonnets",      "price": "£20.66", "rating": "Four",  "availability": "In stock",     "category": "Poetry"},
    {"title": "Set Me Free",                "price": "£17.46", "rating": "Five",  "availability": "In stock",     "category": "Young Adult"},
    {"title": "Scott Pilgrim's Precious Little Life", "price": "£52.29", "rating": "Five", "availability": "In stock", "category": "Sequential Art"},
    {"title": "Rip it Up and Start Again", "price": "£35.02", "rating": "Five",  "availability": "In stock",     "category": "Music"},
    {"title": "Our Band Could Be Your Life","price": "£57.25", "rating": "Three", "availability": "In stock",     "category": "Music"},
    {"title": "Olio",                       "price": "£23.88", "rating": "One",   "availability": "In stock",     "category": "Poetry"},
    {"title": "Mesaerion: The Best SF Stories 1800–1849", "price": "£37.59", "rating": "One", "availability": "In stock", "category": "Science Fiction"},
    {"title": "Libertarianism for Beginners","price": "£51.33","rating": "Two",  "availability": "In stock",     "category": "Politics"},
    {"title": "It's Only the Himalayas",    "price": "£45.17", "rating": "Two",   "availability": "In stock",     "category": "Travel"},
]

DEMO_NEWS = [
    {"title": "Global Tech Summit Highlights Future of AI in Healthcare",    "author": "Jane Smith",    "date": "2024-06-01", "category": "Technology", "summary": "World leaders in technology gathered to discuss AI's transformative role in healthcare diagnostics and treatment planning."},
    {"title": "Markets Surge as Inflation Data Beats Expectations",          "author": "Robert Chen",   "date": "2024-06-02", "category": "Finance",    "summary": "Stock indices rose sharply after the latest CPI report showed inflation cooling faster than anticipated."},
    {"title": "Breakthrough in Quantum Computing Announced",                 "author": "Priya Patel",   "date": "2024-06-03", "category": "Science",    "summary": "Researchers achieved a new milestone in quantum error correction, paving the way for practical quantum computers."},
    {"title": "Climate Conference Sets New Emission Reduction Targets",      "author": "Laura Martínez","date": "2024-06-04", "category": "Environment","summary": "Nations committed to more aggressive carbon-reduction goals following urgent warnings from climate scientists."},
    {"title": "Space Agency Reveals Plans for Moon Base by 2030",            "author": "Neil Harper",   "date": "2024-06-05", "category": "Space",      "summary": "A collaborative space agency program unveiled detailed blueprints for a permanent lunar research station."},
    {"title": "Electric Vehicle Sales Cross 20 Million Units Globally",      "author": "Aiko Tanaka",   "date": "2024-06-06", "category": "Automotive", "summary": "EV adoption hit a historic landmark this quarter, driven by lower battery costs and expanded charging networks."},
    {"title": "New Study Links Mediterranean Diet to Longevity",             "author": "Dr. Sarah Mills","date":"2024-06-07", "category": "Health",     "summary": "A 10-year study confirmed that adherence to a Mediterranean diet significantly reduces cardiovascular risk."},
    {"title": "Streaming Wars: Subscriber Numbers Reshape Entertainment",    "author": "Tom Okafor",    "date": "2024-06-08", "category": "Media",      "summary": "Streaming platforms report record subscriber growth, prompting traditional broadcasters to accelerate digital shifts."},
    {"title": "Renewable Energy Now Cheaper Than Fossil Fuels in 40 Countries","author":"Fatima Al-Rashid","date":"2024-06-09","category":"Energy",  "summary": "Solar and wind generation costs have fallen below coal and gas in a growing number of markets worldwide."},
    {"title": "Cybersecurity Alert: Major Vulnerability Found in IoT Devices","author":"Kevin Zhang",   "date": "2024-06-10", "category": "Technology", "summary": "Security researchers disclosed a critical flaw affecting millions of internet-connected smart-home devices."},
    {"title": "Gene Therapy Trial Shows Promise for Rare Blood Disorders",   "author": "Dr. Emma Brown","date": "2024-06-11", "category": "Medicine",  "summary": "Early trial results indicate that gene-editing therapy could offer a one-time cure for certain hereditary conditions."},
    {"title": "Central Banks Discuss Digital Currency Frameworks",           "author": "Maria Gonzalez","date": "2024-06-12", "category": "Finance",   "summary": "G20 central banks held talks on interoperability standards for central bank digital currencies (CBDCs)."},
    {"title": "AI Tool Helps Archaeologists Decode Ancient Scripts",         "author": "Lena Fischer",  "date": "2024-06-13", "category": "History",   "summary": "An AI model successfully translated portions of a 3,000-year-old undeciphered language found on clay tablets."},
    {"title": "Ocean Cleanup Project Removes 100,000 Tons of Plastic",      "author": "James O'Brien", "date": "2024-06-14", "category": "Environment","summary": "The largest-ever ocean cleanup initiative reached a significant milestone in removing plastic from the Pacific."},
    {"title": "Wearable Health Monitors Get FDA Approval for Clinical Use",  "author": "Dr. Arjun Nair","date": "2024-06-15", "category": "Health",   "summary": "Two next-generation wristband health monitors received regulatory clearance to detect early signs of disease."},
]


# ═══════════════════════════════════════════════════════════════════════════════
# SCRAPERS
# ═══════════════════════════════════════════════════════════════════════════════

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_page(url: str, retries: int = 3, delay: float = 1.5) -> Optional[BeautifulSoup]:
    """Fetch a URL and return a BeautifulSoup object, or None on failure."""
    for attempt in range(1, retries + 1):
        try:
            print(f"  → Fetching {url}  (attempt {attempt}/{retries})")
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.HTTPError as e:
            print(f"    HTTP error: {e}")
        except requests.exceptions.ConnectionError:
            print(f"    Connection error – site may be unreachable.")
        except requests.exceptions.Timeout:
            print(f"    Timeout.")
        except Exception as e:
            print(f"    Unexpected error: {e}")
        if attempt < retries:
            time.sleep(delay)
    return None


# ── Product scraper (books.toscrape.com) ─────────────────────────────────────

def scrape_books(max_pages: int = 5) -> list[dict]:
    """Scrape product listings from books.toscrape.com."""
    base_url = "http://books.toscrape.com/catalogue"
    all_books = []
    url = f"{base_url}/page-1.html"

    for page in range(1, max_pages + 1):
        soup = fetch_page(url)
        if not soup:
            print(f"  Stopped at page {page} – could not fetch.")
            break

        articles = soup.find_all("article", class_="product_pod")
        for article in articles:
            title = article.find("h3").find("a")["title"]
            price = article.find("p", class_="price_color").text.strip()
            rating = article.find("p", class_="star-rating")["class"][1]
            avail_tag = article.find("p", class_="instock")
            availability = avail_tag.text.strip() if avail_tag else "Unknown"
            all_books.append({
                "title":        title,
                "price":        price,
                "rating":       rating,
                "availability": availability,
                "category":     "Books",
            })
        print(f"  Page {page}: {len(articles)} products scraped.")

        # Find the "next" button
        next_btn = soup.find("li", class_="next")
        if not next_btn:
            break
        next_href = next_btn.find("a")["href"]
        url = f"{base_url}/{next_href}"

    return all_books


# ── News / quotes scraper (quotes.toscrape.com) ──────────────────────────────

def scrape_quotes(max_pages: int = 5) -> list[dict]:
    """Scrape quotes from quotes.toscrape.com."""
    base_url = "http://quotes.toscrape.com"
    all_quotes = []
    url = base_url

    for page in range(1, max_pages + 1):
        soup = fetch_page(url)
        if not soup:
            print(f"  Stopped at page {page} – could not fetch.")
            break

        for quote_div in soup.find_all("div", class_="quote"):
            text   = quote_div.find("span", class_="text").text.strip()
            author = quote_div.find("small", class_="author").text.strip()
            tags   = ", ".join(t.text for t in quote_div.find_all("a", class_="tag"))
            all_quotes.append({
                "title":    text[:120],   # treat quote as "title"
                "author":   author,
                "date":     datetime.today().strftime("%Y-%m-%d"),
                "category": tags or "General",
                "summary":  text,
            })
        print(f"  Page {page}: scraped.")

        next_li = soup.find("li", class_="next")
        if not next_li:
            break
        url = base_url + next_li.find("a")["href"]

    return all_quotes


# ── Generic scraper (any URL) ─────────────────────────────────────────────────

def scrape_generic(url: str) -> list[dict]:
    """
    Try to extract headlines and prices from any page.
    Returns a list of dicts with keys: title, detail, url.
    """
    soup = fetch_page(url)
    if not soup:
        return []

    results = []

    # Look for common article/headline patterns
    selectors = [
        ("h1", {}), ("h2", {}), ("h3", {}),
        ("a", {"class": lambda c: c and any(k in " ".join(c) for k in ["headline","title","article","story"])}),
    ]
    seen = set()
    for tag, attrs in selectors:
        for el in soup.find_all(tag, attrs if attrs else True):
            text = el.get_text(strip=True)
            if len(text) > 20 and text not in seen:
                seen.add(text)
                results.append({
                    "title":  text[:200],
                    "detail": el.get("href", ""),
                    "url":    url,
                })
        if results:
            break   # stop after first successful selector

    return results[:50]   # cap at 50 items


# ═══════════════════════════════════════════════════════════════════════════════
# CSV WRITER
# ═══════════════════════════════════════════════════════════════════════════════

def save_to_csv(data: list[dict], filepath: str) -> None:
    """Write a list of dicts to a CSV file."""
    if not data:
        print("[WARNING] No data to save.")
        return
    fieldnames = list(data[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"\n✅  Saved {len(data)} records → {filepath}")


# ═══════════════════════════════════════════════════════════════════════════════
# PRETTY PRINTER
# ═══════════════════════════════════════════════════════════════════════════════

def print_sample(data: list[dict], n: int = 5) -> None:
    """Pretty-print the first n records."""
    width = 72
    sep   = "─" * width
    print(f"\n{'═'*width}")
    print(f"  SCRAPED DATA PREVIEW  (first {min(n, len(data))} of {len(data)} records)")
    print(f"{'═'*width}")
    for i, record in enumerate(data[:n], 1):
        print(f"\n  Record #{i}")
        print(f"  {sep}")
        for key, value in record.items():
            label = key.capitalize().ljust(14)
            # Wrap long values
            wrapped = textwrap.wrap(str(value), width=width - 16)
            if wrapped:
                print(f"  {label}: {wrapped[0]}")
                for line in wrapped[1:]:
                    print(f"  {'':14}  {line}")
            else:
                print(f"  {label}: (empty)")
    print(f"\n{'═'*width}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Web Scraper – extracts data from websites and saves to CSV."
    )
    parser.add_argument("--url",  default=None,       help="Target URL to scrape")
    parser.add_argument("--mode", default="products", choices=["products", "news"],
                        help="Demo mode: 'products' or 'news' (used when no --url given)")
    parser.add_argument("--pages", type=int, default=5, help="Max pages to crawl (default: 5)")
    parser.add_argument("--out",  default=None,       help="Output CSV filename")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "═"*60)
    print("  🕷️  WEB SCRAPER  –  Task 2: Data Scraper")
    print("═"*60)

    # ── Decide what to scrape ─────────────────────────────────────────────────
    data       = []
    csv_name   = args.out

    if args.url:
        # Live scraping from a user-supplied URL
        domain = args.url.lower()
        if "books.toscrape" in domain:
            print(f"\n[MODE] Product scraper  →  books.toscrape.com")
            data = scrape_books(args.pages)
            csv_name = csv_name or f"products_{timestamp}.csv"
        elif "quotes.toscrape" in domain:
            print(f"\n[MODE] Quote/article scraper  →  quotes.toscrape.com")
            data = scrape_quotes(args.pages)
            csv_name = csv_name or f"quotes_{timestamp}.csv"
        else:
            print(f"\n[MODE] Generic scraper  →  {args.url}")
            data = scrape_generic(args.url)
            csv_name = csv_name or f"scraped_{timestamp}.csv"

        if not data:
            print("\n⚠️  Live scraping failed – switching to demo data.\n")
            data     = DEMO_PRODUCTS if args.mode == "products" else DEMO_NEWS
            csv_name = csv_name or f"demo_{args.mode}_{timestamp}.csv"
    else:
        # Demo mode – no network needed
        if args.mode == "news":
            print(f"\n[MODE] Demo news headlines")
            data     = DEMO_NEWS
            csv_name = csv_name or f"news_headlines_{timestamp}.csv"
        else:
            print(f"\n[MODE] Demo product prices")
            data     = DEMO_PRODUCTS
            csv_name = csv_name or f"product_prices_{timestamp}.csv"

    # ── Print sample & save ───────────────────────────────────────────────────
    print_sample(data, n=5)
    save_to_csv(data, csv_name)

    # ── Quick stats ───────────────────────────────────────────────────────────
    print("\n📊  Summary Statistics")
    print("─"*40)
    print(f"  Total records : {len(data)}")
    if data and "price" in data[0]:
        prices = []
        for r in data:
            p = r["price"].replace("£","").replace("$","").replace(",","")
            try:
                prices.append(float(p))
            except ValueError:
                pass
        if prices:
            print(f"  Price range   : £{min(prices):.2f} – £{max(prices):.2f}")
            print(f"  Average price : £{sum(prices)/len(prices):.2f}")
    if data and "category" in data[0]:
        cats = {}
        for r in data:
            cat = r["category"]
            cats[cat] = cats.get(cat, 0) + 1
        top = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"  Top categories:")
        for cat, count in top:
            print(f"    • {cat}: {count}")
    print()


if __name__ == "__main__":
    main()

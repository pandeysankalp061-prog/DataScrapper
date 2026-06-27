# 🕷️ DataScrapper

A Python web scraping tool that extracts product listings and news headlines from websites and saves them to CSV files. Built with `requests` and `BeautifulSoup4`, it gracefully falls back to rich demo datasets when a target site is unreachable — so it works even without internet access.

---

## 📁 Project Structure

```
DataScrapper/
├── web_scraper.py        # Main scraper script
├── product_prices.csv    # Sample output: book product data
└── news_headlines.csv    # Sample output: news headline data
```

---

## ✨ Features

- **Product Scraper** — Scrapes book titles, prices, ratings, availability, and categories from `books.toscrape.com`
- **News/Quote Scraper** — Scrapes quotes and metadata from `quotes.toscrape.com`
- **Generic Scraper** — Auto-detects and extracts headlines or links from any custom URL
- **Demo Mode** — Ships with 20 product records and 15 news records; no internet required
- **CSV Export** — Saves all scraped data to a timestamped CSV file
- **Summary Statistics** — Prints total records, price range, average price, and top categories
- **Retry Logic** — Retries failed HTTP requests up to 3 times with delay
- **Pretty Preview** — Displays a formatted table of the first 5 scraped records in the terminal

---

## 🛠️ Requirements

- Python 3.10+
- `requests`
- `beautifulsoup4`

Install dependencies:

```bash
pip install requests beautifulsoup4
```

---

## 🚀 Usage

### Demo Mode (no internet needed)

```bash
# Demo product prices (default)
python web_scraper.py

# Demo news headlines
python web_scraper.py --mode news
```

### Live Scraping

```bash
# Scrape books from books.toscrape.com
python web_scraper.py --url http://books.toscrape.com

# Scrape quotes from quotes.toscrape.com
python web_scraper.py --url http://quotes.toscrape.com

# Scrape any website (generic extractor)
python web_scraper.py --url https://example.com
```

### Options

| Argument  | Description                                      | Default      |
|-----------|--------------------------------------------------|--------------|
| `--url`   | Target URL to scrape                             | None (demo)  |
| `--mode`  | Demo mode: `products` or `news`                  | `products`   |
| `--pages` | Maximum number of pages to crawl                 | `5`          |
| `--out`   | Custom output CSV filename                       | Auto-named   |

---

## 📄 Output Format

### Product CSV (`product_prices.csv`)

| Column         | Description                          |
|----------------|--------------------------------------|
| `title`        | Book/product title                   |
| `price`        | Price (e.g., `£51.77`)               |
| `rating`       | Star rating as word (e.g., `Four`)   |
| `availability` | Stock status (e.g., `In stock`)      |
| `category`     | Genre or product category            |

### News CSV (`news_headlines.csv`)

| Column     | Description                            |
|------------|----------------------------------------|
| `title`    | Headline or quote text (max 120 chars) |
| `author`   | Author name                            |
| `date`     | Publication date (`YYYY-MM-DD`)        |
| `category` | Topic/tag (e.g., `Technology`)         |
| `summary`  | Full quote or article summary          |

---

## 📊 Example Terminal Output

```
════════════════════════════════════════════════════════════
  🕷️  WEB SCRAPER  –  Task 2: Data Scraper
════════════════════════════════════════════════════════════

[MODE] Demo product prices

════════════════════════════════════════════════════════════
  SCRAPED DATA PREVIEW  (first 5 of 20 records)
════════════════════════════════════════════════════════════

  Record #1
  ────────────────────────────────────────────────────────
  Title         : A Light in the Attic
  Price         : £51.77
  Rating        : Three
  Availability  : In stock
  Category      : Poetry

✅  Saved 20 records → product_prices_20240624_120000.csv

📊  Summary Statistics
────────────────────────────────────────────────
  Total records : 20
  Price range   : £13.99 – £57.25
  Average price : £37.81
  Top categories:
    • Poetry: 4
    • Music: 2
    • Mystery: 2
    ...
```

---

## ⚙️ How It Works

1. **Argument Parsing** — CLI arguments are parsed to determine mode, URL, page limit, and output file.
2. **Fetching** — `fetch_page()` sends HTTP GET requests with a browser-like User-Agent and retries on failure.
3. **Parsing** — BeautifulSoup parses the HTML; scraper functions target site-specific CSS classes.
4. **Fallback** — If live scraping fails, the script automatically switches to built-in demo data.
5. **Export** — `save_to_csv()` writes the results using Python's `csv.DictWriter`.
6. **Stats** — A summary of totals, price range, and category distribution is printed to the console.

---

## 🌐 Supported Sites

| Site                      | Scraper Type     | Data Extracted                          |
|---------------------------|------------------|-----------------------------------------|
| `books.toscrape.com`      | Product scraper  | Title, price, rating, availability      |
| `quotes.toscrape.com`     | Quote scraper    | Quote text, author, tags                |
| Any other URL             | Generic scraper  | Page headings and linked text (up to 50)|

---

## 📝 Notes

- Output CSV filenames are auto-timestamped (e.g., `product_prices_20240624_120000.csv`) unless `--out` is specified.
- The generic scraper caps results at **50 items** to avoid overwhelming output.
- The script respects a **1.5-second delay** between retry attempts to avoid overwhelming servers.
- All CSV files are saved in **UTF-8** encoding.

---

## 📜 License

This project is intended for educational purposes. Always check a website's `robots.txt` and Terms of Service before scraping.

import cloudscraper
from bs4 import BeautifulSoup
import csv
import time
import random

with open("articles.txt", "r") as f:
    urls = [line.strip() for line in f if line.strip()]

scraper = cloudscraper.create_scraper()
all_articles = []

for url in urls:
    print(f"\nScraping: {url}")
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        issue_articles = []

        for item in soup.select("div.issue-item"):
            title_elem = item.select_one("a.issue-item__title h2")
            pages_elem = item.select_one("li.page-range span:nth-of-type(2)")
            date_elem = item.select_one("li.ePubDate span:nth-of-type(2)")
            # pdf_elem = item.select_one("li.PdfLink a")
            doi_anchor = item.select_one("a.issue-item__title")

            authors = [
                a.get_text(strip=True)
                for a in item.select("div.loa.comma.loa-authors-trunc span.comma__item")
            ]
            authors = ", ".join(authors) if authors else None

            title = title_elem.text.strip() if title_elem else None
            pages = f"p. {pages_elem.text.strip()}" if pages_elem else None
            date = f"{date_elem.text.strip()}" if date_elem else None
            # pdf_url = pdf_elem["href"] if pdf_elem else None

            article_url = (
                f"https://onlinelibrary.wiley.com{doi_anchor['href']}"
                if doi_anchor and doi_anchor.has_attr("href")
                else None
            )

            issue_articles.append(
                {
                    "title": title,
                    "authors": authors,
                    "pages": pages,
                    "date": date,
                    # "pdf_url": pdf_url,
                    "article_url": article_url,
                    "issue_url": url,
                }
            )

        print(f"Found {len(issue_articles)} articles.")
        all_articles.extend(issue_articles)

        delay = random.uniform(10, 15)
        print(f"Sleeping {delay:.1f} seconds...\n")
        time.sleep(delay)

    except Exception as e:
        print(f"Error scraping {url}: {e}")

if all_articles:
    with open("articles.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=all_articles[0].keys(),
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(all_articles)
    print(f"\nSaved {len(all_articles)} total articles to articles.csv.")
else:
    print("\nNo articles found.")

# OLX Car Cover Scraper

## Description
This is a Python-based web scraper built using **Playwright**. It scrapes car cover listings from OLX India and extracts:

- **Price** of the item
- **Location** of the seller
- **Item link**

The scraper handles dynamic loading by scrolling and clicking the "Load More" button until all available ads are loaded.

---

## Requirements
- Python 3.8+
- Playwright
- CSV module (standard library)
- Regular expressions (standard library)

### Install Playwright
```bash
pip install playwright
playwright install
```

---

## How to Run
1. Clone or download this repository.  
2. Navigate to the project folder:  
```bash
cd /path/to/project
```
3. Run the scraper:  
```bash
python code.py
```
4. The scraper will navigate to OLX, load all available ads, extract the required fields, and save them into a CSV file.

---

## Output
The scraper generates a CSV file named **`olx_results.csv`** with the following columns:

| Price | Location | Link |
|-------|---------|------|
| Rs. 4500 | Buldana | https://www.olx.in/item/... |
| Rs. 11250 | Kolkata | https://www.olx.in/item/... |

- The CSV contains all ads loaded from the OLX Car Cover page.  
- The **Title column is removed** to focus only on Price, Location, and Link.

---

## Notes
- Make sure to include `https://` in the URL when changing the page.  
- The scraper handles dynamic content and clicking "Load More" automatically.  
- You can adjust `max_wait` in the code for longer or shorter waiting times while loading ads.

---

## License
This project is open source and free to use.


from playwright.sync_api import sync_playwright
import csv
import re
import time

# Function to check if a text is likely a location
def is_probable_location(text):
    if not text:
        return False
    text = text.strip()
    if len(text) > 60 or len(text) < 2:
        return False
    upper_text = text.upper()
    non_location_keywords = [
        "FEATURED", "CAR", "COVER", "KM", "DAYS", "HOURS", "MINUTES", "AGO",
        "USED", "ORIGINAL", "SELLER", "OWNER", "XUV", "SEDAN", "SUV", "PETROL", "DIESEL"
    ]
    if any(k in upper_text for k in non_location_keywords):
        return False
    if re.search(r"\d|₹|RS", text):
        return False
    return True

def scrape_olx(browser_name="chromium"):
    with sync_playwright() as p:
        if browser_name == "chromium":
            browser = p.chromium.launch(headless=False, slow_mo=50)
        elif browser_name == "firefox":
            browser = p.firefox.launch(headless=False, slow_mo=50)
        elif browser_name == "webkit":
            browser = p.webkit.launch(headless=False, slow_mo=50)
        else:
            raise ValueError("Invalid browser! Choose chromium, firefox, or webkit")

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                       "Version/17.0 Safari/605.1.15"
        )
        page = context.new_page()
        page.goto("https://www.olx.in/items/q-car-cover", timeout=60000)

        print("[INFO] Loading all ads by scrolling and clicking 'Load More'...")

        previous_count = 0
        timeout_start = time.time()
        max_wait = 120  # stop if no new ads for 120 seconds

        while True:
            # Scroll a bit
            page.evaluate("window.scrollBy(0, 2000)")
            page.wait_for_timeout(2000)

            # Click "Load More" if visible
            load_more_btn = page.locator("text=Load more")
            if load_more_btn.count() > 0 and load_more_btn.is_visible():
                try:
                    load_more_btn.first.click()
                    print("[INFO] Clicked 'Load More'")
                    page.wait_for_timeout(3000)
                except:
                    pass

            # Count ads
            ads = page.locator("li[data-aut-id='itemBox']")
            current_count = ads.count()
            print(f"[INFO] Ads loaded: {current_count}")

            if current_count > previous_count:
                previous_count = current_count
                timeout_start = time.time()  # reset timer
            else:
                # if no new ads for max_wait seconds, stop
                if time.time() - timeout_start > max_wait:
                    print("[INFO] No more new ads detected. Finished loading.")
                    break

        print(f"[INFO] Total ads loaded: {previous_count}")

        print("[INFO] Extracting ads...")

        locators = [
            "li[data-aut-id='itemBox']",  
            "div[data-aut-id='itemBox']", 
            "a[href*='/item/']"           
        ]

        ads = None
        for locator in locators:
            items = page.locator(locator)
            count = items.count()
            if count > 0:
                ads = items
                print(f"[DEBUG] Found {count} ads using selector: {locator}")
                break

        if not ads:
            print("[WARN] No ads found.")
            html = page.content()
            print("[DEBUG] Page HTML snippet:")
            print(html[:2000])
            browser.close()
            return

        results = []
        for i in range(ads.count()):
            try:
                item = ads.nth(i)

                # Price
                price = "N/A"
                if item.locator("span:has-text('₹')").count() > 0:
                    price = item.locator("span:has-text('₹')").first.inner_text(timeout=2000).replace("₹", "Rs.")

                # Location
                location = "N/A"
                spans = item.locator("span")
                for j in range(spans.count()):
                    txt = spans.nth(j).inner_text(timeout=2000).strip()
                    if is_probable_location(txt):
                        location = txt
                        break

                # Link
                link = item.get_attribute("href") or item.locator("a").get_attribute("href") or "N/A"
                if link and not link.startswith("http"):
                    link = "https://www.olx.in" + link

                results.append([price.strip(), location.strip(), link])
                print(f"[FOUND] {price} | {location} | {link}")

            except Exception as e:
                print(f"[ERROR] Failed extracting item {i}: {e}")

        if results:
            with open("olx_results.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Price", "Location", "Link"])
                writer.writerows(results)
            print(f"[SUCCESS] Saved {len(results)} ads to olx_results.csv")
        else:
            print("[WARN] No ads extracted.")

        browser.close()


if __name__ == "__main__":
    for browser in ["chromium"]:
        scrape_olx(browser)

import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

# Configuration
RETAILERS = {
    'Incredible Connection': 'https://www.incredible.co.za/products/tv-audio/tv/4k',
    'Hirschs': 'https://www.hirschs.co.za/tv-and-entertainment/tv-s?TV_Size=325',
    'Makro': 'https://www.makro.co.za/ckf/czl/~cs-7gmdq5lcp2/pr?sid=ckf%2Cczl&collection-tab-name=Televisions+-+60+Inch+Over&ctx=eyJjYXJkQ29udGV4dCI6eyJhdHRyaWJ1dGVzIjp7InRpdGxlIjp7Im11bHRpVmFsdWVkQXR0cmlidXRlIjp7ImtleSI6InRpdGxlIiwiaW5mZXJlbmNlVHlwZSI6IlRJVExFIiwidmFsdWVzIjpbIjYwXCIrIFRWcyJdLCJ2YWx1ZVR5cGUiOiJNVUxUSV9WQUxVRUQifX19fX0%3D&wid=3.productCard.PMU_V2_3&fm=neo%2Fmerchandising&iid=M_0bf934a8-a3bd-4448-b805-f90c34ff3040_2_MK8PR3WWPP7K_MC.506F383DL0N9&otracker=hp_rich_navigation_4_2.navigationCard.RICH_NAVIGATION_Electronics%7ETelevisions%7E60%2522%2Band%2Bbigger_506F383DL0N9&otracker1=hp_rich_navigation_PINNED_neo%2Fmerchandising_NA_NAV_EXPANDABLE_navigationCard_cc_4_L2_view-all&cid=506F383DL0N9&p%5B%5D=facets.screen_size%255B%255D%3D60%2Binch%2B%2BAbove',
    'Loot': 'https://www.loot.co.za/search?vprice_min=&vprice_max=&facet%40TechHtDisplaySize%2F55%22=on&facet%40TechHtDisplaySize%2F65%22=on&facet%40TechHtDisplaySize%2F50%22=on&facet%40TechHtDisplaySize%2F58%22=on&facet%40TechHtDisplaySize%2F60%22=on&cat=nni',
    'Takealot': 'https://www.takealot.com/tv-audio-video/tvs-25953?filter=TVScreenSize:1549.4-1981.2&sort=Relevance',
    'Game': 'https://www.game.co.za/Electronics-Entertainment/Television/TVs/l/c/G3428'
}

BRANDS = ['Samsung', 'LG']
CSV_FILE = 'tv_prices.csv'
PRICE_HISTORY_FILE = 'price_history.json'

def is_samsung_or_lg(title):
    """Check if product title contains Samsung or LG"""
    title_lower = title.lower()
    return any(brand.lower() in title_lower for brand in BRANDS)

def is_65_inch(title):
    """Check if product is 65 inch"""
    return '65"' in title or '65 inch' in title.lower() or '65in' in title.lower()

def is_4k(title):
    """Check if product is 4K"""
    title_lower = title.lower()
    return '4k' in title_lower or 'ultra hd' in title_lower or 'uhd' in title_lower

def scrape_incredible_connection():
    """Scrape Incredible Connection"""
    products = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(RETAILERS['Incredible Connection'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find product containers
        product_items = soup.find_all('div', class_='product-card')
        
        for item in product_items:
            try:
                title_elem = item.find('h2', class_='product-title')
                price_elem = item.find('span', class_='price')
                
                if title_elem and price_elem:
                    title = title_elem.get_text(strip=True)
                    price_text = price_elem.get_text(strip=True)
                    
                    if is_samsung_or_lg(title) and is_65_inch(title) and is_4k(title):
                        # Extract price (remove R and commas)
                        price = float(price_text.replace('R', '').replace(',', '').strip())
                        products.append({
                            'retailer': 'Incredible Connection',
                            'title': title,
                            'price': price,
                            'url': item.find('a')['href'] if item.find('a') else '',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
            except Exception as e:
                print(f"Error parsing product from Incredible Connection: {e}")
                continue
    except Exception as e:
        print(f"Error scraping Incredible Connection: {e}")
    
    return products

def scrape_hirschs():
    """Scrape Hirschs"""
    products = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(RETAILERS['Hirschs'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_items = soup.find_all('div', class_='product-item')
        
        for item in product_items:
            try:
                title_elem = item.find('h3', class_='product-name')
                price_elem = item.find('span', class_='price')
                
                if title_elem and price_elem:
                    title = title_elem.get_text(strip=True)
                    price_text = price_elem.get_text(strip=True)
                    
                    if is_samsung_or_lg(title) and is_65_inch(title) and is_4k(title):
                        price = float(price_text.replace('R', '').replace(',', '').strip())
                        products.append({
                            'retailer': 'Hirschs',
                            'title': title,
                            'price': price,
                            'url': item.find('a')['href'] if item.find('a') else '',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
            except Exception as e:
                print(f"Error parsing product from Hirschs: {e}")
                continue
    except Exception as e:
        print(f"Error scraping Hirschs: {e}")
    
    return products

def scrape_takealot():
    """Scrape Takealot"""
    products = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(RETAILERS['Takealot'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_items = soup.find_all('article', class_='productTile')
        
        for item in product_items:
            try:
                title_elem = item.find('h2', class_='productTile_title')
                price_elem = item.find('span', class_='productTile_price')
                
                if title_elem and price_elem:
                    title = title_elem.get_text(strip=True)
                    price_text = price_elem.get_text(strip=True)
                    
                    if is_samsung_or_lg(title) and is_65_inch(title) and is_4k(title):
                        price = float(price_text.replace('R', '').replace(',', '').strip())
                        products.append({
                            'retailer': 'Takealot',
                            'title': title,
                            'price': price,
                            'url': item.find('a')['href'] if item.find('a') else '',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
            except Exception as e:
                print(f"Error parsing product from Takealot: {e}")
                continue
    except Exception as e:
        print(f"Error scraping Takealot: {e}")
    
    return products

def scrape_game():
    """Scrape Game"""
    products = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(RETAILERS['Game'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_items = soup.find_all('div', class_='productListItem')
        
        for item in product_items:
            try:
                title_elem = item.find('a', class_='productName')
                price_elem = item.find('span', class_='sellingPrice')
                
                if title_elem and price_elem:
                    title = title_elem.get_text(strip=True)
                    price_text = price_elem.get_text(strip=True)
                    
                    if is_samsung_or_lg(title) and is_65_inch(title) and is_4k(title):
                        price = float(price_text.replace('R', '').replace(',', '').strip())
                        products.append({
                            'retailer': 'Game',
                            'title': title,
                            'price': price,
                            'url': item.find('a')['href'] if item.find('a') else '',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
            except Exception as e:
                print(f"Error parsing product from Game: {e}")
                continue
    except Exception as e:
        print(f"Error scraping Game: {e}")
    
    return products

def scrape_makro():
    """Scrape Makro"""
    products = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(RETAILERS['Makro'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_items = soup.find_all('div', class_='productContainer')
        
        for item in product_items:
            try:
                title_elem = item.find('a', class_='productTitle')
                price_elem = item.find('span', class_='productPrice')
                
                if title_elem and price_elem:
                    title = title_elem.get_text(strip=True)
                    price_text = price_elem.get_text(strip=True)
                    
                    if is_samsung_or_lg(title) and is_65_inch(title) and is_4k(title):
                        price = float(price_text.replace('R', '').replace(',', '').strip())
                        products.append({
                            'retailer': 'Makro',
                            'title': title,
                            'price': price,
                            'url': item.find('a')['href'] if item.find('a') else '',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
            except Exception as e:
                print(f"Error parsing product from Makro: {e}")
                continue
    except Exception as e:
        print(f"Error scraping Makro: {e}")
    
    return products

def scrape_loot():
    """Scrape Loot"""
    products = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(RETAILERS['Loot'], headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_items = soup.find_all('div', class_='productCard')
        
        for item in product_items:
            try:
                title_elem = item.find('h3', class_='productName')
                price_elem = item.find('span', class_='productPrice')
                
                if title_elem and price_elem:
                    title = title_elem.get_text(strip=True)
                    price_text = price_elem.get_text(strip=True)
                    
                    if is_samsung_or_lg(title) and is_65_inch(title) and is_4k(title):
                        price = float(price_text.replace('R', '').replace(',', '').strip())
                        products.append({
                            'retailer': 'Loot',
                            'title': title,
                            'price': price,
                            'url': item.find('a')['href'] if item.find('a') else '',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
            except Exception as e:
                print(f"Error parsing product from Loot: {e}")
                continue
    except Exception as e:
        print(f"Error scraping Loot: {e}")
    
    return products

def load_price_history():
    """Load price history from JSON file"""
    if os.path.exists(PRICE_HISTORY_FILE):
        try:
            with open(PRICE_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_price_history(history):
    """Save price history to JSON file"""
    with open(PRICE_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def detect_changes(current_products, price_history):
    """Detect price changes and cross-retailer differences"""
    changes = {
        'price_drops': [],
        'cross_retailer_deals': [],
        'new_products': []
    }
    
    # Create a key for each product (normalized title)
    for product in current_products:
        key = f"{product['title'].lower()}_{product['retailer']}"
        
        if key in price_history:
            old_price = price_history[key]['price']
            if product['price'] < old_price:
                changes['price_drops'].append({
                    'product': product['title'],
                    'retailer': product['retailer'],
                    'old_price': old_price,
                    'new_price': product['price'],
                    'savings': old_price - product['price']
                })
        else:
            changes['new_products'].append({
                'product': product['title'],
                'retailer': product['retailer'],
                'price': product['price']
            })
    
    # Check for same model at cheaper prices across retailers
    product_titles = {}
    for product in current_products:
        # Normalize title by removing retailer-specific SKUs
        normalized = product['title'].lower()
        if normalized not in product_titles:
            product_titles[normalized] = []
        product_titles[normalized].append(product)
    
    for normalized_title, products_list in product_titles.items():
        if len(products_list) > 1:
            sorted_products = sorted(products_list, key=lambda x: x['price'])
            cheapest = sorted_products[0]
            
            for product in sorted_products[1:]:
                if product['price'] > cheapest['price']:
                    changes['cross_retailer_deals'].append({
                        'product': product['title'],
                        'cheaper_at': cheapest['retailer'],
                        'cheaper_price': cheapest['price'],
                        'current_retailer': product['retailer'],
                        'current_price': product['price'],
                        'potential_savings': product['price'] - cheapest['price']
                    })
    
    return changes

def generate_email_body(changes):
    """Generate HTML email body"""
    html = """
    <html>
    <body style="font-family: Arial, sans-serif;">
    <h2>Daily TV Price Report - Samsung & LG 65" 4K TVs</h2>
    <p>Date: {}</p>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    if changes['price_drops']:
        html += "<h3>🔴 Price Drops</h3><ul>"
        for drop in changes['price_drops']:
            html += f"""
            <li>
                <b>{drop['product']}</b> @ {drop['retailer']}<br>
                R{drop['old_price']:,.0f} → R{drop['new_price']:,.0f}<br>
                <span style="color: green;"><b>Save: R{drop['savings']:,.0f}</b></span>
            </li>
            """
        html += "</ul>"
    
    if changes['cross_retailer_deals']:
        html += "<h3>💰 Cheaper Elsewhere</h3><ul>"
        for deal in changes['cross_retailer_deals']:
            html += f"""
            <li>
                <b>{deal['product']}</b><br>
                Cheaper at {deal['cheaper_at']}: R{deal['cheaper_price']:,.0f}<br>
                Currently at {deal['current_retailer']}: R{deal['current_price']:,.0f}<br>
                <span style="color: green;"><b>Potential savings: R{deal['potential_savings']:,.0f}</b></span>
            </li>
            """
        html += "</ul>"
    
    if changes['new_products']:
        html += "<h3>🆕 New Products Found</h3><ul>"
        for new in changes['new_products']:
            html += f"""
            <li>
                <b>{new['product']}</b> @ {new['retailer']}<br>
                R{new['price']:,.0f}
            </li>
            """
        html += "</ul>"
    
    if not any([changes['price_drops'], changes['cross_retailer_deals'], changes['new_products']]):
        html += "<p>No price changes detected today.</p>"
    
    html += "</body></html>"
    return html

def send_email(changes, recipient_email, sender_email, app_password):
    """Send email with changes"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Daily TV Price Report - {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        text = "See HTML version for formatted report"
        html = generate_email_body(changes)
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def save_to_csv(products):
    """Save products to CSV"""
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'retailer', 'title', 'price', 'url'])
            writer.writeheader()
            for product in products:
                writer.writerow(product)
        print(f"Saved {len(products)} products to {CSV_FILE}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def main():
    """Main execution"""
    print("Starting TV price scraper...")
    
    # Get environment variables for email
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    sender_email = os.getenv('SENDER_EMAIL')
    app_password = os.getenv('APP_PASSWORD')
    
    all_products = []
    
    print("Scraping retailers...")
    print("- Incredible Connection...")
    all_products.extend(scrape_incredible_connection())
    time.sleep(2)
    
    print("- Hirschs...")
    all_products.extend(scrape_hirschs())
    time.sleep(2)
    
    print("- Takealot...")
    all_products.extend(scrape_takealot())
    time.sleep(2)
    
    print("- Game...")
    all_products.extend(scrape_game())
    time.sleep(2)
    
    print("- Makro...")
    all_products.extend(scrape_makro())
    time.sleep(2)
    
    print("- Loot...")
    all_products.extend(scrape_loot())
    
    print(f"Found {len(all_products)} matching products")
    
    # Load price history
    price_history = load_price_history()
    
    # Detect changes
    changes = detect_changes(all_products, price_history)
    
    # Update price history
    for product in all_products:
        key = f"{product['title'].lower()}_{product['retailer']}"
        price_history[key] = {
            'price': product['price'],
            'date': product['date'],
            'url': product['url']
        }
    
    save_price_history(price_history)
    
    # Save to CSV
    save_to_csv(all_products)
    
    # Send email if configured
    if recipient_email and sender_email and app_password:
        send_email(changes, recipient_email, sender_email, app_password)
    else:
        print("Email configuration not found. Skipping email send.")
        print("Set RECIPIENT_EMAIL, SENDER_EMAIL, and APP_PASSWORD environment variables")
    
    print("Scraper completed successfully")

if __name__ == '__main__':
    main()

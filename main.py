import requests
import os
import json
import argparse
from bs4 import BeautifulSoup
import re

def fetch_sitemap(sitemap_url: str, filename: str = 'product_sitemap.xml') -> bytes:
    """
    Fetches a sitemap XML from a URL if it doesn't exist locally.
    
    Args:
        sitemap_url: URL of the sitemap XML to fetch
        filename: Name of the file to save (default: product_sitemap.xml)
        
    Returns:
        Bytes content of the sitemap XML
    """
    if os.path.exists(filename):
        print(f"Using existing sitemap file: {filename}")
        with open(filename, 'rb') as f:
            return f.read()
    
    print(f"Fetching sitemap from: {sitemap_url}")
    resp = requests.get(sitemap_url, timeout=15)
    resp.raise_for_status()  # raise if request failed
    return resp.content

def save_sitemap(sitemap_content: bytes, filename: str = 'product_sitemap.xml') -> None:
    """
    Saves sitemap content to a local file if it doesn't exist.
    
    Args:
        sitemap_content: Bytes content of the sitemap XML
        filename: Name of the file to save (default: product_sitemap.xml)
    """
    with open(filename, 'wb') as f:
        f.write(sitemap_content)

def prettify_json_file(filename: str) -> None:
    """
    Reads a JSON file, formats it with indentation, and saves it with '-pretty' suffix.
    
    Args:
        filename: Path to the JSON file to prettify
    """
    try:
        # Read the JSON file
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Create new filename with -pretty suffix
        base_name = os.path.basename(filename)
        pretty_filename = os.path.join(os.path.dirname(filename), f"{os.path.splitext(base_name)[0]}-pretty.json")
        
        # Write the prettified JSON
        with open(pretty_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Prettified JSON saved to: {pretty_filename}")
            
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {filename}: {str(e)}")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

def fetch_product_json(product_url: str) -> None:
    """
    Fetches product JSON data and saves it to a file.
    
    Args:
        product_url: URL of the product page (without .json)
    """
    # Create products directory if it doesn't exist
    os.makedirs('products', exist_ok=True)
    
    # Get product name from URL (everything after last /)
    product_name = product_url.split('/')[-1]
    
    # Create JSON URL by appending .json
    json_url = f"{product_url}.json"
    
    # Fetch JSON data
    print(f"Fetching JSON for {json_url}")
    try:
        resp = requests.get(json_url, timeout=15)
        resp.raise_for_status()
        
        # Save to products directory with product name
        with open(f"products/{product_name}.json", 'w', encoding='utf-8') as f:
            f.write(resp.text)
            print(f"Saved {product_name}.json")
            
    except requests.RequestException as e:
        print(f"Error fetching {json_url}: {str(e)}")

def fetch_and_parse_sitemap(sitemap_url: str) -> list:
    """
    Fetches a sitemap XML, saves it locally, and extracts product URLs.
    
    Args:
        sitemap_url: URL of the sitemap XML to fetch
        
    Returns:
        List of product URLs found in the sitemap
    """
    # Fetch or use existing sitemap content
    content = fetch_sitemap(sitemap_url)
    
    # Save the sitemap locally if it doesn't exist
    save_sitemap(content)

    # Parse as XML
    soup = BeautifulSoup(content, "xml")

    # Find all <loc> tags, filter for product URLs only
    loc_tags = [tag for tag in soup.find_all(string=re.compile("https://futuresfins.com/products/.*"))]
    urls = [tag.text for tag in loc_tags]
    
    return urls

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch and process product data from Futures Fins')
    parser.add_argument('--fetch-products', action='store_true',
                       help='Fetch product JSON files from URLs (default: False)')
    args = parser.parse_args()

    # URL of the product sitemap
    sitemap_url = "https://futuresfins.com/sitemap_products_1.xml?from=4539112718475&to=7713593983115"
    
    urls = fetch_and_parse_sitemap(sitemap_url)
    print(f"Found {len(urls)} URLs")

    # Fetch all product JSON files if requested
    if args.fetch_products:
        print("\nFetching product JSON files...")
        for url in urls:
            fetch_product_json(url)
    
    # Prettify all JSON files in the products directory
    print("\nPrettifying JSON files...")
    products_dir = 'products/pretty/'
    if os.path.exists(products_dir):
        for filename in os.listdir(products_dir):
            if filename.endswith('.json') and not filename.endswith('-pretty.json'):
                full_path = os.path.join(products_dir, filename)
                prettify_json_file(full_path)
    
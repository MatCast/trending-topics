import feedparser
import requests

urls = [
    "https://hnrss.github.io/newest?q=AI",
    "https://hnrss.org/newest?q=AI"
]

for url in urls:
    print(f"\nTesting URL: {url}")
    try:
        # Step 1: Check raw content
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            content = response.text
            print(f"Content length: {len(content)}")
            print("First 200 chars:")
            print(content[:200])

            # Step 2: Test feedparser
            print("Parsing with feedparser...")
            feed = feedparser.parse(content)
            if feed.bozo:
                print(f"BOZO DETECTED: {feed.bozo_exception}")
            else:
                print(f"Successfully parsed {len(feed.entries)} entries.")
        else:
            print("Failed to fetch.")
    except Exception as e:
        print(f"Error: {e}")

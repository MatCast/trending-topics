import feedparser
import json

urls = {
    "Reddit": "https://www.reddit.com/r/LocalLLaMA/rising.rss",
    "HackerNews": "https://hnrss.org/newest?q=AI"
}

for name, url in urls.items():
    print(f"\n{'='*50}\nAnalyzing {name} ({url})\n{'='*50}")
    feed = feedparser.parse(url)
    if not feed.entries:
        print("No entries found.")
        continue

    # Just look at the first entry
    entry = feed.entries[0]

    # Print keys available
    print(f"Keys available in entry: {list(entry.keys())}")

    # Print some interesting fields
    for k in ['title', 'link', 'comments', 'author', 'tags']:
        if k in entry:
            print(f"- {k}: {entry[k]}")

    # Print the description/content raw to see if points/upvotes are hidden there
    if 'content' in entry:
        print("\nContent snippet:")
        print(repr(entry.content[0].value)[:500])
    elif 'description' in entry:
        print("\nDescription snippet:")
        print(repr(entry.description)[:500])

    print("\nFull entry structure (JSON):")
    # Helper to serialize feedparser dict
    def clean_dict(d):
        cleaned = {}
        for k, v in d.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                cleaned[k] = v
            elif isinstance(v, list):
                if v and isinstance(v[0], str):
                    cleaned[k] = v
            elif isinstance(v, dict):
                cleaned[k] = clean_dict(v)
        return cleaned

    print(json.dumps(clean_dict(entry), indent=2))

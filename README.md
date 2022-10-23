# danbooru-scrape
Simple python utility for tag-based scraping off of danbooru.donmai.us using their web api.

## Setup

1. Install python 3.8+
2. Run `pip install requests`

## Example usage

```
python scrape_danbooru.py \
  --tags "genshin_impact"
```

Pass username and api_key to log on to your account and surpass the default tag search and page limit restrictions:

```
python scrape_danbooru.py \
  --username Maurdekye \
  --api_key abc123 \
  --tags "genshin_impact raiden_shogun musou_isshin_(genshin_impact)" \
  --page_limit 5000
```

Run `python scrape_danbooru.py -h` to see all available arguments.

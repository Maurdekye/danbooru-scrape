# danbooru-scrape
Simple python utility for tag-based scraping off of danbooru.donmai.us using their web api.

Example usage:
```
python danbooru_scrape.py \
  --tags "genshin_impact"
```

Pass username and api_key to log on to your account and surpass the default tag search and page limit restrictions:

```
python danbooru_scrape.py \
  --username Maurdekye \
  --api_key abc123 \
  --tags "genshin_impact raiden_shogun musou_isshin_(genshin_impact)" \
  --page_limit 5000
```

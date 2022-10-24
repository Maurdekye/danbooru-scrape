from argparse import ArgumentParser
from pathlib import Path
import requests
import os

parser = ArgumentParser(description="Scrape content from danbooru based on tag search.")
parser.add_argument("--tags", type=str, required=True, help="Tags to search for when downloading content.")
parser.add_argument("--output", type=Path, default="output", help="Output directory. (default: output/")
parser.add_argument("--url", type=str, default="https://danbooru.donmai.us", help="Danbooru url to make api calls to. (default: https://danbooru.donmai.us)")
parser.add_argument("--page_limit", type=int, default=1000, help="Maximum number of pages to parse through when downloading. (default: 1000)")
parser.add_argument("--api_key", type=str, help="API key for Danbooru, optional unless you want to link a higher level account to surpass tag search and page limit restrictions. Username must also be provided.")
parser.add_argument("--username", type=str, help="Username to log on to Danbooru with, to be provided alongside ana api_key")
parser.add_argument("--max_file_size", action='store_true', help="Attempt to download the maximum available file size instead of the default size.")
parser.add_argument("--extensions", type=str, default=".png,.jpg", help="Extensions of file types to download, comma-separated. Pass * to download all file types. (default: .png,.jpg)")

def get_posts(tags, url, login_info=None, page_limit=1000):
    for i in range(1, page_limit+1):
        params = {
            "tags": tags,
            "page": i
        }
        if login_info:
            params.update(login_info)
        req = requests.get(f"{url}/posts.json", params=params)
        content = req.json()
        if content == []:
            return
        if "success" in content and not content["success"]:
            raise Exception("Danbooru API: " + content["message"]) 
        yield from content

def save_to_path(stream, path):
    with path.open('wb') as f:
        for bytes in stream.iter_content(chunk_size=128):
            f.write(bytes)

def main(args):
    os.makedirs(args.output, exist_ok=True)

    login_info = None
    if any([args.username, args.api_key]):
        if all([args.username, args.api_key]):
            login_info = {
                "login": args.username,
                "api_key": args.api_key
            }
        else:
            raise Exception("You must pass both a --username and an --api_key in order to log on")

    all_extensions = args.extensions == "*"
    extensions = [e.strip().lower() for e in args.extensions.split(",")]

    i = 0
    try:
        for post in get_posts(args.tags, args.url, login_info, args.page_limit):
            if "file_url" not in post or (not all_extensions and Path(post["file_url"]).suffix not in extensions):
                continue
            url_path = post["large_file_url"] if args.max_file_size and "large_file_url" in post else post["file_url"]
            img_file = args.output / Path(url_path).name
            if not img_file.exists():
                try:
                    print(f"Downloading {img_file}")
                    req = requests.get(url_path, stream=True)
                    save_to_path(req, img_file)
                    i += 1
                except Exception:
                    print(f"Error downloading file from {url_path}, skipping")
    except KeyboardInterrupt:
        pass
    print(f"Scraped {i} files")

if __name__ == "__main__":
    try:
        main(parser.parse_args())
    except Exception as e:
        print(e)

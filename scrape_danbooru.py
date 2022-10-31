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
parser.add_argument("--save_tags", action='store_true', help="Save the tags for each image in a text file with the same name.")
parser.add_argument("--tags_only", action='store_true', help="Only save tags for existing images. Do not download any images.")


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

def format_tags(tag_string):
    new_tag_string = tag_string    \
              .replace(" ", ", " ) \
              .replace("_", " "  ) \
              .replace("(", r"\(") \
              .replace(")", r"\)")
    return new_tag_string

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
    if args.tags_only and not args.save_tags:
        args.save_tags = True

    i = 0
    j = 0
    try:
        for post in get_posts(args.tags, args.url, login_info, args.page_limit):
            if "file_url" not in post or (not all_extensions and Path(post["file_url"]).suffix not in extensions):
                continue
            url_path = post["large_file_url"] if args.max_file_size and "large_file_url" in post else post["file_url"]
            img_file = args.output / Path(url_path).name
            if not img_file.exists() and not args.tags_only:
                try:
                    print(f"Downloading {img_file}")
                    req = requests.get(url_path, stream=True)
                    save_to_path(req, img_file)
                    i += 1
                except Exception:
                    print(f"Error downloading file from {url_path}, skipping")
            if not img_file.exists() or not args.save_tags or "tag_string" not in post:
                continue
            tag_file = args.output / Path(url_path).with_suffix(".txt").name
            if not tag_file.exists():
                try:
                    print(f"Saving tags {tag_file}")
                    tag_string = format_tags(post["tag_string"])
                    tag_file.write_text(tag_string, encoding='utf-8')
                    j += 1
                except Exception as e:
                    print(f"Error saving tag file {tag_file}, skipping")
    except KeyboardInterrupt:
        pass
    if not args.tags_only:
        print(f"Scraped {i} files")
    if args.save_tags:
        print(f"Saved {j} tag files")

if __name__ == "__main__":
    try:
        main(parser.parse_args())
    except Exception as e:
        print(e)

import requests
import os

PAGE_SIZE = 50
TOTAL = 20000
NEWS_RSS_ROOT = f"https://www.npr.org/rss/rss.php?id=1039&numResults={PAGE_SIZE}"
IMPORT_ROOT = "."

start_at = 0
while start_at < TOTAL:
    up_to = start_at + PAGE_SIZE
    output_file = f"{IMPORT_ROOT}/news-{start_at}-{up_to}.xml"
    if os.path.isfile(output_file):
        print("found " + output_file + ", skipping")
    else:
        response = requests.get(f"{NEWS_RSS_ROOT}&startNum={start_at}")
        file = open(output_file, "w")
        file.write(response.text)
        file.close()
        print("created " + output_file)
    start_at += PAGE_SIZE

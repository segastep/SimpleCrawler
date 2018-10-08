import argparse
import urllib
import urllib.request as req
import re
import urllib.parse as parse
from bs4 import BeautifulSoup


parser = argparse.ArgumentParser(description="Simple web crawler")
parser.add_argument("--url", action="store", default="", help="Url like https://wwww.sth.com")
parser.add_argument("--disable-verbose", action="store_true", default="", help="Print verbose output")

arguments = parser.parse_args()
url = arguments.url.rstrip("/")

HOST = parse.urlparse(url).netloc
PATTERN = '<a [^>]*href=[\'|"](.*?)[\'"].*?>' #Default link extract pattern
visited_links = [url] #All visited links go here

def split_and_normalize(url):
    scheme, loc, path, qs, anchor = parse.urlsplit(url)
    split = (scheme, loc, path, qs, anchor)
    normalize = parse.urlunsplit(split)
    return split,normalize

def crawl(_url,file_writer, verbose=arguments.disable_verbose):
    """

    :param _url: Url to extract links from
    :param verbose: Print outputs ?
    :return: None

    A small crawl function that will extract only LOCAL to domain links.
    No response checking at all.
    """

    if not verbose:
        print("Parsing url: " + _url)

    resp = req.urlopen(_url)
    page = resp.read()
    soup = BeautifulSoup(page, "lxml")
    title = soup.title.string
    if title is None:
        title = "No title available"
    # Extract interesting data from page
    page_links = re.findall(PATTERN, str(page))

    links_this_run = []

    for link in page_links:

        # Check if link is URL
        split, normalize = split_and_normalize(link)
        #print(page_links)
        # split[0] is the scheme
        #print("Split 0 is " +  split[0])
        #print("split 1 is " + split[1])
        if split[0] in ["http", "https", ""] and bool(link) is True:
            if split[1] == "" or split[1] == HOST: #Extract only local links
                if link not in links_this_run:
                    links_this_run.append(normalize)

    #Write sitemap chunk
    string = "<ul>\n"
    string += "\n".join(["\t\t\t\t<li>" + str(s) + "</li>" for s in links_this_run])
    string += "\n\t\t\t</ul>"
    output = "\n\t\t<url>\n\t\t\t<description>{0}</description>\n\t\t\t<loc>\n\t\t\t\t{1}/\n\t\t\t</loc>\n\t\t\t{2}\n\t\t</url>".format(title, _url, string)
    file_writer.write(output)


    for link in links_this_run:
        if link not in visited_links:
            visited_links.append(split_and_normalize(link)[1]) #1 is the normalized link/url
            try:
                crawl(parse.urljoin(_url,link), file_writer)
            except urllib.error.HTTPError as ERR:
                print("Print failed to parse " + str(_url) + "/n Stacktrace: /n" + str(ERR))
                continue


import os.path
from pathlib import Path
sitemap_path = os.path.join(str(Path.home()),"sitemap.xml")

print("Sitemap will be stored to: " + str(sitemap_path))
with open(sitemap_path, "w") as file:
    file.write('<?xml version="1.0" encoding="UTF-8"?>\n\t<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    crawl(url,file)
    file.write('</urlset>')
# Issues with XML do not use !

#####
##### Helpers
#####

from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests, csv, re, string, secrets
import sys, os


# BS html document creator returned with doc encoding
def getHTMLdocument(url):
  response = requests.get(url)
  return response.text, response.encoding

# Extract root URL from page
def root_url(full_url):
  return urlparse(full_url).scheme + '://' + urlparse(full_url).hostname + '/'

# Local scraper path
def local_path_helper(url):
  if ".net/g" in url:
    path_key = url.split(".net/g/").pop()
    return os.path.join(sys.path[0], (path_key))

# Generate a unique identifier
def generate_slug_id():
  return ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))

# Input text element | Encode tag, stringify, then clean text out the html tags
def clean_text(elem = '') :
  if isinstance(elem, str):
    soup = BeautifulSoup(elem, "html.parser")
    elem = str(soup.encode(formatter="html5"))
  elif elem.text and len(elem.text) > 0:
    elem = str(elem.encode(formatter="html5"))

  elem = remove_html_tags(elem)
  elem = remove_byte_encoding(elem)
  return elem

# Input a string | Removes bytes encoding from HTML encoding
def remove_byte_encoding(text):
  clean = text
  if text.startswith("b'"):
    clean =  re.sub("^b'", "", text)
  elif text.startswith('b"'):
    clean = re.sub('^b"', '', text)

  if text.endswith("'"):
    clean = re.sub("'$", "", clean)
  elif text.endswith('"'):
    clean = re.sub('"$', '', clean)
  return clean

# Input a string | Removes html tags from start/end of given string
def remove_html_tags(text):
  clean = re.compile('<.*?>')
  return re.sub(clean, '', text)


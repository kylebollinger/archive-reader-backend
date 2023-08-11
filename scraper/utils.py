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


def process_body_tag(body_tag):
  body_1=body_2=body_3=body_4=body_5=body_6=body_7=body_8=body_9=body_10=body_11=body_12=body_13=body_14=body_15 = ''
  body_1 = body_tag.encode(formatter="html5")

  # Split at 30000 Characters for CSV cell limit
  if len(body_1) > 30000:
    chunks = [body_1[i:i+30000] for i in range(0, len(body_1), 30000)]
    body_1 = chunks[0]
    body_2 = chunks[1]
    try:
      body_3 = chunks[2]
      body_4 = chunks[3]
      body_5 = chunks[4]
      body_6 = chunks[5]
      body_7 = chunks[6]
      body_8 = chunks[7]
      body_9 = chunks[8]
      body_10 = chunks[9]
      body_11 = chunks[10]
      body_12 = chunks[11]
      body_13 = chunks[12]
      body_14 = chunks[13]
      body_15 = chunks[14]
    except IndexError:
      print("[OK] Less than max characters")

  tags = [body_1, body_2, body_3, body_4, body_5, body_6, body_7, body_8, body_9, body_10, body_11, body_12, body_13, body_14, body_15]
  for idx, tag in enumerate(tags):
    if len(tag) > 0:
      tags[idx] = remove_byte_encoding(str(tag))

  return tags[0], tags[1], tags[2], tags[3], tags[4], tags[5], tags[6], tags[7], tags[8], tags[9], tags[10], tags[11], tags[12], tags[13], tags[14]
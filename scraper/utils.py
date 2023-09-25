from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests, csv, re, string, secrets
import sys, os, html


OUTPUT_DIR = "outputs"

# Ensure directories exist for processing
def register_base_dirs():
  dir_paths = [
    OUTPUT_DIR,
    f"{OUTPUT_DIR}/books",
    f"{OUTPUT_DIR}/books/txt",
    f"{OUTPUT_DIR}/books/html",
    f"{OUTPUT_DIR}/chapters",
  ]

  for dir in dir_paths:
    os.makedirs(dir, exist_ok=True)

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

# Process HTML entities in filenames
def clean_filename(filename):
  # Decode HTML entities
  decoded_filename = html.unescape(filename)

  # Remove non-alphanumeric characters
  # cleaned_filename = re.sub(r'[^a-zA-Z0-9 ]+', '', decoded_filename)

  return decoded_filename

# Process the filename before writing to disk
def save_file(file_name, file_content, encoding='txt', dir=OUTPUT_DIR):
  # Clean the filename
  filename = clean_filename(file_name)
  scrub_name = scrub_filename(filename)

  # Construct the directory path and ensure it exists
  directory_path = os.path.join(dir, encoding)
  os.makedirs(directory_path, exist_ok=True)

  # Construct the full file path
  file_path = os.path.join(directory_path, f"{scrub_name}.txt")

  # Write the content to the file
  with open(file_path, "a") as file:
    file.write(file_content)

# Clean and shorten a filename to make it safe for output
def scrub_filename(filename, max_length=48):
  """
  :param filename: The original filename.
  :param max_length: The maximum length for the cleaned filename.
  :return: A cleaned and shortened filename.
  """

  # Remove unsafe characters
  filename = re.sub(r'[<>:"/\\|?*]', '', filename)

  # Replace multiple spaces with a single space
  filename = re.sub(r'\s+', ' ', filename).strip()

  # Split the filename into name and extension
  name, ext = os.path.splitext(filename)

  # Remove trailing periods from the name
  name = name.rstrip('.')
  filename = name + ext

  # Shorten the filename if it's too long
  if len(filename) > max_length:
    # Split the filename into name and extension
    name, ext = os.path.splitext(filename)

    # Shorten the name part to fit within the max_length
    name = name[:max_length - len(ext)]
    filename = name + ext

  return filename
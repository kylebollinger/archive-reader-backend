import os, html, re


# Declare constants
OUTPUT_DIR = "outputs"


def clean_filename(filename):
    # Decode HTML entities
    decoded_filename = html.unescape(filename)

    # Remove non-alphanumeric characters
    # cleaned_filename = re.sub(r'[^a-zA-Z0-9 ]+', '', decoded_filename)

    return decoded_filename

def register_base_dirs():
    dir_paths = [OUTPUT_DIR, f"{OUTPUT_DIR}/txt", f"{OUTPUT_DIR}/html", f"{OUTPUT_DIR}/chapters"]

    for dir_path in dir_paths:
        os.makedirs(dir_path, exist_ok=True)


def save_file(file_name, file_content, encoding='txt', dir=OUTPUT_DIR):
    file_path = f"{dir}/{encoding}/{clean_filename(file_name)}"
    with open(f"{file_path}.txt", "a") as file:
        file.write(file_content)
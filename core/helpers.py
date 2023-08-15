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
    dir_paths = [
        OUTPUT_DIR,
        f"{OUTPUT_DIR}/books",
        f"{OUTPUT_DIR}/books/txt",
        f"{OUTPUT_DIR}/books/html",
        f"{OUTPUT_DIR}/chapters",
    ]

    for dir in dir_paths:
        os.makedirs(dir, exist_ok=True)


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


def scrub_filename(filename, max_length=48):
    """
    Clean and shorten a filename to make it safe for output.

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

    # Reassemble the filename
    filename = name + ext

    # Shorten the filename if it's too long
    if len(filename) > max_length:
        # Split the filename into name and extension
        name, ext = os.path.splitext(filename)

        # Shorten the name part to fit within the max_length
        name = name[:max_length - len(ext)]

        # Reassemble the filename
        filename = name + ext

    return filename
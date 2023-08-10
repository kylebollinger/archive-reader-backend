import html, re


def clean_filename(filename):
    # Decode HTML entities
    decoded_filename = html.unescape(filename)

    # Remove non-alphanumeric characters
    # cleaned_filename = re.sub(r'[^a-zA-Z0-9 ]+', '', decoded_filename)

    return decoded_filename

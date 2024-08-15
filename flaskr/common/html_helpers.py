from bs4 import BeautifulSoup

def clean_html(html_content):
    # Use a library like BeautifulSoup to strip HTML tags
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()
import io
import re
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF

def read_from_url(url: str) -> tuple[str, str]:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "").lower()
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        text = extract_pdf_text(r.content)
        return text, "pdf"
    else:
        text = extract_html_text(r.text)
        return text, "html"

def extract_pdf_text(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    texts = []
    for page in doc:
        texts.append(page.get_text("text"))
    return "\n".join(texts)

def extract_html_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = soup.get_text("\n")
    return re.sub(r"\n{2,}", "\n\n", text).strip()

def read_local_upload(file_storage) -> tuple[str, str]:
    filename = (file_storage.filename or "").lower()
    data = file_storage.read()
    if filename.endswith(".pdf"):
        return extract_pdf_text(data), "pdf"
    elif filename.endswith(('.html', '.htm', '.xhtml', '.xml', '.txt')):
        try:
            return extract_html_text(data.decode("utf-8", errors="ignore")), "html"
        except Exception:
            return data.decode("latin1", errors="ignore"), "text"
    else:
        # Try PDF first
        try:
            return extract_pdf_text(data), "pdf"
        except Exception:
            # Fallback text
            return data.decode("utf-8", errors="ignore"), "text"

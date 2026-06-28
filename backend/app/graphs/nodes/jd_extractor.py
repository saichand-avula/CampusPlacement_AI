import fitz

from langchain_community.document_loaders import PyPDFLoader

from graphs.state import mystate


def jd_extractor(state: mystate):
    # Extract text using PyPDFLoader
    loader = PyPDFLoader(state["jd_path"])
    documents = loader.load()

    jd_text = "\n".join(doc.page_content for doc in documents)

    # Extract hyperlinks using PyMuPDF
    doc = fitz.open(state["jd_path"])

    raw_links = []

    for page in doc:
        for link in page.get_links():
            uri = link.get("uri")
            if uri:
                raw_links.append(uri)

    # Remove duplicates while preserving order
    raw_links = list(dict.fromkeys(raw_links))

    return {
        "jd_text": jd_text,
        "raw_links": raw_links,
    }
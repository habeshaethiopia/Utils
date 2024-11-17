import streamlit as st
import fitz  # PyMuPDF

# Function to extract hyperlinks with their anchor text
def extract_hyperlinks(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    links_data = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for link in page.get_links():
            uri = link.get("uri")
            if uri:  # if there's a URL
                # Extract text around the link location if available
                rect = link["from"]  # Link rectangle
                words = page.get_text("words")  # List of words in the page
                # Filter words within the link's rectangle
                anchor_text = " ".join(
                    word[4] for word in words 
                    if fitz.Rect(word[:4]).intersects(rect)
                )
                links_data.append({"page": page_num + 1, "text": anchor_text, "url": uri})

    return links_data

# Streamlit App
st.title("PDF Hyperlink Extractor")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    links_data = extract_hyperlinks(uploaded_file)
    if links_data:
        st.write("Extracted Hyperlinks:")
        for link_info in links_data:
            st.write(f"Page {link_info['page']}: **{link_info['text']}**")
            st.markdown(f"[{link_info['url']}]({link_info['url']})")
    else:
        st.write("No hyperlinks found in the PDF.")

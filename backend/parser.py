# import pdfplumber

# def parse_resume(file):
#     content = ""
#     with pdfplumber.open(file) as pdf:
#         for page in pdf.pages:
#             content += page.extract_text()
    
#     return content
import pdfplumber

def parse_resume(file):
    print(f"🔍 Parsing file: {file}")  # Debugging

    content = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            print(f"📄 Extracted text (Page {page.page_number}): {extracted_text[:1000]}")  # Print first 100 chars
            if extracted_text:
                content += extracted_text + "\n"

    return content if content else "⚠️ No text found in the PDF!"

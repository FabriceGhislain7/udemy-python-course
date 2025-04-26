from PDFProcessing import PDFProcessor, PDFSecurity, PDFMerger
import os

def main():
    print("\n=== PDF Processing Toolkit ===\n")
    
    # Ensure necessary directories exist
    os.makedirs("output_pages", exist_ok=True)
    os.makedirs("pdfs_to_merge", exist_ok=True)
    
    try:
        # Example 1: Splitting a PDF
        print("1. Splitting a PDF:")
        input_pdf = "example.pdf"
        if not os.path.exists(input_pdf):
            raise FileNotFoundError(f"Input PDF '{input_pdf}' not found")
            
        splitter = PDFProcessor(input_pdf)
        print(f"Processing {input_pdf} with {splitter.get_page_count()} pages")
        splitter.split("output_pages")
        print(f"Success! PDF split into individual pages in 'output_pages' directory\n")
        
        # Example 2: Merging PDFs
        print("2. Merging PDFs:")
        merge_source = "pdfs_to_merge"
        if not os.listdir(merge_source):
            print(f"Note: '{merge_source}' directory is empty - add PDFs to merge")
        else:
            output_merged = "merged.pdf"
            PDFMerger.merge_folder(merge_source, output_merged)
            print(f"Success! Merged all PDFs from '{merge_source}' into '{output_merged}'\n")
        
        # Example 3: Text Extraction
        print("3. Extracting Text:")
        extractor = PDFProcessor(input_pdf)
        pages_to_extract = [1, 2]  # First two pages
        text = extractor.extract_text(pages_to_extract)
        print(f"Extracted text from pages {pages_to_extract} (first 200 chars):")
        print("-"*50)
        print(text[:200] + ("..." if len(text) > 200 else ""))
        print("-"*50 + "\n")
        
        # Example 4: PDF Security
        print("4. Adding Password Protection:")
        secured_pdf = "secured.pdf"
        password = "securepassword123"  # In real usage, get this securely
        pdf_security = PDFSecurity(input_pdf)
        pdf_security.encrypt(secured_pdf, password)
        print(f"Success! Created password-protected PDF: '{secured_pdf}'")
        print(f"Password: {password} (remember to change this in production)\n")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please ensure:")
        print("- Input PDF exists")
        print("- Required directories exist")
        print("- You have proper permissions")

if __name__ == "__main__":
    main()
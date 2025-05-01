import os
import PyPDF2

def extract_text_from_pdfs(pdf_folder):
    """
    Extract text from all PDF files in a folder and return as a single string
    """
    all_text = ""
    
    # Check if the folder exists
    if not os.path.exists(pdf_folder):
        print(f"Error: Folder '{pdf_folder}' does not exist")
        return all_text
    
    # Get all PDF files from the folder
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in '{pdf_folder}'")
        return all_text
    
    # Process each PDF file
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"Processing: {pdf_file}")
        
        try:
            # Open the PDF file
            with open(pdf_path, 'rb') as file:
                # Create PDF reader object
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get number of pages
                num_pages = len(pdf_reader.pages)
                print(f"  Pages: {num_pages}")
                
                # Extract text from each page
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    all_text += page_text + "\n\n"
                    
                all_text += f"\n--- End of {pdf_file} ---\n\n"
                
        except Exception as e:
            print(f"  Error processing {pdf_file}: {str(e)}")
    
    return all_text

def main():
    # Define the folder containing PDF files
    pdf_folder = "pdf"  # Change this to your PDF folder path
    
    # Extract text from all PDFs
    print(f"Extracting text from PDFs in '{pdf_folder}'...")
    all_text = extract_text_from_pdfs(pdf_folder)
    
    # Save to temp.txt
    if all_text:
        with open("temp.txt", "w", encoding="utf-8") as text_file:
            text_file.write(all_text)
        print(f"Text extracted and saved to temp.txt")
        print(f"Total characters extracted: {len(all_text)}")
    else:
        print("No text was extracted from PDFs")

if __name__ == "__main__":
    main()
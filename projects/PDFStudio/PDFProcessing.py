import os
import PyPDF2
from typing import List, Optional, Tuple, Union, Dict
from datetime import datetime
from PIL import Image
import io

class PDFProcessor:
    """
    A comprehensive class for performing various PDF operations including:
    - Metadata extraction
    - Splitting and merging
    - Text and image extraction
    - Page manipulation
    - Security features
    
    Attributes:
        file_path (str): Path to the PDF file.
        reader (PyPDF2.PdfReader): PDF reader object.
    """
    
    def __init__(self, file_path: str = None):
        """
        Initialize the PDFProcessor with a PDF file path.
        
        Args:
            file_path (str): Path to the PDF file. Can be None if creating new PDFs.
        """
        self.file_path = file_path
        self.reader = None
        
        if file_path is not None:
            self._validate_file()
            self.reader = PyPDF2.PdfReader(self.file_path)
    
    # ==================== CORE METHODS ====================
    
    def _validate_file(self) -> None:
        """Validate that the file exists and is a PDF."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"The file '{self.file_path}' does not exist.")
        if not self.file_path.lower().endswith('.pdf'):
            raise ValueError("The file must be a PDF (.pdf extension).")
    
    def get_page_count(self) -> int:
        """Return the number of pages in the PDF."""
        if self.reader is None:
            raise ValueError("No PDF file has been loaded.")
        return len(self.reader.pages)
    
    def save(self, output_path: str) -> None:
        """Save the current PDF to a new location"""
        if not self.reader:
            raise ValueError("No PDF content to save")
        
        writer = PyPDF2.PdfWriter()
        for page in self.reader.pages:
            writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        print(f"PDF saved successfully to {output_path}")
    
    # ==================== METADATA METHODS ====================
    
    def get_metadata(self) -> Dict[str, Union[str, datetime, int]]:
        """
        Get PDF metadata dictionary with:
        - Title, Author, Creator, Producer, Subject
        - Creation/Modification dates
        - Page count
        """
        if not self.reader:
            raise ValueError("No PDF file loaded")
            
        return {
            'title': self.reader.metadata.get('/Title', ''),
            'author': self.reader.metadata.get('/Author', ''),
            'creator': self.reader.metadata.get('/Creator', ''),
            'producer': self.reader.metadata.get('/Producer', ''),
            'subject': self.reader.metadata.get('/Subject', ''),
            'creation_date': self._parse_pdf_date(
                self.reader.metadata.get('/CreationDate', '')
            ),
            'modification_date': self._parse_pdf_date(
                self.reader.metadata.get('/ModDate', '')
            ),
            'pages': len(self.reader.pages)
        }
    
    def _parse_pdf_date(self, pdf_date: str) -> Optional[datetime]:
        """Parse PDF date string into Python datetime"""
        if not pdf_date:
            return None
        try:
            date_str = pdf_date[2:16]  # Extract YYYYMMDDHHmmSS
            return datetime.strptime(date_str, '%Y%m%d%H%M%S')
        except:
            return None
    
    # ==================== SPLITTING METHODS ====================
    
    def split(self, output_dir: str, prefix: str = "page_") -> None:
        """
        Split the PDF into individual pages.
        
        Args:
            output_dir (str): Directory to save the split pages.
            prefix (str): Prefix for output filenames. Default is "page_".
        """
        self.split_by_pages(output_dir, [(1, self.get_page_count())], prefix)
    
    def split_by_pages(self, output_dir: str, 
                      ranges: List[Tuple[int, int]] = None,
                      prefix: str = "section_") -> List[str]:
        """
        Split PDF into multiple files based on page ranges
        
        Args:
            output_dir: Directory to save split files
            ranges: List of (start, end) page tuples (1-based indexing)
                   If None, splits into individual pages
            prefix: Prefix for output filenames
        
        Returns:
            List of output file paths
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        total_pages = self.get_page_count()
        output_files = []
        
        if ranges is None:
            for i in range(total_pages):
                output_path = os.path.join(output_dir, f'{prefix}{i+1}.pdf')
                self._extract_pages(i+1, i+1, output_path)
                output_files.append(output_path)
        else:
            for i, (start, end) in enumerate(ranges):
                output_path = os.path.join(output_dir, f'{prefix}{i+1}.pdf')
                self._extract_pages(start, end, output_path)
                output_files.append(output_path)
        
        return output_files
    
    def _extract_pages(self, start: int, end: int, output_path: str) -> None:
        """Extract range of pages and save to new file"""
        writer = PyPDF2.PdfWriter()
        for i in range(start-1, min(end, self.get_page_count())):
            writer.add_page(self.reader.pages[i])
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    # ==================== MERGING METHODS ====================
    
    @staticmethod
    def merge(files: List[str], output_path: str) -> None:
        """
        Merge multiple PDF files into one.
        
        Args:
            files (List[str]): List of PDF file paths to merge.
            output_path (str): Path to save the merged PDF.
        """
        if not files:
            raise ValueError("No files provided for merging.")
        
        merger = PyPDF2.PdfMerger()
        
        try:
            for file in files:
                if not os.path.exists(file):
                    raise FileNotFoundError(f"File '{file}' not found.")
                merger.append(file)
            
            with open(output_path, "wb") as output_file:
                merger.write(output_file)
            
            print(f"Merged {len(files)} PDFs successfully to '{output_path}'")
        except Exception as e:
            merger.close()
            raise e
    
    @staticmethod
    def merge_folder(folder_path: str, output_path: str, 
                    sort_by: str = 'name') -> None:
        """
        Merge all PDFs in a folder
        
        Args:
            folder_path: Directory containing PDFs to merge
            output_path: Path to save merged PDF
            sort_by: How to sort files ('name' or 'date')
        """
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"'{folder_path}' is not a directory")
        
        pdf_files = [f for f in os.listdir(folder_path) 
                    if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            raise FileNotFoundError("No PDF files found in directory")
        
        if sort_by == 'name':
            pdf_files.sort()
        elif sort_by == 'date':
            pdf_files.sort(key=lambda x: os.path.getmtime(
                os.path.join(folder_path, x)))
        else:
            raise ValueError("sort_by must be 'name' or 'date'")
        
        PDFProcessor.merge(
            [os.path.join(folder_path, f) for f in pdf_files],
            output_path
        )
    
    # ==================== TEXT METHODS ====================
    
    def extract_text(self, page_numbers: Optional[List[int]] = None) -> str:
        """
        Extract text from the PDF.
        
        Args:
            page_numbers: Specific pages to extract from (1-based).
                         If None, extracts all pages.
        
        Returns:
            Extracted text concatenated with newlines
        """
        text_dict = self.extract_pages_text(page_numbers)
        return '\n'.join(text_dict.values())
    
    def extract_pages_text(self, page_numbers: List[int] = None) -> Dict[int, str]:
        """
        Extract text from specific pages
        
        Returns:
            Dictionary with page numbers as keys and text as values
        """
        if self.reader is None:
            raise ValueError("No PDF file has been loaded.")
            
        if page_numbers is None:
            page_numbers = range(1, self.get_page_count() + 1)
        
        result = {}
        for num in page_numbers:
            if num < 1 or num > self.get_page_count():
                raise ValueError(f"Invalid page number: {num}")
            result[num] = self.reader.pages[num-1].extract_text() or ""
        
        return result
    
    def search_text(self, search_terms: Union[str, List[str]], 
                   case_sensitive: bool = False) -> Dict[str, List[Tuple[int, int]]]:
        """
        Search for text in the PDF
        
        Args:
            search_terms: String or list of strings to search for
            case_sensitive: Whether search should be case sensitive
        
        Returns:
            Dictionary with search terms as keys and lists of 
            (page_num, position) tuples as values
        """
        if isinstance(search_terms, str):
            search_terms = [search_terms]
        
        results = {term: [] for term in search_terms}
        
        for page_num, page in enumerate(self.reader.pages, 1):
            text = page.extract_text() or ""
            if not case_sensitive:
                text = text.lower()
            
            for term in search_terms:
                search_term = term if case_sensitive else term.lower()
                pos = text.find(search_term)
                while pos != -1:
                    results[term].append((page_num, pos))
                    pos = text.find(search_term, pos + 1)
        
        return results
    
    # ==================== IMAGE METHODS ====================
    
    def extract_images(self, output_dir: str) -> List[str]:
        """
        Extract all images from PDF
        
        Args:
            output_dir: Directory to save extracted images
        
        Returns:
            List of paths to saved images
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        saved_files = []
        
        for page_num, page in enumerate(self.reader.pages, 1):
            if '/XObject' not in page['/Resources']:
                continue
                
            x_object = page['/Resources']['/XObject'].get_object()
            
            for obj in x_object:
                if x_object[obj]['/Subtype'] == '/Image':
                    image = x_object[obj]
                    image_data = image.get_data()
                    
                    extension = self._get_image_extension(image)
                    if not extension:
                        continue
                        
                    output_path = os.path.join(
                        output_dir, 
                        f'page_{page_num}_image_{len(saved_files)+1}{extension}'
                    )
                    
                    self._save_image(image_data, output_path)
                    saved_files.append(output_path)
        
        return saved_files
    
    def _get_image_extension(self, image) -> Optional[str]:
        """Determine file extension from image object"""
        if '/Filter' not in image:
            return None
            
        filters = image['/Filter']
        if isinstance(filters, PyPDF2.generic.ArrayObject):
            filters = [str(f) for f in filters]
        else:
            filters = [str(filters)]
        
        if '/DCTDecode' in filters:
            return '.jpg'
        elif '/JPXDecode' in filters:
            return '.jp2'
        elif '/CCITTFaxDecode' in filters:
            return '.tiff'
        elif '/JBIG2Decode' in filters:
            return '.jb2'
        return None
    
    def _save_image(self, image_data: bytes, output_path: str) -> None:
        """Save image data to file"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                img.save(output_path)
        except Exception as e:
            print(f"Failed to save image {output_path}: {e}")
    
    # ==================== PAGE MANIPULATION ====================
    
    def rotate_pages(self, page_numbers: List[int], 
                    rotation: int, output_path: str) -> None:
        """
        Rotate specific pages and save to a new PDF.
        
        Args:
            page_numbers: Page numbers to rotate (1-based index)
            rotation: Degrees to rotate (90, 180, or 270)
            output_path: Path to save modified PDF
        """
        if rotation not in (90, 180, 270):
            raise ValueError("Rotation must be 90, 180, or 270 degrees.")
        
        writer = PyPDF2.PdfWriter()
        
        for i in range(self.get_page_count()):
            page = self.reader.pages[i]
            if (i + 1) in page_numbers:
                page.rotate(rotation)
            writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    @staticmethod
    def create_from_pages(sources: List[str], 
                         page_selections: List[List[int]], 
                         output_path: str) -> None:
        """
        Create new PDF from selected pages of multiple source PDFs
        
        Args:
            sources: List of source PDF files
            page_selections: For each source, list of pages to include (1-based)
            output_path: Path to save new PDF
        """
        if len(sources) != len(page_selections):
            raise ValueError("Sources and page selections must match in length.")
        
        writer = PyPDF2.PdfWriter()
        
        for file, pages in zip(sources, page_selections):
            reader = PyPDF2.PdfReader(file)
            for page_num in pages:
                if page_num < 1 or page_num > len(reader.pages):
                    raise ValueError(f"Invalid page {page_num} in {file}")
                writer.add_page(reader.pages[page_num - 1])
        
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    # ==================== SECURITY METHODS ====================
    
    def encrypt(self, output_path: str, password: str, 
               permissions: Dict[str, bool] = None) -> None:
        """
        Encrypt PDF with password protection
        
        Args:
            output_path: Path to save encrypted PDF
            password: User password required to open
            permissions: Dictionary of allowed operations:
                - print: Allow printing
                - modify: Allow modifications
                - copy: Allow text copying
                - annotate: Allow annotations
        """
        if not permissions:
            permissions = {
                'print': True,
                'modify': False,
                'copy': False,
                'annotate': False
            }
        
        writer = PyPDF2.PdfWriter()
        
        for page in self.reader.pages:
            writer.add_page(page)
        
        if self.reader.metadata:
            writer.add_metadata(self.reader.metadata)
        
        writer.encrypt(
            user_password=password,
            owner_password=None,
            use_128bit=True,
            permissions=permissions
        )
        
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    def decrypt(self, output_path: str, password: str) -> None:
        """
        Remove password protection from PDF
        
        Args:
            output_path: Path to save decrypted PDF
            password: Current PDF password
        """
        if not self.reader.is_encrypted:
            raise ValueError("PDF is not encrypted")
        
        if not self.reader.decrypt(password):
            raise ValueError("Incorrect password")
        
        writer = PyPDF2.PdfWriter()
        for page in self.reader.pages:
            writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
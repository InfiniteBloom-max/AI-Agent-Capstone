import fitz  # PyMuPDF
from PIL import Image
import io
import os
from pathlib import Path
from typing import List, Dict

class ImageExtractor:
    """Extract images from PDFs using PyMuPDF"""
    
    def __init__(self, output_dir: str = "data/extracted_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_images(self, pdf_path: str) -> List[Dict[str, str]]:
        """
        Extract all images from a PDF
        
        Returns:
            List of dicts with 'path', 'page', 'index'
        """
        images = []
        
        try:
            doc = fitz.open(pdf_path)
            pdf_name = Path(pdf_path).stem
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    
                    if base_image:
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Save image
                        image_filename = f"{pdf_name}_page{page_num+1}_img{img_index+1}.{image_ext}"
                        image_path = self.output_dir / image_filename
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        images.append({
                            "path": str(image_path),
                            "page": page_num + 1,
                            "index": img_index + 1,
                            "size": len(image_bytes)
                        })
                        
                        print(f"  Extracted: {image_filename} ({len(image_bytes)} bytes)")
            
            doc.close()
            
        except Exception as e:
            print(f"Error extracting images: {e}")
        
        return images
    
    def cleanup_images(self):
        """Remove all extracted images"""
        for file in self.output_dir.glob("*"):
            if file.is_file():
                file.unlink()

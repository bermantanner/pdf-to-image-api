from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import fitz  # PyMuPDF
import base64

app = FastAPI(title="PDF to Image Converter")

class PDFRequest(BaseModel):
    pdf_url: str

@app.post("/convert")
def convert_pdf(request: PDFRequest):
    try:
        # download the PDF from link
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(request.pdf_url, headers=headers)
        response.raise_for_status()

        # open the PDF in memory
        doc = fitz.open(stream=response.content, filetype="pdf")
        
        images_array = []
        
        # loop through every page and turn it into a high res JPEG
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # testing Matrix(2, 2) zooms in 2x so the images arent blurry
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
            img_bytes = pix.tobytes("jpeg")
            
            # converting binary image to a base64 string to send safely in JSON
            b64_string = base64.b64encode(img_bytes).decode("utf-8")
            
            images_array.append({
                "image_index": page_num,
                "base64_data": b64_string
            })
            
        return {
            "status": "success", 
            "total_images": len(images_array),
            "images": images_array
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
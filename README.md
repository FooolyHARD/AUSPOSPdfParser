# pdftolatex   
## Description
A simple tool for take needed insformation from AUSPOS .pdf files

## Usage
To use tool run `convert_pdf.py` with either the `--filepath` argument to convert a single PDF or the `--folderpath` argument to convert every PDF file in the folder. 

    python convert_pdf.py --filepath docs/example.pdf
    python convert_pdf.py --folderpath docs/example/

## Notes
### Packages Required
- OpenCV4 (cv2)
- pytesseract 
- pillow
- tqdm


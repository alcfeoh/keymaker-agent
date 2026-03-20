---
name: pdf-signing
description: A skill to automatically sign French 'Devis' style PDFs using pre-compiled transparent signature images.
---

# PDF Signing Skill

## Description
This skill provides the ability to automatically sign PDF documents. It utilizes a Python script based on PyMuPDF (fitz) to seamlessly place transparent signature PNGs onto the page. By default, it looks for specific anchor text in French "Devis" (quotation) PDFs, but can also fallback to a generic placement at the bottom of the last page for any PDF.

## Prerequisites
- **Python**: 3.x
- **Libraries**: `PyMuPDF` (`fitz`), `Pillow` (if image processing is required).
- The signature images must be prepared beforehand as transparent PNGs or GIFs. In this case, they are permanently stored in:
  - `~/Dropbox/obsidian-brain/3 RESOURCE/Bon pour accord_transparent.png`
  - `~/Dropbox/obsidian-brain/3 RESOURCE/Alain Chautard_transparent.png`
  - `~/Dropbox/obsidian-brain/3 RESOURCE/signature-alain.gif`

## Usage Instructions

To sign a new PDF, you must utilize the `sign_pdf.py` script located in `pdf-signer/sign_pdf.py` (or recreated as needed below). 

### How the Script Works
The script first attempts to find native text anchors on the final page (or preceding pages if not found). **If the PDF only consists of scanned images, it will automatically employ OCR (Optical Character Recognition) via Tesseract.** To avoid matching random text, it picks the lowest match on the page.
1. **Name**: It looks for variations like `NOM DU SIGNATAIRE`, `MENTION MANUSCRITE DU NOM`, or `NOM` and places the name image to the right.
2. **Location**: It looks for variations like `FAIT À`, `FAIT A`, `À :`, or `A :` and places the location text ("Languidic") next to it.
3. **Date**: It looks for variations like `DATE :`, `LE :`, `DATE`, or `LE` and places the dynamic current date (e.g., "20 mars 2026") next to it.
4. **Signature Box**: If a standalone `SIGNATURE` keyword is found without the other anchors, the script will base the entire layout around it.

If no anchors are identified even after the OCR pass, the script employs a **fallback layout** placing all the elements sequentially at the bottom-left of the final page. This makes the script capable of signing any arbitrary PDF document.

### Execution
Activate the python environment and run the script against the target PDF.
```bash
cd /Users/alainchautard/code-repos/keymaker-agent/pdf-signer
source venv/bin/activate
python sign_pdf.py /path/to/document.pdf
```
It will generate a new document named `signed_document.pdf` in the target directory.

## Maintenance Notes
If the structure of the "Devis" PDF changes significantly (different spacing, different keywords), the vertical and horizontal absolute coordinates (e.g., `x=180`, `y+15`) within `sign_pdf.py` will have to be tweaked by searching the target bounds in `PyMuPDF` and logging the `Rect` dimensions.

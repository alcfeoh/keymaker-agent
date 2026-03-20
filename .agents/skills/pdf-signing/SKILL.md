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
The script first attempts to find specific anchor text on the final page of the PDF to align the signature blocks:
1. **`NOM DU SIGNATAIRE:`**: The name image (`Alain Chautard_transparent.png`) is placed to the right of this text.
2. **`FAIT A :`**: The location text ("Languidic") is placed next to this anchor.
3. **`LE :`**: The current date text (e.g. "20 mars 2026", generated dynamically) is placed next to this anchor.
4. **Signature Area**: "Bon pour accord_transparent.png" and the main signature GIF are placed vertically below the `FAIT A :` bounds.

If these specific anchors are not found, the script employs a **fallback layout**. It will place the location, the dynamic current date, the "Bon pour accord" watermark, the signature image, and the name image sequentially at the bottom-left of the final page. This makes the script capable of signing any arbitrary PDF document.

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

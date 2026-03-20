import fitz  # PyMuPDF
import sys
import os
from pathlib import Path

from datetime import datetime

# Setup constants
RESOURCE_DIR = os.path.expanduser("~/Dropbox/obsidian-brain/3 RESOURCE/")
SIGNATURE_FILE = os.path.join(RESOURCE_DIR, "signature-alain.gif")
BPA_PNG = os.path.join(RESOURCE_DIR, "Bon pour accord_transparent.png")
NAME_PNG = os.path.join(RESOURCE_DIR, "Alain Chautard_transparent.png")

MONTHS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
now = datetime.now()

LOCATION = "Languidic"
DATE_STR = f"{now.day} {MONTHS_FR[now.month - 1]} {now.year}"

def sign_pdf(input_pdf, output_pdf=None):
    if not output_pdf:
        p = Path(input_pdf)
        output_pdf = str(p.with_name(f"signed_{p.name}"))

    if not os.path.exists(SIGNATURE_FILE):
        print(f"Error: Signature file not found at {SIGNATURE_FILE}")
        sys.exit(1)
        
    has_bpa = os.path.exists(BPA_PNG)
    has_name = os.path.exists(NAME_PNG)

    print(f"Opening {input_pdf}...")
    doc = fitz.open(input_pdf)
    
    target_page = doc[-1] # Default to last page
    
    # We will search the last page for specific anchors
    found_any = False
    
    def find_lowest_rect(page, keywords, tp=None):
        for kw in keywords:
            rects = page.search_for(kw, textpage=tp)
            if rects:
                # Return the rect closest to the bottom of the page (highest y1)
                return sorted(rects, key=lambda r: r.y1, reverse=True)[0]
        return None

    NOM_KEYWORDS = [
        "NOM DU SIGNATAIRE :", "NOM DU SIGNATAIRE:", "NOM DU SIGNATAIRE",
        "MENTION MANUSCRITE DU NOM", "MENTION MANUSCRITE",
        "NOM ET SIGNATURE", "NOM :", "NOM:", "NOM"
    ]
    FAIT_KEYWORDS = [
        "FAIT A :", "FAIT À :", "FAIT A:", "FAIT À:", "FAIT A", "FAIT À",
        "À :", "A :", "À:", "A:"
    ]
    LE_KEYWORDS = [
        "DATE :", "DATE:", "DATE",
        "LE :", "LE:", "LE"
    ]
    SIG_KEYWORDS = [
        "SIGNATURE :", "SIGNATURE:", "SIGNATURE"
    ]
    
    for use_ocr in [False, True]:
        if found_any: break
        
        for page in reversed(doc):
            tp = None
            if use_ocr:
                try:
                    tp = page.get_textpage_ocr(flags=0, language='eng')
                except Exception:
                    continue
                    
            rect_nom = find_lowest_rect(page, NOM_KEYWORDS, tp)
            rect_fait = find_lowest_rect(page, FAIT_KEYWORDS, tp)
            rect_le = find_lowest_rect(page, LE_KEYWORDS, tp)
            rect_sig = find_lowest_rect(page, SIG_KEYWORDS, tp)
            
            if rect_nom or rect_fait or rect_le or rect_sig:
                found_any = True
                
                # Base the layout on the lowest available anchor
                anchors = [r for r in [rect_nom, rect_fait, rect_le, rect_sig] if r is not None]
                base_rect = sorted(anchors, key=lambda r: r.y1, reverse=True)[0]
                
                # Place Name image to the right of "NOM DU SIGNATAIRE:" if found, else default
                if rect_nom:
                    name_x = rect_nom.x1 + 10
                    name_y = rect_nom.y0 - 10
                else:
                    name_x = base_rect.x0 + 100
                    name_y = base_rect.y1 + 50
                    
                if has_name:
                    name_rect = fitz.Rect(name_x, name_y, name_x + 120, name_y + 30)
                    page.insert_image(name_rect, filename=NAME_PNG)
                else:
                    page.insert_text((name_x, name_y + 15), "Alain Chautard", fontsize=12, fontname="helv", color=(0, 0, 0))

                # Place Location next to "FAIT A :"
                fait_x = rect_fait.x1 + 10 if rect_fait else base_rect.x0
                fait_y = rect_fait.y1 if rect_fait else base_rect.y0 - 20
                page.insert_text((fait_x, fait_y), LOCATION, fontsize=12, fontname="helv", color=(0, 0, 0))
                
                # Place Date next to "LE :"
                le_x = rect_le.x1 + 10 if rect_le else fait_x + 100
                le_y = rect_le.y1 if rect_le else fait_y
                page.insert_text((le_x, le_y), DATE_STR, fontsize=12, fontname="helv", color=(0, 0, 0))
                
                # Place "Bon pour accord" and Signature below the lowest anchor
                curr_y = base_rect.y1 + 15
                sig_x = base_rect.x0
                
                # "Bon pour accord"
                if has_bpa:
                    bpa_rect = fitz.Rect(sig_x, curr_y, sig_x + 120, curr_y + 30)
                    page.insert_image(bpa_rect, filename=BPA_PNG)
                    curr_y += 35
                else:
                    page.insert_text((sig_x, curr_y + 15), "Bon pour accord", fontsize=12, fontname="helv", color=(0, 0, 0))
                    curr_y += 20
                    
                # Signature Image
                img_rect = fitz.Rect(sig_x, curr_y, sig_x + 150, curr_y + 50)
                page.insert_image(img_rect, filename=SIGNATURE_FILE)
                
                print(f"Signature blocks aligned based on anchors (OCR={use_ocr}) on page {page.number + 1}")
                break
            
    if not found_any:
        print("Could not find specific anchors. Placing at the bottom of the last page.")
        page = doc[-1] # Fallback to the last page
        rect = page.rect
        bottom_y = rect.y1 - 150 # Start 150 points from the bottom edge
        margin_x = 50
        
        # Location and Date
        page.insert_text((margin_x, bottom_y), f"Fait à {LOCATION}, le {DATE_STR}", fontsize=12, fontname="helv", color=(0, 0, 0))
        
        curr_y = bottom_y + 10
        
        # "Bon pour accord"
        if has_bpa:
            bpa_rect = fitz.Rect(margin_x, curr_y, margin_x + 120, curr_y + 30)
            page.insert_image(bpa_rect, filename=BPA_PNG)
            curr_y += 35
        else:
            page.insert_text((margin_x, curr_y + 15), "Bon pour accord", fontsize=12, fontname="helv", color=(0, 0, 0))
            curr_y += 20
            
        # Signature Image
        img_rect = fitz.Rect(margin_x, curr_y, margin_x + 150, curr_y + 50)
        page.insert_image(img_rect, filename=SIGNATURE_FILE)

        # Name Image
        if has_name:
            curr_y += 50
            name_rect = fitz.Rect(margin_x, curr_y, margin_x + 120, curr_y + 30)
            page.insert_image(name_rect, filename=NAME_PNG)
        else:
            curr_y += 65
            page.insert_text((margin_x, curr_y), "Alain Chautard", fontsize=12, fontname="helv", color=(0, 0, 0))

    doc.save(output_pdf)
    print(f"Successfully saved signed PDF to {output_pdf}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sign_pdf.py <input.pdf> [output.pdf]")
        sys.exit(1)
        
    in_pdf = sys.argv[1]
    out_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    
    sign_pdf(in_pdf, out_pdf)

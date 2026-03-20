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
    
    for page in reversed(doc):
        inst_nom = page.search_for("NOM DU SIGNATAIRE:")
        inst_fait = page.search_for("FAIT A :")
        inst_le = page.search_for("LE :")
        
        if inst_nom and inst_fait and inst_le:
            found_any = True
            rect_nom = inst_nom[0]
            rect_fait = inst_fait[0]
            rect_le = inst_le[-1]
            
            # Place Name image to the right of "NOM DU SIGNATAIRE:"
            if has_name:
                # Placing safely to the right of the label text.
                # Assuming label ends roughly around x=160
                name_rect = fitz.Rect(180, rect_nom.y0 - 10, 300, rect_nom.y0 + 20)
                page.insert_image(name_rect, filename=NAME_PNG)
            else:
                page.insert_text((180, rect_nom.y1), "Alain Chautard", fontsize=12, fontname="helv", color=(0, 0, 0))

            # Place Location next to "FAIT A :"
            page.insert_text((90, rect_fait.y1), LOCATION, fontsize=12, fontname="helv", color=(0, 0, 0))
            
            # Place Date next to "LE :"
            # LE is slightly further to the right horizontally than FAIT A
            page.insert_text((245, rect_le.y1), DATE_STR, fontsize=12, fontname="helv", color=(0, 0, 0))
            
            # Place "Bon pour accord" and Signature below the FAIT A zone
            curr_y = rect_le.y1 + 15
            
            # "Bon pour accord"
            if has_bpa:
                bpa_rect = fitz.Rect(80, curr_y, 200, curr_y + 30)
                page.insert_image(bpa_rect, filename=BPA_PNG)
                curr_y += 35
            else:
                page.insert_text((80, curr_y + 15), "Bon pour accord", fontsize=12, fontname="helv", color=(0, 0, 0))
                curr_y += 20
                
            # Signature Image
            img_rect = fitz.Rect(80, curr_y, 230, curr_y + 50)
            page.insert_image(img_rect, filename=SIGNATURE_FILE)
            
            print(f"Signature blocks aligned individually next to relative anchors on page {page.number + 1}")
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

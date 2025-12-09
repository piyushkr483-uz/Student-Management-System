import os
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import markdown
import cairosvg

BASE = Path(__file__).resolve().parents[1]
MD = BASE / 'PROJECT_REPORT.md'
OUT = BASE / 'PROJECT_REPORT.pdf'
SCREENSHOTS_DIR = BASE / 'screenshots'

def md_to_plain(md_text):
    html = markdown.markdown(md_text)
    # remove HTML tags for a simple plain-text representation
    text = re.sub('<[^<]+?>', '', html)
    return text


def convert_svgs_to_pngs(screenshot_files):
    png_files = []
    for svg in screenshot_files:
        svg_path = SCREENSHOTS_DIR / svg
        if not svg_path.exists():
            continue
        png_path = SCREENSHOTS_DIR / (svg_path.stem + '.png')
        try:
            cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=1200)
            png_files.append(png_path)
        except Exception as e:
            print(f"Failed to convert {svg_path}: {e}")
    return png_files


def build_pdf():
    if not MD.exists():
        raise SystemExit('PROJECT_REPORT.md not found')
    md_text = MD.read_text(encoding='utf-8')
    plain = md_to_plain(md_text)

    doc = SimpleDocTemplate(str(OUT), pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    heading = ParagraphStyle('Heading', parent=styles['Heading1'], alignment=0)

    story = []
    # Title
    first_line = plain.strip().splitlines()[0]
    story.append(Paragraph(first_line, heading))
    story.append(Spacer(1, 6))

    # Add the rest in paragraphs, splitting by double-newline
    body = '\n\n'.join(plain.split('\n\n')[1:])
    # Limit paragraph length to avoid layout issues
    for para in body.split('\n\n'):
        para = para.strip()
        if not para:
            continue
        # replace multiple newlines
        para = para.replace('\n', ' ')
        story.append(Paragraph(para, normal))
        story.append(Spacer(1, 6))

    # Add screenshots
    svg_files = [f for f in os.listdir(SCREENSHOTS_DIR) if f.lower().endswith('.svg')]
    png_files = convert_svgs_to_pngs(svg_files)

    for png in png_files:
        # scale image to page width
        try:
            img = Image(str(png))
            max_width = (A4[0] - 40*mm)
            if img.drawWidth > max_width:
                ratio = max_width / img.drawWidth
                img.drawWidth = img.drawWidth * ratio
                img.drawHeight = img.drawHeight * ratio
            story.append(Spacer(1,12))
            story.append(img)
            story.append(Spacer(1,12))
        except Exception as e:
            print(f"Failed to add image {png}: {e}")

    doc.build(story)
    print('PDF written to', OUT)

if __name__ == '__main__':
    build_pdf()

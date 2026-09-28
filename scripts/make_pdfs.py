"""Optional: render the synthetic notes in data/ as PDFs (data/pdf/). Needs: pip install reportlab"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

DATA = Path(__file__).resolve().parent.parent / "data"
(DATA / "pdf").mkdir(exist_ok=True)

for txt in sorted(DATA.glob("P*.txt")):
    c = canvas.Canvas(str(DATA / "pdf" / f"{txt.stem}.pdf"), pagesize=letter)
    y = 740
    for i, line in enumerate(txt.read_text().splitlines()):
        c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 10)
        c.drawString(56, y, line)
        y -= 16
    c.save()
    print("wrote", txt.stem + ".pdf")

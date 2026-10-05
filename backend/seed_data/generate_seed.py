"""
DocuMine Seed Data Generator
Generates all synthetic seed documents for the Kranti OCP demo corpus.
Run: python generate_seed.py
"""
import os
import sys
from datetime import datetime

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def make_docx_geological_a():
    """DocA — Geological Report FY2022-23. Reserve=142.6 MT, Grade=G8, Method=Cross-Sectional."""
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Title
    title = doc.add_heading("GEOLOGICAL REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph("KRANTI OPENCAST PROJECT (OCP), FY 2022-23")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].bold = True
    sub.runs[0].font.size = Pt(13)

    doc.add_paragraph()

    # Header Table
    table = doc.add_table(rows=8, cols=2)
    table.style = "Table Grid"
    rows_data = [
        ("Mine Name", "Kranti Opencast Project (OCP)"),
        ("Company", "Eastern Coalfields Limited (ECL)"),
        ("Location", "Raniganj Coalfield, Paschim Bardhaman, West Bengal"),
        ("Mine Type", "Opencast"),
        ("Fiscal Year", "2022-23"),
        ("Report Date", "March 31, 2023"),
        ("Coal Grade", "G8"),
        ("Estimation Method", "Cross-Sectional Method"),
    ]
    for i, (k, v) in enumerate(rows_data):
        table.rows[i].cells[0].text = k
        table.rows[i].cells[1].text = v
        table.rows[i].cells[0].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    doc.add_heading("1. Introduction", 1)
    doc.add_paragraph(
        "The Kranti Opencast Project (OCP), operated by Eastern Coalfields Limited (ECL) under the Ministry of Coal, "
        "Government of India, is located in the Raniganj Coalfield belt of Paschim Bardhaman district, West Bengal. "
        "The mine has been in continuous operation since 1987 and constitutes a significant contributor to ECL's "
        "annual production targets under the national energy security framework."
    )
    doc.add_paragraph(
        "This geological report covers the assessment period FY 2022-23, presenting updated reserve estimates, "
        "seam-wise geological characterisation, and production performance metrics. The estimation follows the "
        "Cross-Sectional Method as per Indian Bureau of Mines (IBM) guidelines for reserve computation."
    )

    doc.add_heading("2. Geological Setting", 1)
    doc.add_paragraph(
        "The coalfield falls within the Gondwana sedimentary basin. The productive seams (Seam-II, Seam-III, Seam-IV) "
        "dip at 5°–12° towards the north-northwest at depths ranging from 35 to 120 metres below the surface. "
        "Overburden consists of sandstone, shale, and carbonaceous shale inter-beds. The stripping ratio for the "
        "current mining block averages 3.8 m³/tonne."
    )
    doc.add_paragraph(
        "Ground conditions are generally stable. Hydrogeological studies indicate moderate aquifer presence in the "
        "Barakar Formation. Controlled blasting protocols and slope monitoring systems are in place as per DGMS directives."
    )

    doc.add_heading("3. Reserve Estimation", 1)
    doc.add_paragraph(
        "Coal reserves have been estimated using the Cross-Sectional Method, verified by drill-hole data from "
        "90 exploratory boreholes. The following table summarises the seam-wise reserve estimates as of FY 2022-23:"
    )

    rtable = doc.add_table(rows=5, cols=4)
    rtable.style = "Table Grid"
    headers = ["Seam", "Area (ha)", "Average Thickness (m)", "Reserve (MT)"]
    for j, h in enumerate(headers):
        rtable.rows[0].cells[j].text = h
        rtable.rows[0].cells[j].paragraphs[0].runs[0].bold = True
    data = [
        ("Seam-II", "420", "4.8", "48.2"),
        ("Seam-III", "380", "5.6", "52.7"),
        ("Seam-IV", "310", "4.3", "41.7"),
        ("TOTAL", "—", "—", "142.6"),
    ]
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            rtable.rows[i + 1].cells[j].text = val

    doc.add_paragraph()
    doc.add_paragraph(
        "Total Estimated Coal Reserve: 142.6 Million Tonnes (MT)\n"
        "Coal Grade: G8 (as per BIS IS 770:2015 classification)\n"
        "Estimation Method: Cross-Sectional Method\n"
        "Confidence Level: Indicated (Category B)"
    ).runs[0].bold = False

    doc.add_heading("4. Annual Production", 1)
    doc.add_paragraph(
        "Annual coal production target for FY 2022-23: 3.80 Million Tonnes. "
        "Actual production achieved: 3.76 MT (98.9% of target). Overburden removal: 14.3 MCM."
    )

    doc.add_heading("5. Environmental Notes", 1)
    doc.add_paragraph(
        "The project operates under Environmental Clearance No. J-11015/77/2004-IA.II(M) dated 14 March 2005, "
        "as amended. Green belt development, surface water quality monitoring, and dust suppression measures "
        "are maintained in compliance with MoEFCC conditions."
    )

    path = os.path.join(OUT_DIR, "DocA_Geological_Report_FY2022-23.docx")
    doc.save(path)
    print(f"  ✓ {os.path.basename(path)}")


def make_docx_geological_b():
    """DocB — Geological Report FY2023-24. Reserve=138.9 MT, Method=Polygon (deliberate change)."""
    from docx import Document
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    title = doc.add_heading("GEOLOGICAL REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph("KRANTI OPENCAST PROJECT (OCP), FY 2023-24")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].bold = True
    sub.runs[0].font.size = Pt(13)

    doc.add_paragraph()

    table = doc.add_table(rows=8, cols=2)
    table.style = "Table Grid"
    rows_data = [
        ("Mine Name", "Kranti Opencast Project (OCP)"),
        ("Company", "Eastern Coalfields Limited (ECL)"),
        ("Location", "Raniganj Coalfield, Paschim Bardhaman, West Bengal"),
        ("Mine Type", "Opencast"),
        ("Fiscal Year", "2023-24"),
        ("Report Date", "March 31, 2024"),
        ("Coal Grade", "G8"),
        ("Estimation Method", "Polygon Method"),
    ]
    for i, (k, v) in enumerate(rows_data):
        table.rows[i].cells[0].text = k
        table.rows[i].cells[1].text = v
        table.rows[i].cells[0].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    doc.add_heading("1. Introduction", 1)
    doc.add_paragraph(
        "This geological report for FY 2023-24 presents the updated reserve assessment for Kranti Opencast Project, "
        "based on revised borehole data and updated geological mapping conducted during the previous year. "
        "Production planning for the upcoming fiscal year is based on these revised estimates."
    )
    doc.add_paragraph(
        "Reserves have been re-estimated using the Polygon Method to improve spatial accuracy in the deeper seam "
        "blocks. This report supersedes the FY 2022-23 geological report for reserve planning purposes."
    )

    doc.add_heading("2. Geological Setting", 1)
    doc.add_paragraph(
        "No major structural changes have been identified compared to the previous year's assessment. Minor "
        "faulting at Block-7 has been incorporated into the updated geological model, resulting in a revised "
        "mineable reserve estimate for that block."
    )

    doc.add_heading("3. Reserve Estimation", 1)
    rtable = doc.add_table(rows=5, cols=4)
    rtable.style = "Table Grid"
    headers = ["Seam", "Area (ha)", "Average Thickness (m)", "Reserve (MT)"]
    for j, h in enumerate(headers):
        rtable.rows[0].cells[j].text = h
        rtable.rows[0].cells[j].paragraphs[0].runs[0].bold = True
    data = [
        ("Seam-II", "415", "4.7", "47.1"),
        ("Seam-III", "372", "5.5", "50.8"),
        ("Seam-IV", "302", "4.2", "41.0"),
        ("TOTAL", "—", "—", "138.9"),
    ]
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            rtable.rows[i + 1].cells[j].text = val

    doc.add_paragraph()
    doc.add_paragraph(
        "Total Estimated Coal Reserve: 138.9 Million Tonnes (MT)\n"
        "Coal Grade: G8\n"
        "Estimation Method: Polygon Method\n"
        "Confidence Level: Indicated (Category B)"
    )

    doc.add_heading("4. Annual Production", 1)
    doc.add_paragraph(
        "Annual coal production for FY 2023-24: 3.91 Million Tonnes. "
        "Overburden removal: 15.1 MCM. Stripping ratio: 3.87 m³/tonne."
    )

    doc.add_heading("5. Environmental Notes", 1)
    doc.add_paragraph(
        "Environmental compliance monitoring continues as per MoEFCC conditions. "
        "Plantation area increased to 48.2 hectares during FY 2023-24. "
        "Water quality monitoring at 6 stations shows all parameters within permissible limits."
    )

    path = os.path.join(OUT_DIR, "DocB_Geological_Report_FY2023-24.docx")
    doc.save(path)
    print(f"  ✓ {os.path.basename(path)}")


def make_xlsx_production_log():
    """DocC — Monthly Production Log FY2023-24. Monthly sum = 3.85 MT (conflicts with DocB's 3.91)."""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Production_Log_FY2023-24"

    # Mine header
    ws.merge_cells("A1:E1")
    ws["A1"] = "Kranti Opencast Project (OCP) — Eastern Coalfields Limited (ECL)"
    ws["A1"].font = Font(bold=True, size=13, color="1F3864")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 25

    ws.merge_cells("A2:E2")
    ws["A2"] = "Monthly Coal Production Log — FY 2023-24"
    ws["A2"].font = Font(bold=True, size=11, color="2F5597")
    ws["A2"].alignment = Alignment(horizontal="center")

    # Column headers
    headers = ["Month", "Coal_Production_MT", "OB_Removal_MCM", "Equipment_Hours", "Remarks"]
    blue_fill = PatternFill(start_color="1F3864", end_color="1F3864", fill_type="solid")
    thin = Side(style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF", size=10)
        cell.fill = blue_fill
        cell.alignment = Alignment(horizontal="center")
        cell.border = border

    # Monthly data (sums to 3.85 MT — DELIBERATE CONFLICT with DocB's 3.91 MT)
    monthly_data = [
        ("April 2023",    0.31, 1.18, 682,  "Normal operations"),
        ("May 2023",      0.33, 1.26, 715,  "Normal operations"),
        ("June 2023",     0.28, 1.07, 598,  "Monsoon onset — partial day losses"),
        ("July 2023",     0.30, 1.14, 620,  "Monsoon — reduced blast frequency"),
        ("August 2023",   0.32, 1.22, 670,  "Monsoon — pumping operations active"),
        ("September 2023",0.34, 1.30, 710,  "Post-monsoon recovery"),
        ("October 2023",  0.35, 1.33, 740,  "Full operations resumed"),
        ("November 2023", 0.33, 1.26, 718,  "Normal operations"),
        ("December 2023", 0.32, 1.22, 700,  "Normal operations"),
        ("January 2024",  0.31, 1.18, 685,  "Scheduled maintenance — Shovel #3"),
        ("February 2024", 0.29, 1.11, 645,  "Equipment maintenance"),
        ("March 2024",    0.27, 1.03, 598,  "Year-end inventory; blast moratorium day 28-31"),
    ]

    light_fill = PatternFill(start_color="EBF3FB", end_color="EBF3FB", fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    for i, row_data in enumerate(monthly_data):
        row_num = i + 5
        fill = light_fill if i % 2 == 0 else white_fill
        for col, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col, value=val)
            cell.fill = fill
            cell.border = border
            cell.alignment = Alignment(horizontal="center" if col > 1 else "left")
            if col == 2:
                cell.number_format = "0.00"

    # Total row
    total_row = len(monthly_data) + 5
    total_fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
    ws.cell(row=total_row, column=1, value="TOTAL").font = Font(bold=True)
    ws.cell(row=total_row, column=1).fill = total_fill
    ws.cell(row=total_row, column=1).border = border

    total_production = sum(r[1] for r in monthly_data)  # = 3.85
    ws.cell(row=total_row, column=2, value=round(total_production, 2)).font = Font(bold=True)
    ws.cell(row=total_row, column=2).fill = total_fill
    ws.cell(row=total_row, column=2).number_format = "0.00"
    ws.cell(row=total_row, column=2).border = border

    total_ob = sum(r[2] for r in monthly_data)
    ws.cell(row=total_row, column=3, value=round(total_ob, 2)).font = Font(bold=True)
    ws.cell(row=total_row, column=3).fill = total_fill
    ws.cell(row=total_row, column=3).border = border

    total_hrs = sum(r[3] for r in monthly_data)
    ws.cell(row=total_row, column=4, value=total_hrs).font = Font(bold=True)
    ws.cell(row=total_row, column=4).fill = total_fill
    ws.cell(row=total_row, column=4).border = border

    ws.cell(row=total_row, column=5, value="Annual Total").fill = total_fill
    ws.cell(row=total_row, column=5).border = border

    # Column widths
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 16
    ws.column_dimensions["E"].width = 38

    # Note row
    note_row = total_row + 2
    ws.merge_cells(f"A{note_row}:E{note_row}")
    ws.cell(row=note_row, column=1, value=(
        f"NOTE: Annual total = {round(total_production, 2)} MT. "
        "All figures are provisional and subject to audit verification."
    ))
    ws.cell(row=note_row, column=1).font = Font(italic=True, size=9, color="666666")

    # Equipment log sheet
    ws2 = wb.create_sheet("Equipment_Log")
    ws2["A1"] = "Equipment Utilization Log — Kranti OCP FY 2023-24"
    ws2["A1"].font = Font(bold=True, size=12)
    eq_headers = ["Equipment ID", "Type", "Make/Model", "Hours Operated", "Breakdowns", "Availability %"]
    for col, h in enumerate(eq_headers, 1):
        cell = ws2.cell(row=3, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = blue_fill
        cell.border = border
    equipment = [
        ("HE-01", "Hydraulic Excavator", "Caterpillar 390F", 7820, 12, "94.2%"),
        ("HE-02", "Hydraulic Excavator", "Komatsu PC2000", 7650, 15, "92.5%"),
        ("DT-01", "Dump Truck", "Komatsu HD785", 8100, 8, "96.1%"),
        ("DT-02", "Dump Truck", "Komatsu HD785", 7980, 11, "94.8%"),
        ("DT-03", "Dump Truck", "Caterpillar 777E", 7560, 18, "91.3%"),
        ("BS-01", "Surface Drill", "Atlas Copco D65", 6240, 5, "97.8%"),
        ("DZ-01", "Dozer", "Komatsu D375A", 6890, 9, "95.4%"),
    ]
    for i, row in enumerate(equipment):
        for j, val in enumerate(row):
            ws2.cell(row=i + 4, column=j + 1, value=val).border = border
    for col in range(1, 7):
        ws2.column_dimensions[get_column_letter(col)].width = 20

    path = os.path.join(OUT_DIR, "DocC_Monthly_Production_Log_FY2023-24.xlsx")
    wb.save(path)
    print(f"  ✓ {os.path.basename(path)}")


def make_pdf_environmental():
    """DocD — Environmental Compliance Report FY2023-24. Water discharge field is illegible."""
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm

    path = os.path.join(OUT_DIR, "DocD_Environmental_Compliance_Report_FY2023-24.pdf")
    c = rl_canvas.Canvas(path, pagesize=A4)
    w, h = A4

    def section_title(text, y):
        c.setFont("Helvetica-Bold", 12)
        c.setFillColorRGB(0.12, 0.25, 0.49)
        c.drawString(2 * cm, y, text)
        c.setStrokeColorRGB(0.12, 0.25, 0.49)
        c.line(2 * cm, y - 3, w - 2 * cm, y - 3)
        return y - 18

    def body_text(text, y, indent=0, bold=False):
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 9)
        c.setFillColorRGB(0, 0, 0)
        # wrap text manually
        max_width = w - (4 + indent * 2) * cm
        words = text.split()
        line = ""
        for word in words:
            test = line + " " + word if line else word
            if c.stringWidth(test, "Helvetica", 9) < max_width:
                line = test
            else:
                c.drawString((2 + indent) * cm, y, line)
                y -= 13
                line = word
        if line:
            c.drawString((2 + indent) * cm, y, line)
            y -= 13
        return y - 3

    # Header
    c.setFillColorRGB(0.12, 0.25, 0.49)
    c.rect(0, h - 3.5 * cm, w, 3.5 * cm, fill=True, stroke=False)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w / 2, h - 1.6 * cm, "ENVIRONMENTAL COMPLIANCE REPORT")
    c.setFont("Helvetica", 11)
    c.drawCentredString(w / 2, h - 2.3 * cm, "Kranti Opencast Project (OCP) — FY 2023-24")
    c.setFont("Helvetica", 9)
    c.drawCentredString(w / 2, h - 3.0 * cm, "Eastern Coalfields Limited (ECL) | Report Date: March 31, 2024")

    y = h - 4.2 * cm

    # Identification block
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.rect(2 * cm, y - 1.6 * cm, w - 4 * cm, 1.6 * cm, fill=True, stroke=False)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    c.drawString(2.3 * cm, y - 0.5 * cm, "EC No.: J-11015/77/2004-IA.II(M)")
    c.drawString(2.3 * cm, y - 1.1 * cm, "Monitoring Period: April 2023 — March 2024")
    c.drawString(w / 2, y - 0.5 * cm, "Compliance Status: Partial Compliance")
    c.drawString(w / 2, y - 1.1 * cm, "Report Ref: ECL/KRA/ENV/2024/03")
    y -= 2.0 * cm

    # Section 1 — Air Quality
    y = section_title("1. Air Quality Monitoring", y)
    y = body_text("Ambient air quality monitoring was conducted at 4 stations around the mine periphery.", y)
    params = [
        ("Parameter", "Unit", "Observed Value", "Permissible Limit", "Status"),
        ("Dust Concentration (RPM)", "mg/m³", "85", "150", "Compliant"),
        ("SPM (Suspended Particulate Matter)", "µg/m³", "120", "200", "Compliant"),
        ("SO₂", "µg/m³", "18", "80", "Compliant"),
        ("NOx", "µg/m³", "35", "80", "Compliant"),
        ("Air Quality Index (AQI)", "—", "78 (Moderate)", "< 100 (Satisfactory)", "Compliant"),
    ]
    col_x = [2 * cm, 6.5 * cm, 10.5 * cm, 14 * cm, 17.5 * cm]
    col_w = [4.2, 3.8, 3.3, 3.3, 2.5]
    for row_idx, row in enumerate(params):
        if y < 3 * cm:
            c.showPage()
            y = h - 2 * cm
        fill_color = (0.87, 0.93, 1.0) if row_idx == 0 else ((1, 1, 1) if row_idx % 2 else (0.97, 0.97, 0.97))
        c.setFillColorRGB(*fill_color)
        c.rect(2 * cm, y - 0.45 * cm, w - 4 * cm, 0.5 * cm, fill=True, stroke=False)
        c.setFillColorRGB(0, 0, 0)
        for xi, val in zip(col_x, row):
            c.setFont("Helvetica-Bold" if row_idx == 0 else "Helvetica", 8)
            c.drawString(xi + 0.1 * cm, y - 0.35 * cm, str(val))
        y -= 0.52 * cm
    y -= 0.3 * cm

    # Section 2 — Water Quality
    y = section_title("2. Water Quality Monitoring", y)
    y = body_text("Water quality monitoring was conducted at mine discharge points and nearby water bodies.", y)

    # Normal parameters
    water_params = [
        ("pH", "—", "7.2", "6.5 – 8.5", "Compliant"),
        ("Total Dissolved Solids (TDS)", "mg/L", "450", "2000", "Compliant"),
        ("Total Suspended Solids (TSS)", "mg/L", "68", "100", "Compliant"),
        ("Iron (Fe)", "mg/L", "0.42", "3.0", "Compliant"),
    ]
    for row_idx, row in enumerate(water_params):
        fill_color = (1, 1, 1) if row_idx % 2 else (0.97, 0.97, 0.97)
        c.setFillColorRGB(*fill_color)
        c.rect(2 * cm, y - 0.45 * cm, w - 4 * cm, 0.5 * cm, fill=True, stroke=False)
        c.setFillColorRGB(0, 0, 0)
        for xi, val in zip(col_x, row):
            c.setFont("Helvetica", 8)
            c.drawString(xi + 0.1 * cm, y - 0.35 * cm, str(val))
        y -= 0.52 * cm

    # ILLEGIBLE FIELD — Water Discharge
    y -= 0.2 * cm
    c.setFillColorRGB(1.0, 0.95, 0.88)
    c.rect(2 * cm, y - 0.9 * cm, w - 4 * cm, 0.95 * cm, fill=True, stroke=True)
    c.setFillColorRGB(0.6, 0.0, 0.0)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2.2 * cm, y - 0.35 * cm, "Water Discharge Volume (MLD):")
    # Simulate illegible/smeared ink
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(9 * cm, y - 0.35 * cm,
                 "???.?? MLD   [ILLEGIBLE — ink smear on original scanned document]")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.7, 0.3, 0.0)
    c.drawString(2.2 * cm, y - 0.72 * cm,
                 "⚠ This field could not be read from the original hardcopy. Manual verification required.")
    y -= 1.2 * cm

    # Section 3 — Plantation
    y = section_title("3. Plantation & Green Cover", y)
    y = body_text("Green belt development status as on March 31, 2024:", y)
    y = body_text("• Total plantation area: 48.2 hectares (target: 50 ha)", y, indent=0.5)
    y = body_text("• Number of saplings planted (cumulative): 12,450", y, indent=0.5)
    y = body_text("• Species: Eucalyptus (40%), Acacia (30%), Bamboo (20%), Local species (10%)", y, indent=0.5)
    y = body_text("• Survival rate: 78%", y, indent=0.5)
    y -= 0.3 * cm

    # Section 4 — Overall Compliance
    y = section_title("4. Overall Compliance Status", y)
    c.setFillColorRGB(1.0, 0.97, 0.88)
    c.rect(2 * cm, y - 1.3 * cm, w - 4 * cm, 1.3 * cm, fill=True, stroke=True)
    c.setFillColorRGB(0.5, 0.3, 0.0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2.3 * cm, y - 0.5 * cm, "PARTIAL COMPLIANCE")
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(2.3 * cm, y - 1.0 * cm,
                 "Non-conformance: Water discharge volume record unavailable (illegible source document).")
    y -= 1.8 * cm

    # Signature block
    y = max(y, 4 * cm)
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, y, "Prepared by:")
    c.drawString(2 * cm, y - 0.5 * cm, "Environmental Officer, Kranti OCP")
    c.drawString(2 * cm, y - 1.0 * cm, "Date: March 31, 2024")
    c.drawString(12 * cm, y, "Approved by:")
    c.drawString(12 * cm, y - 0.5 * cm, "General Manager (Environment), ECL")
    c.drawString(12 * cm, y - 1.0 * cm, "Date: April 5, 2024")

    # Footer
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(w / 2, 1.5 * cm,
                        "CONFIDENTIAL — Eastern Coalfields Limited. Not for public distribution.")
    c.drawCentredString(w / 2, 1.0 * cm, "Page 1 of 1")

    c.save()
    print(f"  ✓ {os.path.basename(path)}")


def make_docx_archived_reserve():
    """DocE — Archived Reserve Estimate 2019. Coal Grade=G7 (conflicts with G8 in DocA/DocB)."""
    from docx import Document
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    title = doc.add_heading("RESERVE ESTIMATION REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph("KRANTI COLLIERY — HISTORICAL BASELINE RECORD")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].bold = True
    sub.runs[0].font.size = Pt(12)

    doc.add_paragraph()

    table = doc.add_table(rows=7, cols=2)
    table.style = "Table Grid"
    rows_data = [
        ("Mine Name", "Kranti Colliery (Now: Kranti OCP)"),
        ("Company", "Eastern Coalfields Limited (ECL)"),
        ("Location", "Raniganj Coalfield, Burdwan, West Bengal"),
        ("Report Date", "September 15, 2019"),
        ("Coal Grade", "G7"),
        ("Estimation Method", "Cross-Sectional Method"),
        ("Document Status", "ARCHIVED — Historical Reference Only"),
    ]
    for i, (k, v) in enumerate(rows_data):
        table.rows[i].cells[0].text = k
        table.rows[i].cells[1].text = v
        table.rows[i].cells[0].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    doc.add_heading("Preamble", 1)
    doc.add_paragraph(
        "This report constitutes the baseline geological reserve estimation for the Kranti Colliery, conducted "
        "during the pre-expansion feasibility study of 2018-19. At the time of this assessment, the mine "
        "operated partially as an underground mine with opencast operations limited to the western block. "
        "This document is maintained as a historical reference and does not reflect current reserve positions."
    )
    doc.add_paragraph(
        "Coal sampling and grade analysis were conducted by CMPDI Ranchi and Dhanbad Regional Institute. "
        "The coal was classified as Grade G7 under the then-prevailing BIS classification norms. "
        "Subsequent reclassification exercises by CMPDI (if any) are not reflected in this archived document."
    )
    doc.add_paragraph(
        "Reserve estimates were computed using the Cross-Sectional Method based on 64 exploratory boreholes "
        "drilled between 2014 and 2018. The total estimated reserve stood at 156.2 Million Tonnes as on "
        "April 1, 2019, prior to commencement of full-scale opencast production."
    )

    doc.add_heading("Seam-wise Reserve Summary (As on April 1, 2019)", 1)
    rtable = doc.add_table(rows=6, cols=4)
    rtable.style = "Table Grid"
    headers = ["Seam", "Category", "Grade", "Reserve (MT)"]
    for j, h in enumerate(headers):
        rtable.rows[0].cells[j].text = h
        rtable.rows[0].cells[j].paragraphs[0].runs[0].bold = True
    data = [
        ("Seam-II", "Indicated (Cat B)", "G7", "52.4"),
        ("Seam-III", "Indicated (Cat B)", "G7", "58.1"),
        ("Seam-IV", "Inferred (Cat C)", "G7", "45.7"),
        ("Seam-V", "Inferred (Cat C)", "G7", "— (Not quantified)"),
        ("TOTAL", "—", "G7", "156.2"),
    ]
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            rtable.rows[i + 1].cells[j].text = val

    doc.add_paragraph()
    doc.add_heading("Notes and Limitations", 1)
    doc.add_paragraph(
        "1. This document was prepared under the 2019 IBM Reserve Estimation Guidelines.\n"
        "2. Coal grade G7 is as per BIS IS 770 (2004 version) classification.\n"
        "3. Reserve figures are pre-mining; actual mineable reserves will be lower after depletion.\n"
        "4. This archived document should NOT be used for current production planning or regulatory submissions."
    )

    path = os.path.join(OUT_DIR, "DocE_Archived_Reserve_Estimate_2019.docx")
    doc.save(path)
    print(f"  ✓ {os.path.basename(path)}")


def make_correspondence(filename, from_office, to_office, date_str, subject, status, body_paragraphs):
    """Generic helper to create a correspondence DOCX."""
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Letterhead
    lh = doc.add_paragraph()
    lh.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = lh.add_run("GOVERNMENT OF INDIA / EASTERN COALFIELDS LIMITED")
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x1F, 0x39, 0x64)

    doc.add_paragraph()

    # Ref block
    meta = doc.add_table(rows=4, cols=2)
    meta.style = "Table Grid"
    meta.rows[0].cells[0].text = "FROM"
    meta.rows[0].cells[1].text = from_office
    meta.rows[1].cells[0].text = "TO"
    meta.rows[1].cells[1].text = to_office
    meta.rows[2].cells[0].text = "DATE"
    meta.rows[2].cells[1].text = date_str
    meta.rows[3].cells[0].text = "STATUS"
    meta.rows[3].cells[1].text = status.upper()
    for row in meta.rows:
        row.cells[0].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    subj_para = doc.add_paragraph()
    subj_para.add_run("SUBJECT: ").bold = True
    subj_para.add_run(subject)

    doc.add_paragraph()
    doc.add_paragraph("Sir/Madam,")
    doc.add_paragraph()

    for para in body_paragraphs:
        doc.add_paragraph(para)

    doc.add_paragraph()
    doc.add_paragraph("Yours faithfully,")
    doc.add_paragraph()
    doc.add_paragraph("(Authorised Signatory)")
    doc.add_paragraph(from_office)
    doc.add_paragraph(f"Date: {date_str}")

    path = os.path.join(OUT_DIR, filename)
    doc.save(path)
    print(f"  ✓ {os.path.basename(path)}")


def main():
    print("\n🗂️  DocuMine Seed Data Generator")
    print("=" * 50)
    print(f"Output directory: {OUT_DIR}\n")

    print("Generating mining documents...")

    make_docx_geological_a()
    make_docx_geological_b()
    make_xlsx_production_log()
    make_pdf_environmental()
    make_docx_archived_reserve()

    print("\nGenerating clearance correspondence documents...")

    make_correspondence(
        "CL1_Village_Panchayat_NOC.docx",
        from_office="Gram Panchayat, Karanpur Village, Paschim Bardhaman",
        to_office="District Collector, Paschim Bardhaman",
        date_str="January 5, 2024",
        subject="No Objection Certificate for Land Acquisition — Kranti OCP Expansion Phase II",
        status="resolved",
        body_paragraphs=[
            "This is to certify that the Gram Sabha of Karanpur Village held a special meeting on "
            "December 28, 2023, duly attended by 312 registered voters (quorum 60%), to deliberate "
            "upon the proposal for land acquisition by Eastern Coalfields Limited for Phase II expansion "
            "of Kranti Opencast Project.",
            "After due deliberation and in consideration of the assurances given by ECL management "
            "regarding: (a) priority employment for 85 displaced households, (b) compensation at 4x "
            "the circle rate, and (c) construction of a community skill-development centre, the "
            "Gram Sabha has resolved to grant its No Objection Certificate for the said land acquisition "
            "covering 38.4 hectares in Survey Numbers 141/A through 148/C.",
            "This NOC is issued subject to strict adherence to the Rehabilitation & Resettlement plan "
            "filed with the District Collector's office. Any deviation shall render this NOC void.",
        ],
    )

    make_correspondence(
        "CL2_District_Collector_Forwarding.docx",
        from_office="Office of the District Collector, Paschim Bardhaman, Government of West Bengal",
        to_office="Principal Secretary, State Revenue Department, Government of West Bengal",
        date_str="January 18, 2024",
        subject="Forwarding of Village Panchayat NOC — Kranti OCP Phase II Land Acquisition",
        status="resolved",
        body_paragraphs=[
            "Please refer to the No Objection Certificate dated January 5, 2024 issued by the Gram "
            "Panchayat of Karanpur Village (Reference: GP/KRN/NOC/2024/01) in respect of land "
            "acquisition by Eastern Coalfields Limited for the Kranti Opencast Project Phase II expansion.",
            "The same is forwarded herewith for necessary action by the State Revenue Department under "
            "Section 4 of the Right to Fair Compensation and Transparency in Land Acquisition, "
            "Rehabilitation and Resettlement Act, 2013. The District Administration confirms that the "
            "Gram Sabha proceedings were conducted in accordance with prescribed procedure.",
        ],
    )

    make_correspondence(
        "CL3_State_Revenue_Dept_Query.docx",
        from_office="State Revenue Department, Government of West Bengal, Nabanna, Howrah",
        to_office="Director (Projects), Eastern Coalfields Limited, Sanctoria",
        date_str="February 12, 2024",
        subject="Query Regarding Land Compensation Assessment — Kranti OCP Phase II Expansion",
        status="resolved",
        body_paragraphs=[
            "This office has received the land acquisition proposal forwarded by the District Collector, "
            "Paschim Bardhaman (Ref: DC/PB/LA/2024/07 dated January 18, 2024) in connection with the "
            "Kranti OCP Phase II expansion.",
            "Before proceeding with the acquisition notification, this department requires the following "
            "clarifications from ECL: (i) Basis for compensation calculation — whether circle rate or "
            "market value methodology has been adopted; (ii) Displacement census data for affected "
            "households with Aadhaar-linked verification; (iii) Timeline for R&R implementation. "
            "Please submit a detailed response within 30 days of receipt of this communication.",
        ],
    )

    make_correspondence(
        "CL4_MoEFCC_Forest_Clearance_Request.docx",
        from_office="Eastern Coalfields Limited (ECL), Ministry of Coal, Government of India",
        to_office="Additional Director General (Forests), MoEFCC, New Delhi",
        date_str="March 1, 2024",
        subject="Application for Forest Clearance under Forest (Conservation) Act, 1980 — Kranti OCP Phase II Expansion",
        status="pending",
        body_paragraphs=[
            "Eastern Coalfields Limited (ECL) hereby submits this application for Stage I Forest Clearance "
            "under Section 2 of the Forest (Conservation) Act, 1980, for diversion of 28.5 hectares of "
            "Reserved Forest land (Karanpur Reserve Forest, Block-IV) required for Phase II expansion of "
            "Kranti Opencast Project, Raniganj Coalfield, West Bengal.",
            "The proposed forest land diversion is essential for development of the haul road corridor "
            "(12.8 ha), overburden dump expansion (10.2 ha), and infrastructure facilities (5.5 ha). "
            "The project has valid Environmental Clearance (EC No. J-11015/77/2004-IA.II(M)) and "
            "State Government recommendation vide letter No. FD/WB/FC/2023/456 dated November 22, 2023.",
            "Compensatory Afforestation: ECL proposes to carry out compensatory afforestation over 57.0 "
            "hectares (2x the diverted area) in degraded forest areas identified by the West Bengal "
            "Forest Department. CA funds of Rs. 4.82 Crore have been deposited with CAMPA.",
            "Required attachments (enclosed): (1) Survey & demarcation map, (2) Working plan extract, "
            "(3) Certificate of non-availability of non-forest land, (4) District Collector's "
            "recommendation, (5) State Government's recommendation, (6) CA plan and cost estimate.",
        ],
    )

    make_correspondence(
        "CL5_MoEFCC_Response_Pending.docx",
        from_office="MoEFCC Regional Office, Bhubaneswar (Internal Tracking Note — ECL Project Team)",
        to_office="Director (Projects), Eastern Coalfields Limited, Sanctoria [INTERNAL]",
        date_str="March 5, 2024",
        subject=(
            "PENDING: Forest Clearance Application — Kranti OCP Phase II (No Response from MoEFCC "
            "as of September 30, 2026)"
        ),
        status="pending",
        body_paragraphs=[
            "INTERNAL TRACKING NOTE — This document records the status of ECL's Forest Clearance "
            "application (Ref: ECL/FC/KROCP/2024/01 dated March 1, 2024) submitted to MoEFCC "
            "for Kranti OCP Phase II expansion.",
            "As of September 30, 2026, the Ministry of Environment, Forest and Climate Change (MoEFCC) "
            "has NOT responded to the above application. The application has been pending for 579 days "
            "with no Stage-I clearance communication, no acknowledgement of deficiency, and no "
            "request for additional information received from MoEFCC.",
            "Follow-up communications sent by ECL on: March 5, 2024 (acknowledgement request); "
            "June 15, 2024 (reminder); November 8, 2024 (escalation to ADG level); "
            "March 20, 2025 (reminder to Regional Office, Bhubaneswar). No response received to any.",
            "STATUS: BOTTLENECK — This is the critical path item blocking Phase II expansion. "
            "Days pending as on September 30, 2026: 579 days. Escalation to Secretary (Forests), "
            "MoEFCC is recommended immediately.",
        ],
    )

    print("\n" + "=" * 50)
    print("✅ All seed documents generated successfully!")
    print(f"   Location: {OUT_DIR}")
    print("   Files created:")
    for f in sorted(os.listdir(OUT_DIR)):
        if f != os.path.basename(__file__):
            size = os.path.getsize(os.path.join(OUT_DIR, f))
            print(f"   • {f} ({size:,} bytes)")


if __name__ == "__main__":
    main()


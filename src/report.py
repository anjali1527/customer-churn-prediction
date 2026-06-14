import io
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
)

from retention import retention_strategy

# ── Palette ───────────────────────────────────────────────────────────────────
C_BLACK    = colors.HexColor("#060608")
C_950      = colors.HexColor("#0c0c0f")
C_900      = colors.HexColor("#111115")
C_800      = colors.HexColor("#1c1c22")
C_700      = colors.HexColor("#26262e")
C_500      = colors.HexColor("#4a4a58")
C_300      = colors.HexColor("#9898aa")
C_100      = colors.HexColor("#e8e8f0")
C_WHITE    = colors.HexColor("#f0f0f8")
C_RED      = colors.HexColor("#dc2626")
C_RED_DARK = colors.HexColor("#7f1d1d")
C_RED_LITE = colors.HexColor("#f87171")
C_AMBER    = colors.HexColor("#d97706")
C_GREEN    = colors.HexColor("#059669")

W, H = A4  # 595 x 842 pts

# ── Page decorator ────────────────────────────────────────────────────────────
def _draw_page(canvas, doc):
    canvas.saveState()

    # Background
    canvas.setFillColor(C_BLACK)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)

    # Header band
    canvas.setFillColor(C_950)
    canvas.rect(0, H - 48 * mm, W, 48 * mm, fill=1, stroke=0)

    # Red separator line
    canvas.setStrokeColor(C_RED)
    canvas.setLineWidth(1.0)
    canvas.line(0, H - 48 * mm, W, H - 48 * mm)

    # Left red stripe
    canvas.setFillColor(C_RED)
    canvas.rect(0, 0, 3.5, H, fill=1, stroke=0)

    # Logo wordmark
    canvas.setFillColor(C_WHITE)
    canvas.setFont("Helvetica-Bold", 17)
    canvas.drawString(13 * mm, H - 17 * mm, "NEXUS")

    canvas.setFillColor(C_RED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(13 * mm, H - 24 * mm, "RETENTION INTELLIGENCE PLATFORM")

    # Page meta (right)
    canvas.setFillColor(C_500)
    canvas.setFont("Helvetica", 6.5)
    ts = datetime.now().strftime("%d %b %Y  %H:%M UTC")
    canvas.drawRightString(W - 13 * mm, H - 17 * mm, f"Generated: {ts}")
    canvas.drawRightString(W - 13 * mm, H - 24 * mm, f"Page {doc.page}")

    # Horizontal rule under sub-header text
    canvas.setStrokeColor(C_700)
    canvas.setLineWidth(0.4)
    canvas.line(13 * mm, H - 30 * mm, W - 13 * mm, H - 30 * mm)

    # Footer
    canvas.setStrokeColor(C_800)
    canvas.setLineWidth(0.4)
    canvas.line(13 * mm, 13 * mm, W - 13 * mm, 13 * mm)
    canvas.setFillColor(C_500)
    canvas.setFont("Helvetica", 6)
    canvas.drawString(13 * mm, 8 * mm,
                      "NEXUS · AI Customer Retention Intelligence · Strictly Confidential")
    canvas.drawRightString(W - 13 * mm, 8 * mm, "nexus-retention.io")

    canvas.restoreState()


# ── Styles ────────────────────────────────────────────────────────────────────
def _S():
    def make(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "page_title": make("pt",
            fontName="Helvetica-Bold", fontSize=30, leading=34,
            textColor=C_WHITE, spaceAfter=2, alignment=TA_LEFT),

        "page_title_red": make("ptr",
            fontName="Helvetica-Bold", fontSize=30, leading=34,
            textColor=C_RED, spaceAfter=6, alignment=TA_LEFT),

        "page_sub": make("ps",
            fontName="Helvetica", fontSize=8, leading=12,
            textColor=C_500, spaceAfter=4, letterSpacing=2),

        "section": make("sec",
            fontName="Helvetica-Bold", fontSize=8, leading=11,
            textColor=C_RED_LITE, spaceBefore=10, spaceAfter=2,
            letterSpacing=3),

        "body": make("body",
            fontName="Helvetica", fontSize=8.5, leading=13,
            textColor=C_300, spaceAfter=4),

        "kpi_label": make("kl",
            fontName="Helvetica", fontSize=6.5, leading=9,
            textColor=C_500, alignment=TA_CENTER),

        "kpi_value": make("kv",
            fontName="Helvetica-Bold", fontSize=24, leading=28,
            textColor=C_WHITE, alignment=TA_CENTER),

        "kpi_sub": make("ks",
            fontName="Helvetica", fontSize=6.5, leading=9,
            textColor=C_RED_LITE, alignment=TA_CENTER),

        "th": make("th",
            fontName="Helvetica-Bold", fontSize=6.5, leading=9,
            textColor=C_300, alignment=TA_LEFT),

        "th_c": make("thc",
            fontName="Helvetica-Bold", fontSize=6.5, leading=9,
            textColor=C_300, alignment=TA_CENTER),

        "td": make("td",
            fontName="Helvetica", fontSize=7.5, leading=10,
            textColor=C_300, alignment=TA_LEFT),

        "td_c": make("tdc",
            fontName="Helvetica", fontSize=7.5, leading=10,
            textColor=C_300, alignment=TA_CENTER),

        "risk_h": make("rh",
            fontName="Helvetica-Bold", fontSize=7.5, leading=10,
            textColor=C_RED_LITE, alignment=TA_CENTER),

        "risk_m": make("rm",
            fontName="Helvetica-Bold", fontSize=7.5, leading=10,
            textColor=C_AMBER, alignment=TA_CENTER),

        "risk_l": make("rl",
            fontName="Helvetica-Bold", fontSize=7.5, leading=10,
            textColor=C_GREEN, alignment=TA_CENTER),

        "ret_title": make("rtt",
            fontName="Helvetica-Bold", fontSize=8, leading=11,
            textColor=C_RED_LITE, spaceAfter=2),

        "ret_tip": make("rtp",
            fontName="Helvetica", fontSize=7.5, leading=12,
            textColor=C_300, leftIndent=8, spaceAfter=3),

        "insight": make("ins",
            fontName="Helvetica", fontSize=8, leading=13,
            textColor=C_300, leftIndent=6, spaceAfter=2),

        "caption": make("cap",
            fontName="Helvetica", fontSize=6, leading=8,
            textColor=C_500, alignment=TA_CENTER),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def _red_rule():
    return HRFlowable(width="100%", thickness=0.8, color=C_RED,
                      spaceAfter=5, spaceBefore=1)

def _grey_rule():
    return HRFlowable(width="100%", thickness=0.3, color=C_700,
                      spaceAfter=3, spaceBefore=1)

def _section(label, S):
    return [Paragraph(label.upper(), S["section"]), _red_rule()]

def _base_table_style():
    return TableStyle([
        ("BACKGROUND",     (0, 0), (-1,  0), C_800),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_950, C_900]),
        ("BOX",            (0, 0), (-1, -1), 0.4, C_700),
        ("INNERGRID",      (0, 0), (-1, -1), 0.25, C_800),
        ("TOPPADDING",     (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 6),
        ("LEFTPADDING",    (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 7),
        ("LINEABOVE",      (0, 0), (-1,  0), 1.5, C_RED),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ])

def _risk_style(level, S):
    return {"High Risk": S["risk_h"], "Medium Risk": S["risk_m"],
            "Low Risk": S["risk_l"]}.get(level, S["td_c"])

def _kpi_row(items, S, page_width):
    n = len(items)
    cw = page_width / n
    rows = [
        [Paragraph(lbl, S["kpi_label"])  for lbl, _, _ in items],
        [Paragraph(val, S["kpi_value"])  for _, val, _ in items],
        [Paragraph(sub, S["kpi_sub"])    for _, _, sub in items],
    ]
    tbl = Table(rows, colWidths=[cw] * n, rowHeights=[12, 28, 11])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, -1), C_950),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_950, C_900, C_950]),
        ("BOX",            (0, 0), (-1, -1), 0.4, C_700),
        ("INNERGRID",      (0, 0), (-1, -1), 0.25, C_800),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("LINEABOVE",      (0, 0), (-1,  0), 1.5, C_RED),
    ]))
    return tbl

def _inline_bar(value, max_val, color, bar_max_pts=130):
    """Inline filled rectangle as a bar cell."""
    w = int((value / max_val) * bar_max_pts) if max_val > 0 else 1
    w = max(w, 2)
    t = Table([[""]], colWidths=[w], rowHeights=[7])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), color),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
def generate_pdf(df: pd.DataFrame) -> bytes:
    """
    Generate a full professional dark-themed PDF report.

    Parameters
    ----------
    df : DataFrame that must contain columns:
         Prediction, Probability, RiskLevel
         (all other columns treated as customer features)

    Returns
    -------
    bytes : Raw PDF bytes — pass to st.download_button(data=...)
    """
    buf = io.BytesIO()
    S   = _S()
    PW  = W - 26 * mm   # usable page width

    # ── Document ──────────────────────────────────────────────────────────────
    frame = Frame(
        13 * mm, 20 * mm,
        PW, H - 20 * mm - 52 * mm,
        leftPadding=0, rightPadding=0,
        topPadding=0, bottomPadding=0,
    )
    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=13 * mm, rightMargin=13 * mm,
        topMargin=52 * mm, bottomMargin=20 * mm,
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_draw_page)])

    story = []

    # ── Metrics ───────────────────────────────────────────────────────────────
    total      = len(df)
    churn_rate = df["Prediction"].mean() if "Prediction" in df.columns else 0
    avg_prob   = df["Probability"].mean() if "Probability" in df.columns else 0
    high_n     = len(df[df["RiskLevel"] == "High Risk"])   if "RiskLevel" in df.columns else 0
    med_n      = len(df[df["RiskLevel"] == "Medium Risk"]) if "RiskLevel" in df.columns else 0
    low_n      = len(df[df["RiskLevel"] == "Low Risk"])    if "RiskLevel" in df.columns else 0

    # ── Cover ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("AI CUSTOMER", S["page_title"]))
    story.append(Paragraph("RETENTION REPORT", S["page_title_red"]))
    story.append(Paragraph(
        f"GENERATED  ·  {datetime.now().strftime('%d %B %Y').upper()}  ·  CONFIDENTIAL",
        S["page_sub"]))
    story.append(Spacer(1, 3 * mm))
    story.append(_red_rule())
    story.append(Spacer(1, 4 * mm))

    # ── KPI Row ───────────────────────────────────────────────────────────────
    story += _section("Executive Summary", S)
    story.append(_kpi_row([
        ("Total Customers", f"{total:,}",         "Scored"),
        ("Churn Rate",      f"{churn_rate:.1%}",  "Predicted"),
        ("High Risk",       f"{high_n:,}",         "Customers"),
        ("Avg Probability", f"{avg_prob:.2f}",     "Score"),
    ], S, PW))
    story.append(Spacer(1, 5 * mm))

    # ── Risk Distribution ─────────────────────────────────────────────────────
    story += _section("Risk Distribution", S)
    risk_rows = [[
        Paragraph("RISK LEVEL", S["th"]),
        Paragraph("COUNT",      S["th_c"]),
        Paragraph("SHARE",      S["th_c"]),
        Paragraph("DISTRIBUTION", S["th_c"]),
    ]]
    for label, count, color in [
        ("High Risk",   high_n, C_RED),
        ("Medium Risk", med_n,  C_AMBER),
        ("Low Risk",    low_n,  C_GREEN),
    ]:
        pct = count / total if total > 0 else 0
        risk_rows.append([
            Paragraph(label, _risk_style(label, S)),
            Paragraph(f"{count:,}", S["td_c"]),
            Paragraph(f"{pct:.1%}",  S["td_c"]),
            _inline_bar(count, max(high_n, med_n, low_n, 1), color, bar_max_pts=int(PW * 0.40)),
        ])
    rt = Table(risk_rows, colWidths=[PW*0.24, PW*0.13, PW*0.13, PW*0.50])
    rt.setStyle(_base_table_style())
    story.append(rt)
    story.append(Spacer(1, 5 * mm))

    # ── Probability Decile ────────────────────────────────────────────────────
    if "Probability" in df.columns:
        story += _section("Probability Decile Breakdown", S)
        bins   = [i * 0.1 for i in range(11)]
        labels = [f"{int(b*100)}–{int(b*100)+10}%" for b in bins[:-1]]
        counts = pd.cut(df["Probability"], bins=bins, labels=labels,
                        include_lowest=True).value_counts().sort_index()
        max_c  = counts.max() if counts.max() > 0 else 1

        dec_rows = [[
            Paragraph("DECILE",        S["th"]),
            Paragraph("COUNT",         S["th_c"]),
            Paragraph("SHARE",         S["th_c"]),
            Paragraph("BAR",           S["th_c"]),
        ]]
        for lbl, cnt in counts.items():
            dec_rows.append([
                Paragraph(str(lbl),             S["td"]),
                Paragraph(f"{cnt:,}",           S["td_c"]),
                Paragraph(f"{cnt/total:.1%}" if total else "0%", S["td_c"]),
                _inline_bar(cnt, max_c, C_RED_DARK, bar_max_pts=int(PW * 0.45)),
            ])
        dt = Table(dec_rows, colWidths=[PW*0.20, PW*0.13, PW*0.12, PW*0.55])
        dt.setStyle(_base_table_style())
        story.append(dt)
        story.append(Spacer(1, 5 * mm))

    # ── Feature Statistics ────────────────────────────────────────────────────
    feat_cols = [
        c for c in df.columns
        if c not in ("Prediction", "Probability", "RiskLevel")
        and pd.api.types.is_numeric_dtype(df[c])
    ]
    if feat_cols:
        story += _section("Feature Statistics", S)
        fh = [
            Paragraph("FEATURE",  S["th"]),
            Paragraph("MIN",      S["th_c"]),
            Paragraph("MEAN",     S["th_c"]),
            Paragraph("MAX",      S["th_c"]),
            Paragraph("STD",      S["th_c"]),
        ]
        frows = [fh]
        for fc in feat_cols[:15]:
            col = pd.to_numeric(df[fc], errors="coerce").dropna()
            if col.empty: continue
            frows.append([
                Paragraph(fc[:26], S["td"]),
                Paragraph(f"{col.min():.2f}",  S["td_c"]),
                Paragraph(f"{col.mean():.2f}", S["td_c"]),
                Paragraph(f"{col.max():.2f}",  S["td_c"]),
                Paragraph(f"{col.std():.2f}",  S["td_c"]),
            ])
        ft = Table(frows, colWidths=[PW*0.34, PW*0.165, PW*0.165, PW*0.165, PW*0.165])
        ft.setStyle(_base_table_style())
        story.append(ft)
        story.append(Spacer(1, 5 * mm))

    if "RiskLevel" in df.columns:
        hr_df = df[df["RiskLevel"] == "High Risk"].copy()
        if not hr_df.empty:
            story += _section("Top High-Risk Customers", S)
            display_cols = (
                ["Probability", "RiskLevel"]
                + [c for c in hr_df.columns
                   if c not in ("Prediction", "Probability", "RiskLevel")
                   and len(str(c)) <= 22][:5]
            )
            sample = hr_df.sort_values("Probability", ascending=False).head(10)
            head   = [Paragraph(c.upper()[:14], S["th_c"]) for c in display_cols]
            rows   = [head]
            for _, row in sample.iterrows():
                r = []
                for c in display_cols:
                    val = row[c]
                    if c == "RiskLevel":
                        r.append(Paragraph(str(val), _risk_style(str(val), S)))
                    elif c == "Probability":
                        r.append(Paragraph(f"{float(val):.1%}", S["risk_h"]))
                    elif isinstance(val, float):
                        r.append(Paragraph(f"{val:.2f}", S["td_c"]))
                    else:
                        r.append(Paragraph(str(val)[:18], S["td_c"]))
                rows.append(r)
            cw = PW / len(display_cols)
            ht = Table(rows, colWidths=[cw] * len(display_cols))
            ht.setStyle(_base_table_style())
            story.append(ht)
            story.append(Spacer(1, 5 * mm))

    
    story += _section("Automated AI Insights", S)
    insights = []

    if churn_rate > 0.5:
        insights.append("⚠  CRITICAL: Churn rate exceeds 50% — immediate executive escalation required.")
    elif churn_rate > 0.3:
        insights.append("△  ELEVATED: Churn rate above 30% — targeted retention campaigns should be deployed now.")
    else:
        insights.append("✓  STABLE: Churn rate within acceptable range. Continue proactive monitoring.")

    if high_n / total > 0.4 if total else False:
        insights.append(f"⚠  {high_n/total:.0%} of cohort is High Risk — bulk outreach programme recommended.")
    elif high_n / total > 0.2 if total else False:
        insights.append(f"△  {high_n/total:.0%} high-risk cohort — deploy customer success team within 72 hours.")
    else:
        insights.append(f"✓  High-risk segment at {high_n/total:.0%} — manageable with 1:1 targeted outreach.")

    if avg_prob > 0.6:
        insights.append("⚠  Average churn probability is HIGH — systemic retention weakness detected.")
    elif avg_prob > 0.4:
        insights.append("△  Average probability MODERATE — focus on medium-risk segment to prevent escalation.")
    else:
        insights.append("✓  Average probability HEALTHY — prioritise loyalty programmes for low-risk cohort.")

    ins_data = [[Paragraph(i, S["insight"])] for i in insights]
    it = Table(ins_data, colWidths=[PW])
    it.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, -1), C_950),
        ("BOX",            (0, 0), (-1, -1), 0.4, C_700),
        ("INNERGRID",      (0, 0), (-1, -1), 0.25, C_800),
        ("TOPPADDING",     (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 7),
        ("LEFTPADDING",    (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 10),
        ("LINEABOVE",      (0, 0), (-1,  0), 1.5, C_RED),
    ]))
    story.append(it)
    story.append(Spacer(1, 5 * mm))


    if "RiskLevel" in df.columns:
        hr_df = df[df["RiskLevel"] == "High Risk"].copy()
        if not hr_df.empty:
            story.append(PageBreak())
            story.append(Spacer(1, 4 * mm))
            story.append(Paragraph("RETENTION", S["page_title"]))
            story.append(Paragraph("STRATEGY REPORT", S["page_title_red"]))
            story.append(Paragraph(
                "PERSONALISED ACTIONS · HIGH-RISK CUSTOMERS",
                S["page_sub"]))
            story.append(Spacer(1, 3 * mm))
            story.append(_red_rule())
            story.append(Spacer(1, 4 * mm))

            hr_sorted = hr_df.sort_values("Probability", ascending=False).head(20)

            for idx, (_, row) in enumerate(hr_sorted.iterrows()):
                prob       = row.get("Probability", 0)
                risk_level = row.get("RiskLevel", "High Risk")
                customer   = row.to_dict()
                tips       = retention_strategy(customer, risk_level)

                # Customer header block
                prob_bar_w = int(prob * (PW * 0.55))
                prob_bar   = _inline_bar(prob, 1.0, C_RED, bar_max_pts=int(PW * 0.55))

                header_data = [[
                    Paragraph(f"CUSTOMER {idx + 1:02d}", S["th"]),
                    Paragraph(f"CHURN PROB: {prob:.1%}", S["risk_h"]),
                    Paragraph(f"RISK: {risk_level.upper()}", S["risk_h"]),
                ]]
                ht_hdr = Table(header_data, colWidths=[PW*0.30, PW*0.35, PW*0.35])
                ht_hdr.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, -1), C_800),
                    ("BOX",           (0, 0), (-1, -1), 0.4, C_700),
                    ("LINEABOVE",     (0, 0), (-1,  0), 1.5, C_RED),
                    ("TOPPADDING",    (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
                    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ]))

                # Probability visual bar row
                bar_data = [[Paragraph("PROBABILITY", S["caption"]), prob_bar]]
                bar_tbl  = Table(bar_data, colWidths=[PW*0.12, PW*0.88])
                bar_tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, -1), C_950),
                    ("BOX",           (0, 0), (-1, -1), 0.4, C_700),
                    ("TOPPADDING",    (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
                    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ]))

                # Tips table
                tip_rows = []
                for i, tip in enumerate(tips):
                    tip_rows.append([
                        Paragraph(str(i + 1), S["td_c"]),
                        Paragraph(tip, S["ret_tip"]),
                    ])
                tips_tbl = Table(tip_rows, colWidths=[PW*0.06, PW*0.94])
                tips_tbl.setStyle(TableStyle([
                    ("BACKGROUND",     (0, 0), (-1, -1), C_950),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_950, C_900]),
                    ("BOX",            (0, 0), (-1, -1), 0.4, C_700),
                    ("INNERGRID",      (0, 0), (-1, -1), 0.2, C_800),
                    ("TOPPADDING",     (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING",  (0, 0), (-1, -1), 6),
                    ("LEFTPADDING",    (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
                    ("VALIGN",         (0, 0), (-1, -1), "TOP"),
                    ("TEXTCOLOR",      (0, 0), (0, -1), C_RED_LITE),
                    ("FONTNAME",       (0, 0), (0, -1), "Helvetica-Bold"),
                ]))

                block = KeepTogether([
                    ht_hdr,
                    bar_tbl,
                    tips_tbl,
                    Spacer(1, 6 * mm),
                ])
                story.append(block)

  
    doc.build(story)
    return buf.getvalue()

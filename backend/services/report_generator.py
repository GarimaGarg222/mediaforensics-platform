"""
PDF Forensic Report Generator using ReportLab.
Generates professional reports with scores, heatmaps, and frame data.
"""
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

REPORTS_DIR = "./reports"


def generate_report(job: Dict[str, Any]) -> Optional[str]:
    """
    Generate a PDF forensic report for a completed analysis job.
    Returns the path to the generated PDF, or None on failure.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table,
            TableStyle, HRFlowable, Image as RLImage
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        os.makedirs(REPORTS_DIR, exist_ok=True)

        job_id    = job.get("job_id", "unknown")
        result    = job.get("result", {})
        media     = job.get("media",  {})
        signals   = result.get("signals", {})
        verdict   = result.get("verdict", "unknown")
        score     = result.get("authenticity_score", 0)
        frames    = result.get("frame_results", [])

        output_path = os.path.join(REPORTS_DIR, f"{job_id}.pdf")
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm,   bottomMargin=2*cm,
        )

        styles = getSampleStyleSheet()
        story  = []

        # ── Colors ────────────────────────────────
        GREEN  = colors.HexColor("#1ab87e")
        RED    = colors.HexColor("#f05252")
        AMBER  = colors.HexColor("#f59e0b")
        DARK   = colors.HexColor("#0a0f0d")
        GRAY   = colors.HexColor("#6b7280")
        LIGHT  = colors.HexColor("#f9fafb")

        verdict_color = RED if verdict == "fake" else AMBER if verdict == "suspicious" else GREEN

        # ── Title ─────────────────────────────────
        title_style = ParagraphStyle(
            "Title", parent=styles["Title"],
            fontSize=22, textColor=DARK,
            spaceAfter=4, fontName="Helvetica-Bold",
        )
        sub_style = ParagraphStyle(
            "Sub", parent=styles["Normal"],
            fontSize=10, textColor=GRAY,
            spaceAfter=2,
        )

        story.append(Paragraph("MediaForensics Platform", title_style))
        story.append(Paragraph("AI-Powered Media Authenticity Report", sub_style))
        story.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=16))

        # ── Job Info ──────────────────────────────
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        info_data = [
            ["Job ID",     job_id[:16] + "..."],
            ["File",       media.get("filename", "—")],
            ["Generated",  now],
            ["File Size",  f"{media.get('file_size_bytes', 0) / 1024 / 1024:.1f} MB"],
            ["Media Type", media.get("mime_type", "—")],
        ]
        info_table = Table(info_data, colWidths=[4*cm, 13*cm])
        info_table.setStyle(TableStyle([
            ("FONTNAME",    (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("TEXTCOLOR",   (0,0), (0,-1),  GRAY),
            ("TEXTCOLOR",   (1,0), (1,-1),  DARK),
            ("FONTNAME",    (0,0), (0,-1),  "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,0), (-1,-1), [LIGHT, colors.white]),
            ("TOPPADDING",  (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 16))

        # ── Verdict Banner ────────────────────────
        verdict_label = {
            "fake": "⚠ DEEPFAKE / AI-GENERATED DETECTED",
            "suspicious": "◉ SUSPICIOUS CONTENT",
            "authentic": "✓ AUTHENTIC MEDIA",
        }.get(verdict, verdict.upper())

        verdict_style = ParagraphStyle(
            "Verdict", parent=styles["Normal"],
            fontSize=14, textColor=colors.white,
            fontName="Helvetica-Bold",
            backColor=verdict_color,
            borderPadding=(10, 16, 10, 16),
            alignment=TA_CENTER,
        )
        story.append(Paragraph(verdict_label, verdict_style))
        story.append(Spacer(1, 16))

        # ── Authenticity Score ────────────────────
        section_style = ParagraphStyle(
            "Section", parent=styles["Normal"],
            fontSize=11, fontName="Helvetica-Bold",
            textColor=DARK, spaceAfter=8, spaceBefore=12,
        )
        story.append(Paragraph("Authenticity Score", section_style))

        score_data = [["Score", "Verdict", "Confidence", "Frames Analyzed", "Frames Flagged"]]
        score_data.append([
            f"{score}%",
            verdict.upper(),
            f"{round(result.get('confidence', 0) * 100)}%",
            str(result.get("frames_analyzed", 0)),
            str(result.get("frames_flagged", 0)),
        ])
        score_table = Table(score_data, colWidths=[3.4*cm]*5)
        score_table.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0),  DARK),
            ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
            ("FONTNAME",    (0,0), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 10),
            ("ALIGN",       (0,0), (-1,-1), "CENTER"),
            ("TOPPADDING",  (0,0), (-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("TEXTCOLOR",   (0,1), (0,1),   verdict_color),
            ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 8))

        # ── Detection Signals ─────────────────────
        story.append(Paragraph("Detection Signals", section_style))
        signal_labels = {
            "face_swap":              "Face Swap Probability",
            "gan_artifacts":          "GAN Artifact Score",
            "temporal_inconsistency": "Temporal Inconsistency",
            "blink_anomaly":          "Blink Anomaly Score",
            "jpeg_artifacts":         "JPEG/ELA Artifact Score",
        }
        sig_data = [["Signal", "Score", "Interpretation"]]
        for key, label in signal_labels.items():
            val = signals.get(key, 0.0)
            pct = round(val * 100)
            interp = "High Risk" if pct > 70 else "Medium Risk" if pct > 40 else "Low Risk"
            sig_data.append([label, f"{pct}%", interp])

        sig_table = Table(sig_data, colWidths=[7*cm, 3*cm, 7*cm])
        sig_table.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0),  DARK),
            ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
            ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTNAME",    (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("ALIGN",       (1,0), (1,-1),  "CENTER"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT, colors.white]),
            ("TOPPADDING",  (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ]))
        story.append(sig_table)
        story.append(Spacer(1, 8))

        # ── Heatmap ───────────────────────────────
        heatmap_url  = result.get("heatmap_url")
        heatmap_path = f".{heatmap_url}" if heatmap_url else None
        if heatmap_path and os.path.exists(heatmap_path):
            story.append(Paragraph("Forensic Heatmap", section_style))
            story.append(RLImage(heatmap_path, width=8*cm, height=5.5*cm))
            story.append(Spacer(1, 8))

        # ── Frame Results ─────────────────────────
        if frames:
            story.append(Paragraph("Frame-Level Analysis (first 20)", section_style))
            f_data = [["Frame", "Timestamp", "Manipulated", "Confidence", "Face"]]
            for f in frames[:20]:
                f_data.append([
                    str(f.get("frame_index", "")),
                    f"{f.get('timestamp_sec', 0):.1f}s",
                    "YES" if f.get("is_manipulated") else "no",
                    f"{round(f.get('confidence', 0) * 100)}%",
                    "✓" if f.get("face_detected") else "✗",
                ])
            f_table = Table(f_data, colWidths=[2.5*cm, 3*cm, 3.5*cm, 3.5*cm, 2.5*cm])
            f_table.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,0),  DARK),
                ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
                ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
                ("FONTNAME",    (0,1), (-1,-1), "Helvetica"),
                ("FONTSIZE",    (0,0), (-1,-1), 8),
                ("ALIGN",       (0,0), (-1,-1), "CENTER"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT, colors.white]),
                ("TOPPADDING",  (0,0), (-1,-1), 5),
                ("BOTTOMPADDING",(0,0),(-1,-1), 5),
                ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
            ]))
            story.append(f_table)
            story.append(Spacer(1, 8))

        # ── Footer ────────────────────────────────
        story.append(HRFlowable(width="100%", thickness=1, color=GRAY, spaceBefore=16))
        footer_style = ParagraphStyle(
            "Footer", parent=styles["Normal"],
            fontSize=8, textColor=GRAY, alignment=TA_CENTER,
        )
        story.append(Paragraph(
            f"Generated by MediaForensics Platform · {now} · Job {job_id[:8]}",
            footer_style
        ))

        doc.build(story)
        logger.info(f"[Report] Generated PDF: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"[Report] Failed to generate PDF: {e}", exc_info=True)
        return None

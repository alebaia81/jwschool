#!/usr/bin/env python3
"""
generator.py - Modulo per la generazione dei tagliandini S-89 in PDF per Jw School.
Fornisce funzioni per la generazione di fogli A4 mensili e singoli tagliandini.
"""

import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors

SLIP_W = 95 * mm
SLIP_H = 135 * mm
PAGE_MARGIN_X = 10 * mm
PAGE_MARGIN_Y = 13 * mm


def draw_slip(c, x, y, assegnazione):
    """Disegna un singolo tagliandino S-89 nella posizione (x, y)."""
    # Bordo tratteggiato di ritaglio
    c.setStrokeColor(colors.Color(0.65, 0.65, 0.65))
    c.setLineWidth(0.4)
    c.setDash(3, 3)
    c.rect(x, y, SLIP_W, SLIP_H)
    c.setDash()

    inner_x = x + 5 * mm
    inner_w = SLIP_W - 10 * mm
    top_y = y + SLIP_H - 8 * mm

    # --- INTESTAZIONE ---
    c.setFillColor(colors.Color(0.15, 0.15, 0.15))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x + SLIP_W / 2, top_y, "PARTE PER L'ADUNANZA")
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(x + SLIP_W / 2, top_y - 11, "VITA CRISTIANA E MINISTERO")

    curr_y = top_y - 28
    c.setStrokeColor(colors.Color(0.5, 0.5, 0.5))
    c.setLineWidth(0.3)
    c.line(inner_x, curr_y + 3, inner_x + inner_w, curr_y + 3)

    # --- NOME E COGNOME ---
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.Color(0.2, 0.2, 0.2))
    c.drawString(inner_x, curr_y - 5, "Nome e cognome:")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.Color(0, 0, 0))
    c.drawString(inner_x + 1 * mm, curr_y - 17, assegnazione.get("studente", ""))
    c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
    c.setLineWidth(0.3)
    c.line(inner_x, curr_y - 19, inner_x + inner_w, curr_y - 19)
    curr_y -= 28

    # --- ASSISTENTE ---
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.Color(0.2, 0.2, 0.2))
    c.drawString(inner_x, curr_y, "Assistente:")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.Color(0, 0, 0))
    assistente = assegnazione.get("assistente", "")
    assistente_str = assistente if assistente else "—"
    c.drawString(inner_x + 1 * mm, curr_y - 12, assistente_str)
    c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
    c.line(inner_x, curr_y - 14, inner_x + inner_w, curr_y - 14)
    curr_y -= 23

    # --- DATA ---
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.Color(0.2, 0.2, 0.2))
    c.drawString(inner_x, curr_y, "Data:")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.Color(0, 0, 0))
    c.drawString(inner_x + 1 * mm, curr_y - 12, assegnazione.get("data", ""))
    c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
    c.line(inner_x, curr_y - 14, inner_x + inner_w, curr_y - 14)
    curr_y -= 23

    # --- PARTE N. ---
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.Color(0.2, 0.2, 0.2))
    c.drawString(inner_x, curr_y, "Parte n.:")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.Color(0, 0, 0))
    c.drawString(inner_x + 1 * mm, curr_y - 12, str(assegnazione.get("parte_n", "")))
    c.setFont("Helvetica-Oblique", 6.5)
    c.setFillColor(colors.Color(0.3, 0.3, 0.3))
    tipo_text = assegnazione.get("tipo", "")
    if len(tipo_text) > 45:
        tipo_text = tipo_text[:42] + "..."
    c.drawString(inner_x + 1 * mm, curr_y - 22, tipo_text)
    c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
    c.line(inner_x, curr_y - 25, inner_x + inner_w, curr_y - 25)
    curr_y -= 34

    # --- DA SVOLGERE NELLA ---
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.Color(0.2, 0.2, 0.2))
    c.drawString(inner_x, curr_y, "Da svolgere nella:")
    curr_y -= 13

    # Sala principale (✓)
    c.setStrokeColor(colors.Color(0.3, 0.3, 0.3))
    c.setLineWidth(0.5)
    c.rect(inner_x + 2 * mm, curr_y - 1, 7, 7)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.Color(0, 0, 0))
    c.drawString(inner_x + 3 * mm, curr_y, "✓")
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.Color(0.2, 0.2, 0.2))
    c.drawString(inner_x + 12 * mm, curr_y, "Sala principale")

    curr_y -= 12
    c.rect(inner_x + 2 * mm, curr_y - 1, 7, 7)
    c.drawString(inner_x + 12 * mm, curr_y, "Sala secondaria 1")

    curr_y -= 12
    c.rect(inner_x + 2 * mm, curr_y - 1, 7, 7)
    c.drawString(inner_x + 12 * mm, curr_y, "Sala secondaria 2")

    # --- NOTA ---
    note_y = y + 5 * mm
    c.setFont("Helvetica", 5)
    c.setFillColor(colors.Color(0.4, 0.4, 0.4))
    c.drawString(inner_x, note_y + 14, "Nota per lo studente: La fonte e la lezione che")
    c.drawString(inner_x, note_y + 8, "riguardano la tua parte sono indicate nella Guida")
    c.drawString(inner_x, note_y + 2, "per l'adunanza Vita e ministero.")
    c.setFont("Helvetica", 5)
    c.setFillColor(colors.Color(0.5, 0.5, 0.5))
    c.drawString(inner_x, y + 2 * mm, "S-89-I  11/23")


def generate_pdf_bytes(assegnazioni):
    """Genera i byte di un PDF A4 contenente i tagliandini (4 per pagina)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_w, page_h = A4

    positions = [
        (PAGE_MARGIN_X, page_h - PAGE_MARGIN_Y - SLIP_H),
        (PAGE_MARGIN_X + SLIP_W + 5 * mm, page_h - PAGE_MARGIN_Y - SLIP_H),
        (PAGE_MARGIN_X, PAGE_MARGIN_Y),
        (PAGE_MARGIN_X + SLIP_W + 5 * mm, PAGE_MARGIN_Y),
    ]

    for i, assegnazione in enumerate(assegnazioni):
        slot = i % 4
        if slot == 0 and i > 0:
            c.showPage()
        pos_x, pos_y = positions[slot]
        draw_slip(c, pos_x, pos_y, assegnazione)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_single_slip_bytes(assegnazione):
    """Genera i byte di un PDF contenente un singolo tagliandino S-89 (formato esatto $95\\text{mm} \\times 135\\text{mm}$)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(SLIP_W, SLIP_H))
    draw_slip(c, 0, 0, assegnazione)
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

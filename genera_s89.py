#!/usr/bin/env python3
"""
Genera tagliandini S-89 compilati in PDF dal programma AVM.
Organizzati per cartelle mensili. Ogni foglio A4 contiene 4 tagliandini (2x2).
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os

# =====================================================
# DATI ASSEGNAZIONI - estratti dal programma AVM
# =====================================================

assegnazioni = [
    # --- 6 maggio | ISAIA 58-59 ---
    {"data": "6 maggio 2026", "mese": "Maggio", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Ghilardotti S.", "assistente": ""},
    {"data": "6 maggio 2026", "mese": "Maggio", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Zhou J.", "assistente": "Armelloni A."},
    {"data": "6 maggio 2026", "mese": "Maggio", "parte_n": "5",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Ghilardotti T.", "assistente": "Doro R."},
    {"data": "6 maggio 2026", "mese": "Maggio", "parte_n": "6",
     "tipo": "Discorso (5 min)", "studente": "Sirianni L.", "assistente": ""},

    # --- 13 maggio | ISAIA 60-61 ---
    {"data": "13 maggio 2026", "mese": "Maggio", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Uggetti M.", "assistente": ""},
    {"data": "13 maggio 2026", "mese": "Maggio", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Sirianni S.", "assistente": "Merli L."},
    {"data": "13 maggio 2026", "mese": "Maggio", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Hua I.", "assistente": "Paganuzzi I."},
    {"data": "13 maggio 2026", "mese": "Maggio", "parte_n": "6",
     "tipo": "Fare discepoli (5 min)", "studente": "Tilaro A.", "assistente": "Greco A."},

    # --- 20 maggio | ISAIA 62-64 ---
    {"data": "20 maggio 2026", "mese": "Maggio", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Arnone A.", "assistente": ""},
    {"data": "20 maggio 2026", "mese": "Maggio", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "La Malfa G.", "assistente": "Pellegri A."},
    {"data": "20 maggio 2026", "mese": "Maggio", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Pellegri L.", "assistente": "Arquati M."},
    {"data": "20 maggio 2026", "mese": "Maggio", "parte_n": "6",
     "tipo": "Fare discepoli (5 min)", "studente": "Uggetti L.", "assistente": "Bambini D."},

    # --- 27 maggio | ISAIA 65-66 ---
    {"data": "27 maggio 2026", "mese": "Maggio", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Freddi I.", "assistente": ""},
    {"data": "27 maggio 2026", "mese": "Maggio", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Doro R.", "assistente": "Romanini L."},
    {"data": "27 maggio 2026", "mese": "Maggio", "parte_n": "5",
     "tipo": "Iniziare una conversazione (2 min)", "studente": "Freddi G.", "assistente": "Baiamonte P."},
    {"data": "27 maggio 2026", "mese": "Maggio", "parte_n": "6",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Armelloni A.", "assistente": "Bordonaro M."},
    {"data": "27 maggio 2026", "mese": "Maggio", "parte_n": "7",
     "tipo": "Spiegare quello in cui si crede (3 min)", "studente": "Romano V.", "assistente": "Braghè R."},

    # --- 3 giugno | GEREMIA 1-3 ---
    {"data": "3 giugno 2026", "mese": "Giugno", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Tilaro C.", "assistente": ""},
    {"data": "3 giugno 2026", "mese": "Giugno", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Vidali L.", "assistente": "Tilaro A."},
    {"data": "3 giugno 2026", "mese": "Giugno", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Uggetti N.", "assistente": "La Malfa G."},
    {"data": "3 giugno 2026", "mese": "Giugno", "parte_n": "6",
     "tipo": "Fare discepoli (5 min)", "studente": "Romano I.", "assistente": "Arnone E."},

    # --- 10 giugno | GEREMIA 4-6 ---
    {"data": "10 giugno 2026", "mese": "Giugno", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Bori G.", "assistente": ""},
    {"data": "10 giugno 2026", "mese": "Giugno", "parte_n": "4",
     "tipo": "Iniziare una conversazione (2 min)", "studente": "Bigatel L.", "assistente": "Ghilardotti T."},
    {"data": "10 giugno 2026", "mese": "Giugno", "parte_n": "5",
     "tipo": "Iniziare una conversazione (2 min)", "studente": "Briceag E.", "assistente": "Maglia A."},
    {"data": "10 giugno 2026", "mese": "Giugno", "parte_n": "6",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Baiamonte F.", "assistente": "Romano V."},
    {"data": "10 giugno 2026", "mese": "Giugno", "parte_n": "7",
     "tipo": "Spiegare quello in cui si crede (3 min)", "studente": "Merli G.", "assistente": "Ghilardotti S."},

    # --- 17 giugno | GEREMIA 7-8 ---
    {"data": "17 giugno 2026", "mese": "Giugno", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Braghè L.", "assistente": ""},
    {"data": "17 giugno 2026", "mese": "Giugno", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Briceag A.", "assistente": "Pellegri L."},
    {"data": "17 giugno 2026", "mese": "Giugno", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Cusano A.", "assistente": "Sirianni S."},
    {"data": "17 giugno 2026", "mese": "Giugno", "parte_n": "6",
     "tipo": "Fare discepoli (5 min)", "studente": "Romanini L.", "assistente": "Zhou J."},

    # --- 24 giugno | GEREMIA 9-10 ---
    {"data": "24 giugno 2026", "mese": "Giugno", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Armelloni F.", "assistente": ""},
    {"data": "24 giugno 2026", "mese": "Giugno", "parte_n": "4",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Bambini D.", "assistente": "Hua I."},
    {"data": "24 giugno 2026", "mese": "Giugno", "parte_n": "5",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Merli L.", "assistente": "Uggetti L."},
    {"data": "24 giugno 2026", "mese": "Giugno", "parte_n": "6",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Di Lallo C.", "assistente": "Doro R."},

    # --- 1 luglio | GEREMIA 11-12 ---
    {"data": "1 luglio 2026", "mese": "Luglio", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Arquati U.", "assistente": ""},
    {"data": "1 luglio 2026", "mese": "Luglio", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Antonelli R.", "assistente": "Armelloni A."},
    {"data": "1 luglio 2026", "mese": "Luglio", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Romano A.", "assistente": "Freddi G."},
    {"data": "1 luglio 2026", "mese": "Luglio", "parte_n": "6",
     "tipo": "Discorsi (5 min)", "studente": "Zhou A.", "assistente": ""},

    # --- 8 luglio | GEREMIA 13-15 ---
    {"data": "8 luglio 2026", "mese": "Luglio", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Bordonaro M.", "assistente": ""},
    {"data": "8 luglio 2026", "mese": "Luglio", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Armelloni A.", "assistente": "Uggetti N."},
    {"data": "8 luglio 2026", "mese": "Luglio", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Paganuzzi I.", "assistente": "Bigatel L."},
    {"data": "8 luglio 2026", "mese": "Luglio", "parte_n": "6",
     "tipo": "Discorso (5 min)", "studente": "Di Lallo A.", "assistente": ""},

    # --- 15 luglio | GEREMIA 16-17 ---
    {"data": "15 luglio 2026", "mese": "Luglio", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Antonelli A.", "assistente": ""},
    {"data": "15 luglio 2026", "mese": "Luglio", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Baiamonte P.", "assistente": "Tilaro A."},
    {"data": "15 luglio 2026", "mese": "Luglio", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Xhelo S.", "assistente": "Freddi G."},
    {"data": "15 luglio 2026", "mese": "Luglio", "parte_n": "6",
     "tipo": "Fare discepoli (5 min)", "studente": "Pellegri L.", "assistente": "Braghè R."},

    # --- 29 luglio | GEREMIA 20-21 ---
    {"data": "29 luglio 2026", "mese": "Luglio", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Doro D.", "assistente": ""},
    {"data": "29 luglio 2026", "mese": "Luglio", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Ghilardotti T.", "assistente": "Baiamonte P."},
    {"data": "29 luglio 2026", "mese": "Luglio", "parte_n": "5",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "La Malfa G.", "assistente": "Briceag E."},
    {"data": "29 luglio 2026", "mese": "Luglio", "parte_n": "6",
     "tipo": "Spiegare quello in cui si crede (3 min)", "studente": "Zhou J.", "assistente": "Romano A."},

    # --- 5 agosto | GEREMIA 22-23 ---
    {"data": "5 agosto 2026", "mese": "Agosto", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Greco N.", "assistente": ""},
    {"data": "5 agosto 2026", "mese": "Agosto", "parte_n": "4",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Hua I.", "assistente": "Pellegri L."},
    {"data": "5 agosto 2026", "mese": "Agosto", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Romano V.", "assistente": "Arquati M."},
    {"data": "5 agosto 2026", "mese": "Agosto", "parte_n": "6",
     "tipo": "Discorso (4 min)", "studente": "Arnone A.", "assistente": ""},

    # --- 12 agosto | GEREMIA 24-25 ---
    {"data": "12 agosto 2026", "mese": "Agosto", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Sbarufatti S.", "assistente": ""},
    {"data": "12 agosto 2026", "mese": "Agosto", "parte_n": "4",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Uggetti N.", "assistente": "Pellegri A."},
    {"data": "12 agosto 2026", "mese": "Agosto", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Uggetti L.", "assistente": "Rosita B."},
    {"data": "12 agosto 2026", "mese": "Agosto", "parte_n": "6",
     "tipo": "Fare discepoli (4 min)", "studente": "Tilaro A.", "assistente": "Antonelli R."},

    # --- 19 agosto | GEREMIA 26-28 ---
    {"data": "19 agosto 2026", "mese": "Agosto", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Bordonaro Ml.", "assistente": ""},
    {"data": "19 agosto 2026", "mese": "Agosto", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Bordonaro M.", "assistente": "Armelloni A."},
    {"data": "19 agosto 2026", "mese": "Agosto", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Romanini L.", "assistente": "Xhelo S."},
    {"data": "19 agosto 2026", "mese": "Agosto", "parte_n": "6",
     "tipo": "Fare discepoli (5 min)", "studente": "Romano I.", "assistente": "Cusano A."},

    # --- 26 agosto | GEREMIA 29-30 ---
    {"data": "26 agosto 2026", "mese": "Agosto", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Freddi I.", "assistente": ""},
    {"data": "26 agosto 2026", "mese": "Agosto", "parte_n": "4",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Sirianni S.", "assistente": "Di Lallo C."},
    {"data": "26 agosto 2026", "mese": "Agosto", "parte_n": "5",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Doro R.", "assistente": "Merli L."},
    {"data": "26 agosto 2026", "mese": "Agosto", "parte_n": "6",
     "tipo": "Discorso (5 min)", "studente": "Tilaro C.", "assistente": ""},

    # --- 2 settembre | GEREMIA 31 ---
    {"data": "2 settembre 2026", "mese": "Settembre", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Ghilardotti S.", "assistente": ""},
    {"data": "2 settembre 2026", "mese": "Settembre", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Freddi G.", "assistente": "Zhou J."},
    {"data": "2 settembre 2026", "mese": "Settembre", "parte_n": "5",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Baiamonte F.", "assistente": "Baiamonte P."},
    {"data": "2 settembre 2026", "mese": "Settembre", "parte_n": "6",
     "tipo": "Spiegare quello in cui si crede (5 min)", "studente": "Cusano A.", "assistente": "Romano V."},

    # --- 9 settembre | GEREMIA 32-33 ---
    {"data": "9 settembre 2026", "mese": "Settembre", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Arquati U.", "assistente": ""},
    {"data": "9 settembre 2026", "mese": "Settembre", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Bambini D.", "assistente": "Cusano A."},
    {"data": "9 settembre 2026", "mese": "Settembre", "parte_n": "5",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Romano V.", "assistente": "Uggetti N."},
    {"data": "9 settembre 2026", "mese": "Settembre", "parte_n": "6",
     "tipo": "Coltivare l'interesse (5 min)", "studente": "Briceag E.", "assistente": "Ghilardotti T."},

    # --- 16 settembre | GEREMIA 34-35 ---
    {"data": "16 settembre 2026", "mese": "Settembre", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Armelloni F.", "assistente": ""},
    {"data": "16 settembre 2026", "mese": "Settembre", "parte_n": "4",
     "tipo": "Iniziare una conversazione (2 min)", "studente": "Briceag A.", "assistente": "Braghè R."},
    {"data": "16 settembre 2026", "mese": "Settembre", "parte_n": "5",
     "tipo": "Iniziare una conversazione (2 min)", "studente": "Antonelli R.", "assistente": "Freddi G."},
    {"data": "16 settembre 2026", "mese": "Settembre", "parte_n": "6",
     "tipo": "Coltivare l'interesse (3 min)", "studente": "Merli L.", "assistente": "Sirianni S."},
    {"data": "16 settembre 2026", "mese": "Settembre", "parte_n": "7",
     "tipo": "Fare discepoli (4 min)", "studente": "Tilaro A.", "assistente": "Antonelli R."},

    # --- 23 settembre | GEREMIA 36-37 ---
    {"data": "23 settembre 2026", "mese": "Settembre", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Braghè L.", "assistente": ""},
    {"data": "23 settembre 2026", "mese": "Settembre", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Vidali L.", "assistente": "Tilaro A."},
    {"data": "23 settembre 2026", "mese": "Settembre", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Paganuzzi I.", "assistente": "Greco A."},
    {"data": "23 settembre 2026", "mese": "Settembre", "parte_n": "6",
     "tipo": "Cosa direste? (5 min)", "studente": "Armelloni A.", "assistente": "Arnone E."},

    # --- 30 settembre | GEREMIA 38-39 ---
    {"data": "30 settembre 2026", "mese": "Settembre", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Bori G.", "assistente": ""},
    {"data": "30 settembre 2026", "mese": "Settembre", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Xhelo S.", "assistente": "Merli L."},
    {"data": "30 settembre 2026", "mese": "Settembre", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Pellegri L.", "assistente": "Maglia A."},
    {"data": "30 settembre 2026", "mese": "Settembre", "parte_n": "6",
     "tipo": "Cosa direste? (6 min)", "studente": "Romano A.", "assistente": "Uggetti L."},

    # --- 7 ottobre | GEREMIA 40-41 ---
    {"data": "7 ottobre 2026", "mese": "Ottobre", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Merli G.", "assistente": ""},
    {"data": "7 ottobre 2026", "mese": "Ottobre", "parte_n": "4",
     "tipo": "Iniziare una conversazione (2 min)", "studente": "Baiamonte P.", "assistente": "Bambini D."},
    {"data": "7 ottobre 2026", "mese": "Ottobre", "parte_n": "5",
     "tipo": "Iniziare una conversazione (2 min)", "studente": "La Malfa G.", "assistente": "Di Lallo C."},
    {"data": "7 ottobre 2026", "mese": "Ottobre", "parte_n": "6",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Zhou J.", "assistente": "Arquati M."},
    {"data": "7 ottobre 2026", "mese": "Ottobre", "parte_n": "7",
     "tipo": "Spiegare quello in cui si crede (3 min)", "studente": "Ghilardotti T.", "assistente": "Doro R."},

    # --- 21 ottobre | GEREMIA 45-46 ---
    {"data": "21 ottobre 2026", "mese": "Ottobre", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Uggetti M.", "assistente": ""},
    {"data": "21 ottobre 2026", "mese": "Ottobre", "parte_n": "4",
     "tipo": "Iniziare una conversazione (3 min)", "studente": "Hua I.", "assistente": "Baiamonte P."},
    {"data": "21 ottobre 2026", "mese": "Ottobre", "parte_n": "5",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Tilaro A.", "assistente": "Briceag A."},
    {"data": "21 ottobre 2026", "mese": "Ottobre", "parte_n": "6",
     "tipo": "Iniziare una conversazione (5 min)", "studente": "Uggetti L.", "assistente": "Armelloni A."},
    {"data": "21 ottobre 2026", "mese": "Ottobre", "parte_n": "7",
     "tipo": "Discorso (5 min)", "studente": "Tilaro C.", "assistente": ""},

    # --- 28 ottobre | GEREMIA 47-48 ---
    {"data": "28 ottobre 2026", "mese": "Ottobre", "parte_n": "3",
     "tipo": "Lettura biblica (4 min o meno)", "studente": "Sirianni L.", "assistente": ""},
    {"data": "28 ottobre 2026", "mese": "Ottobre", "parte_n": "4",
     "tipo": "Iniziare una conversazione (4 min)", "studente": "Uggetti N.", "assistente": "Paganuzzi I."},
    {"data": "28 ottobre 2026", "mese": "Ottobre", "parte_n": "5",
     "tipo": "Coltivare l'interesse (4 min)", "studente": "Romanini L.", "assistente": "Ghilardotti T."},
    {"data": "28 ottobre 2026", "mese": "Ottobre", "parte_n": "6",
     "tipo": "Fare discepoli (5 min)", "studente": "Romano I.", "assistente": "Xhelo S."},
]


# =====================================================
# GENERATORE PDF S-89
# =====================================================

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
    c.drawString(inner_x + 1 * mm, curr_y - 17, assegnazione["studente"])
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
    assistente = assegnazione["assistente"] if assegnazione["assistente"] else "—"
    c.drawString(inner_x + 1 * mm, curr_y - 12, assistente)
    c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
    c.line(inner_x, curr_y - 14, inner_x + inner_w, curr_y - 14)
    curr_y -= 23

    # --- DATA ---
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.Color(0.2, 0.2, 0.2))
    c.drawString(inner_x, curr_y, "Data:")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.Color(0, 0, 0))
    c.drawString(inner_x + 1 * mm, curr_y - 12, assegnazione["data"])
    c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
    c.line(inner_x, curr_y - 14, inner_x + inner_w, curr_y - 14)
    curr_y -= 23

    # --- PARTE N. ---
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.Color(0.2, 0.2, 0.2))
    c.drawString(inner_x, curr_y, "Parte n.:")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.Color(0, 0, 0))
    c.drawString(inner_x + 1 * mm, curr_y - 12, assegnazione["parte_n"])
    c.setFont("Helvetica-Oblique", 6.5)
    c.setFillColor(colors.Color(0.3, 0.3, 0.3))
    tipo_text = assegnazione["tipo"]
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


def genera_pdf_mese(assegnazioni_mese, output_path):
    """Genera il PDF con i tagliandini S-89 di un mese, 4 per pagina."""

    c = canvas.Canvas(output_path, pagesize=A4)
    page_w, page_h = A4

    positions = [
        (PAGE_MARGIN_X, page_h - PAGE_MARGIN_Y - SLIP_H),
        (PAGE_MARGIN_X + SLIP_W + 5 * mm, page_h - PAGE_MARGIN_Y - SLIP_H),
        (PAGE_MARGIN_X, PAGE_MARGIN_Y),
        (PAGE_MARGIN_X + SLIP_W + 5 * mm, PAGE_MARGIN_Y),
    ]

    for i, assegnazione in enumerate(assegnazioni_mese):
        slot = i % 4
        if slot == 0 and i > 0:
            c.showPage()
        pos_x, pos_y = positions[slot]
        draw_slip(c, pos_x, pos_y, assegnazione)

    c.save()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Raggruppa per mese
    mesi = {}
    for a in assegnazioni:
        mese = a["mese"]
        if mese not in mesi:
            mesi[mese] = []
        mesi[mese].append(a)

    print("=" * 50)
    print("  GENERAZIONE S-89 PER MESE")
    print("=" * 50)

    for mese, lista in mesi.items():
        # Crea cartella del mese
        cartella = os.path.join(base_dir, mese)
        os.makedirs(cartella, exist_ok=True)

        # Genera PDF
        nome_file = f"S-89_{mese}_2026.pdf"
        percorso = os.path.join(cartella, nome_file)
        genera_pdf_mese(lista, percorso)

        n_pagine = (len(lista) + 3) // 4
        print(f"\n📁 {mese}/")
        print(f"   📄 {nome_file}")
        print(f"      → {len(lista)} tagliandini, {n_pagine} pagine")

    print(f"\n✅ Fatto! Cartelle create in: {base_dir}")


if __name__ == "__main__":
    main()

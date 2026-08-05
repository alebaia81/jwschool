#!/usr/bin/env python3
"""
parser.py - Modulo per l'estrazione automatica delle assegnazioni dai PDF AVM.
Sfrutta la normalizzazione del testo ed il matching posizionale per abbinare
date, parti, studenti e assistenti, inclusi i casi in cui titolo e studente
si trovano sulla stessa riga nel PDF.
"""

import re
import os
import pypdf
import io


def extract_assignments_from_pdf(file_input):
    """
    Legge un file PDF AVM (percorso file str, bytes o stream) e restituisce
    la lista strutturata delle assegnazioni degli studenti.
    """
    if isinstance(file_input, bytes):
        reader = pypdf.PdfReader(io.BytesIO(file_input))
    elif hasattr(file_input, "read"):
        reader = pypdf.PdfReader(file_input)
    else:
        reader = pypdf.PdfReader(file_input)

    full_text = ""
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            full_text += "\n" + txt

    return _parse_by_sections(full_text)


def _parse_by_sections(full_text):
    assegnazioni = []

    pattern_settimana = r'(\d{1,2})\s+([a-zA-Zàèéìòù]+)\s*\|\s*([^\n]+)'
    matches = list(re.finditer(pattern_settimana, full_text))

    for i, match in enumerate(matches):
        giorno = match.group(1)
        mese_raw = match.group(2).strip()
        mese_cap = mese_raw.capitalize()
        data_str = f"{giorno} {mese_raw.lower()} 2026"

        start_idx = match.end()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)

        block_text = full_text[start_idx:end_idx]

        # 1. Lettura biblica in TESORI DELLA PAROLA DI DIO
        parte_n = 3
        lb = re.search(r'Lettura biblica[^\n]*\n?\s*Studente:\s*([^\n]+)', block_text, re.IGNORECASE)
        if lb:
            studente_raw = lb.group(1).strip()
            if "EFFICACI" in studente_raw:
                studente_raw = studente_raw.split("EFFICACI")[0].strip()
            assegnazioni.append({
                "data": data_str,
                "mese": mese_cap,
                "parte_n": str(parte_n),
                "tipo": "Lettura biblica (4 min o meno)",
                "studente": studente_raw,
                "assistente": ""
            })
            parte_n += 1

        # 2. Sezione EFFICACI NEL MINISTERO
        if 'EFFICACI NEL MINISTERO' in block_text:
            min_pos = block_text.find('EFFICACI NEL MINISTERO')
            vita_pos = block_text.find('VITA CRISTIANA')
            min_text = block_text[min_pos:(vita_pos if vita_pos != -1 else len(block_text))]

            # Unisci righe spezzate nei titoli
            cleaned = min_text
            cleaned = re.sub(r'([\uf0b7•]\s*[^\n\(\)]+)\n+\s*(\(\s*\d+\s*min)', r'\1 \2', cleaned)
            cleaned = re.sub(r'\(\s*(\d+)\s*\n+\s*min\s*(?:o meno)?\s*\)', r'(\1 min)', cleaned)

            titoli = []
            nomi = []

            lines = cleaned.splitlines()
            idx_line = 0
            while idx_line < len(lines):
                line = lines[idx_line].strip()
                if not line or 'EFFICACI' in line:
                    idx_line += 1
                    continue

                # Caso speciale: Titolo e Studente sulla STESSA riga
                same_line_match = re.search(r'([\uf0b7•]?\s*[A-ZÀÈÉÌÒÙa-zàèéìòù\'’\?\!\s]+\(\s*\d+\s*min\s*(?:o meno)?\s*\))\s*Studente(?:/Assistente)?:?\s*(.*)', line)
                if same_line_match:
                    t = ' '.join(same_line_match.group(1).replace('•', '').replace('\uf0b7', '').split())
                    n = same_line_match.group(2).strip()
                    titoli.append(t)
                    nomi.append(n)
                elif '•' in line or '\uf0b7' in line or ('(' in line and 'min' in line):
                    t_candidate = line
                    if not ('(' in t_candidate and 'min' in t_candidate) and idx_line + 1 < len(lines):
                        next_line = lines[idx_line + 1].strip()
                        if '(' in next_line and 'min' in next_line:
                            t_candidate = t_candidate + ' ' + next_line
                            idx_line += 1
                    t = ' '.join(t_candidate.replace('•', '').replace('\uf0b7', '').split())
                    if 'Lettura' not in t and t:
                        titoli.append(t)
                elif 'Studente/Assistente' in line:
                    rest = line.replace('Studente/Assistente:', '').replace('Studente/Assistente', '').strip()
                    if rest:
                        nomi.append(rest)
                elif line and not line.startswith('•') and not line.startswith('\uf0b7') and 'min)' not in line:
                    nomi.append(line)
                idx_line += 1

            for p_idx, titolo in enumerate(titoli):
                n = nomi[p_idx] if p_idx < len(nomi) else ""
                if "/" in n:
                    parts = n.split("/")
                    stud = parts[0].strip()
                    ass = parts[1].strip() if len(parts) > 1 else ""
                else:
                    stud = n.strip()
                    ass = ""

                assegnazioni.append({
                    "data": data_str,
                    "mese": mese_cap,
                    "parte_n": str(parte_n),
                    "tipo": titolo,
                    "studente": stud,
                    "assistente": ass
                })
                parte_n += 1

    return assegnazioni


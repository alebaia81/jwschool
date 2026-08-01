#!/usr/bin/env python3
"""
parser.py - Modulo per l'estrazione automatica delle assegnazioni dai PDF AVM.
Sfrutta la normalizzazione del testo ed il matching posizionale per abbinare
date, parti, studenti e assistenti.
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

            # Unisci righe spezzate come '(3\nmin)' in '(3 min)'
            min_text_clean = re.sub(r'\(\s*(\d+)\s*\n\s*min\s*(?:o meno)?\s*\)', r'(\1 min)', min_text)

            # Titoli: qualsiasi bullet o riga con (N min)
            titoli_raw = re.findall(r'(?:[\uf0b7•]|\b)\s*([A-ZÀÈÉÌÒÙa-zàèéìòù\'’\?\!\s]+\(\s*\d+\s*min\s*(?:o meno)?\s*\))', min_text_clean)
            titoli = [' '.join(t.split()) for t in titoli_raw if 'Lettura' not in t]

            # Nomi: righe con nomi che non sono titoli
            nomi = []
            for line in min_text_clean.splitlines():
                line_str = line.strip()
                if 'Studente/Assistente:' in line_str:
                    line_str = line_str.replace('Studente/Assistente:', '').strip()
                if 'Studente/Assistente' in line_str:
                    line_str = line_str.replace('Studente/Assistente', '').strip()

                if (line_str and not line_str.startswith('•')
                        and not line_str.startswith('\uf0b7')
                        and '(' not in line_str
                        and 'MINISTERO' not in line_str
                        and line_str != 'min)'):
                    nomi.append(line_str)

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


if __name__ == "__main__":
    test_pdf = "AVM settembre-ottobre.pdf"
    if os.path.exists(test_pdf):
        res = extract_assignments_from_pdf(test_pdf)
        print(f"Estratte {len(res)} assegnazioni da {test_pdf}:")
        for r in res[:10]:
            print(" ", r)

# Jw School — Specifiche di Progetto & Memoria Tecnica

**Nome Progetto:** Jw School  
**Scopo:** Applicazione Web per l'estrazione automatica delle assegnazioni dai programmi dell'adunanza "Vita e Ministero" (AVM) e la generazione personalizzabile dei tagliandini S-89 in formato PDF.  
**Data creazione memoria:** 1 Agosto 2026  

---

## 1. Riepilogo di Comprensione (Understanding Lock)

- **Utente Target:** Uso personale (singolo gestore/sorvegliante), con predisposizione per futura pubblicazione online.
- **Input:** File PDF del programma AVM ufficiale (es. `AVM settembre-ottobre.pdf`).
- **Funzionalità Principali:**
  1. Caricamento drag-and-drop del PDF AVM.
  2. Estrazione automatica mediante parser del testo (date, parti, studenti, assistenti).
  3. Griglia/Editor web interattivo per revisionare e modificare i dati prima della generazione.
  4. Generazione PDF mensili A4 (4 tagliandini per foglio $95\text{mm} \times 135\text{mm}$ con tratteggio di ritaglio).
  5. Generazione ed esportazione di singoli biglietti S-89 (per specifico studente o adunanza).
- **Esclusioni attuali (Non-Goals):** Autenticazione utenti complessa, database relazionale esterno.

---

## 2. Decision Log (Registro delle Decisioni)

| Decisione | Opzioni Considerate | Scelta Effettuata | Motivazione |
| :--- | :--- | :--- | :--- |
| **Stack Backend** | FastAPI vs Streamlit vs Node.js | **FastAPI (Python)** | Riutilizzo 100% del motore PDF ReportLab già sviluppato; isolamento logica; cloud-ready. |
| **Stack Frontend** | Streamlit vs Next.js vs HTML/JS | **HTML5 + Vanilla JS + CSS** | Massima personalizzazione grafica, reattività, anteprima a schermo dei biglietti S-89. |
| **Generatore PDF** | `pdf-lib` (JS) vs `reportlab` (Python) | **ReportLab (Python)** | Codice grafico $95\text{mm} \times 135\text{mm}$ già collaudato ed esatto in `genera_s89.py`. |
| **Architettura Deployment** | Solamente Locale vs Solamente Cloud | **Architettura Ibrida (Locale + Cloud-ready)** | Funziona offline su Mac via Python locale, pronta al deploy su Render/PythonAnywhere. |

---

## 3. Architettura del Sistema & Struttura File

```text
Teocrazia/
├── app.py              # Server Web FastAPI (Endpoint API REST)
├── parser.py           # Lettore & Estrattore del programma AVM dai file PDF
├── generator.py        # Generatore PDF S-89 (motore ReportLab adattato)
├── genera_s89.py       # Script CLI di riferimento originale
├── memory.md           # Questo documento di memoria tecnica
├── static/
│   ├── style.css       # Design CSS moderno (interfaccia pulita, responsive, Dark Mode)
│   └── app.js          # Logica client (drag-and-drop, tabella editabile, download)
└── templates/
    └── index.html      # Interfaccia utente principale di Jw School
```

---

## 4. Specifiche API REST

### `POST /api/extract`
- **Input:** Multipart Form Data (`file`: PDF AVM)
- **Output:** JSON contenente la lista delle adunanze e delle assegnazioni estratte.
  ```json
  [
    {
      "data": "9 settembre 2026",
      "mese": "Settembre",
      "parte_n": "3",
      "tipo": "Lettura biblica (4 min o meno)",
      "studente": "Arquati U.",
      "assistente": ""
    }
  ]
  ```

### `POST /api/generate`
- **Input:** JSON (lista delle assegnazioni approvate o modificate dall'utente).
- **Output:** Binary File PDF (formato A4 con fogli di 4 biglietti S-89 ciascuno).

### `POST /api/generate-single`
- **Input:** JSON (singola assegnazione).
- **Output:** Binary File PDF (singolo biglietto S-89 $95\text{mm} \times 135\text{mm}$).

---

## 5. Specifiche Interfaccia Utente (UI/UX)

1. **Header & Branding:** Titolo **Jw School** con indicatore di stato del server.
2. **Zona Dropzone:** Area visibile e responsive per trascinare il file PDF AVM.
3. **Tabella delle Assegnazioni:**
   - Suddivisa per mese e data adunanza.
   - Campi modificabili in tempo reale (`input` text).
   - Pulsanti azione per ogni riga: *Elimina*, *Scarica biglietto singolo*.
4. **Toolbar Azioni Principali:**
   - *Pulsante "Scarica Tutti i PDF Mensili (Zip / A4)"*
   - *Pulsante "Resetta/Nuovo File"*

---

## 6. Guida all'Esecuzione Locale e Futura Pubblicazione

### Esecuzione in Locale:
```bash
python3 -m pip install fastapi uvicorn reportlab pypdf
python3 app.py
```
L'applicazione si aprirà all'indirizzo `http://localhost:8000`.

### Futura Pubblicazione Cloud (es. Render / PythonAnywhere):
1. Creare repository Git.
2. Aggiungere file `requirements.txt` (`fastapi`, `uvicorn`, `reportlab`, `pypdf`).
3. Collegare a Render/PythonAnywhere puntando al comando `uvicorn app:app --host 0.0.0.0 --port $PORT`.

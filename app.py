#!/usr/bin/env python3
"""
app.py - Server Web FastAPI per l'applicazione Jw School.
Servizio backend per estrazione PDF AVM e generazione tagliandini S-89.
"""

import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Response, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from parser import extract_assignments_from_pdf
from generator import generate_pdf_bytes, generate_single_slip_bytes

app = FastAPI(title="Jw School", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _find_file(rel_path):
    possible = [
        os.path.join(BASE_DIR, rel_path),
        os.path.join(os.getcwd(), rel_path),
        os.path.join(os.path.dirname(BASE_DIR), rel_path),
        os.path.join("/var/task", rel_path)
    ]
    for p in possible:
        if os.path.exists(p):
            return p
    return None


@app.get("/static/{file_path:path}")
async def get_static(file_path: str):
    target = _find_file(os.path.join("static", file_path))
    if target and os.path.isfile(target):
        media_type = "text/css" if file_path.endswith(".css") else "application/javascript"
        with open(target, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type=media_type)
    raise HTTPException(status_code=404, detail="Static file not found")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    target = _find_file(os.path.join("templates", "index.html"))
    if target and os.path.isfile(target):
        with open(target, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Jw School</h1><p>Index template not found</p>")


class AssegnazioneModel(BaseModel):
    data: str
    mese: str
    parte_n: str
    tipo: str
    studente: str
    assistente: Optional[str] = ""


class GenerateRequestModel(BaseModel):
    assegnazioni: List[AssegnazioneModel]


@app.post("/api/extract")
async def extract_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Il file caricato deve essere un PDF.")

    contents = await file.read()
    try:
        assegnazioni = extract_assignments_from_pdf(contents)
        return JSONResponse(content={"status": "success", "count": len(assegnazioni), "data": assegnazioni})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la lettura del PDF: {str(e)}")


@app.post("/api/generate")
async def generate_pdf(payload: GenerateRequestModel):
    if not payload.assegnazioni:
        raise HTTPException(status_code=400, detail="Nessuna assegnazione fornita.")

    assegnazioni_dict = [a.dict() for a in payload.assegnazioni]
    pdf_bytes = generate_pdf_bytes(assegnazioni_dict)

    filename = "S-89_compilati.pdf"
    if payload.assegnazioni:
        mese = payload.assegnazioni[0].mese
        filename = f"S-89_{mese}_2026.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/generate-single")
async def generate_single_pdf(assegnazione: AssegnazioneModel):
    pdf_bytes = generate_single_slip_bytes(assegnazione.dict())

    studente_safe = "".join([c if c.isalnum() else "_" for c in assegnazione.studente])
    filename = f"S-89_{studente_safe}_{assegnazione.parte_n}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/generate-zip")
async def generate_zip_pdf(payload: GenerateRequestModel):
    import zipfile
    import io

    if not payload.assegnazioni:
        raise HTTPException(status_code=400, detail="Nessuna assegnazione fornita.")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for a in payload.assegnazioni:
            a_dict = a.dict()
            single_bytes = generate_single_slip_bytes(a_dict)
            studente_safe = "".join([c if c.isalnum() else "_" for c in a.studente])
            if not studente_safe:
                studente_safe = f"Parte_{a.parte_n}"
            data_safe = "".join([c if c.isalnum() else "_" for c in a.data])

            folder = a.mese if a.mese else "Assegnazioni"
            file_name = f"{folder}/{data_safe}_Parte{a.parte_n}_{studente_safe}.pdf"
            zip_file.writestr(file_name, single_bytes)

    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=S-89_Assegnazioni_Singole.zip"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

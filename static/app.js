// Jw School — Frontend App Logic

let assignmentsData = [];
let currentMonthFilter = 'Tutti';

document.addEventListener('DOMContentLoaded', () => {
    initDropzone();
    initEventListeners();
});

function initDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');

    if (dropzone) {
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }
}

function initEventListeners() {
    const btnZip = document.getElementById('btnGenerateZip');
    if (btnZip) btnZip.addEventListener('click', generateZipPdf);

    const btnAll = document.getElementById('btnGenerateAll');
    if (btnAll) btnAll.addEventListener('click', generateFullPdf);

    const btnReset = document.getElementById('btnReset');
    if (btnReset) btnReset.addEventListener('click', resetApp);

    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.addEventListener('input', renderTable);
}

async function handleFileUpload(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('❌ Seleziona un file PDF valido.');
        return;
    }

    showLoader(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            assignmentsData = result.data;
            showToast(`✅ Estratte ${result.count} assegnazioni dal PDF!`);
            buildMonthTabs();
            renderTable();
            showEditor(true);
        } else {
            showToast(`❌ Errore: ${result.detail || 'Impossibile leggere il PDF.'}`);
        }
    } catch (err) {
        showToast(`❌ Si è verificato un errore di connessione: ${err.message}`);
    } finally {
        showLoader(false);
    }
}

function buildMonthTabs() {
    const monthTabsContainer = document.getElementById('monthTabs');
    if (!monthTabsContainer) return;
    monthTabsContainer.innerHTML = '';

    const mesi = ['Tutti', ...new Set(assignmentsData.map(a => a.mese))];

    mesi.forEach(mese => {
        const tab = document.createElement('div');
        tab.className = `month-tab ${mese === currentMonthFilter ? 'active' : ''}`;
        tab.innerText = mese;
        tab.onclick = () => {
            currentMonthFilter = mese;
            document.querySelectorAll('.month-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderTable();
        };
        monthTabsContainer.appendChild(tab);
    });
}

function renderTable() {
    const tableBody = document.getElementById('tableBody');
    if (!tableBody) return;

    const searchInput = document.getElementById('searchInput');
    const searchQuery = searchInput ? searchInput.value.toLowerCase().trim() : '';

    tableBody.innerHTML = '';

    const filtered = assignmentsData.filter(a => {
        const matchesMonth = currentMonthFilter === 'Tutti' || a.mese === currentMonthFilter;
        const matchesSearch = !searchQuery ||
            a.studente.toLowerCase().includes(searchQuery) ||
            (a.assistente && a.assistente.toLowerCase().includes(searchQuery)) ||
            a.data.toLowerCase().includes(searchQuery) ||
            a.tipo.toLowerCase().includes(searchQuery);
        return matchesMonth && matchesSearch;
    });

    if (filtered.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 24px; color: var(--text-muted);">Nessuna assegnazione trovata per i filtri selezionati.</td></tr>`;
        return;
    }

    filtered.forEach((item) => {
        const realIndex = assignmentsData.indexOf(item);
        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td>
                <input type="text" class="cell-input" value="${escapeHtml(item.data)}" onchange="updateItem(${realIndex}, 'data', this.value)">
            </td>
            <td>
                <span class="badge-part">Parte ${escapeHtml(item.parte_n)}</span>
            </td>
            <td>
                <input type="text" class="cell-input" value="${escapeHtml(item.tipo)}" onchange="updateItem(${realIndex}, 'tipo', this.value)">
            </td>
            <td>
                <input type="text" class="cell-input" style="font-weight:600;" value="${escapeHtml(item.studente)}" onchange="updateItem(${realIndex}, 'studente', this.value)">
            </td>
            <td>
                <input type="text" class="cell-input" value="${escapeHtml(item.assistente || '')}" placeholder="Nessun assistente" onchange="updateItem(${realIndex}, 'assistente', this.value)">
            </td>
            <td class="text-center">
                <button class="btn btn-secondary btn-icon" title="Scarica Biglietto Singolo S-89" onclick="generateSinglePdf(${realIndex})">🖨️ Singolo</button>
            </td>
        `;

        tableBody.appendChild(tr);
    });

    const summaryElem = document.getElementById('extractionSummary');
    if (summaryElem) {
        summaryElem.innerText = `Visualizzando ${filtered.length} di ${assignmentsData.length} assegnazioni totali.`;
    }
}

function updateItem(index, key, value) {
    if (assignmentsData[index]) {
        assignmentsData[index][key] = value;
        showToast(`✏️ Aggiornata assegnazione per ${assignmentsData[index].studente || 'lo studente'}`);
    }
}

async function generateFullPdf() {
    if (assignmentsData.length === 0) {
        showToast('⚠️ Nessuna assegnazione disponibile per generare il PDF.');
        return;
    }

    showToast('⏳ Generazione del PDF S-89 in corso...');

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ assegnazioni: assignmentsData })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `S-89_JwSchool_${currentMonthFilter}_2026.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            setTimeout(() => window.URL.revokeObjectURL(url), 1000);
            showToast('✅ PDF scaricato con successo!');
        } else {
            showToast('❌ Errore durante la generazione del PDF.');
        }
    } catch (err) {
        showToast(`❌ Errore: ${err.message}`);
    }
}

async function generateZipPdf() {
    if (assignmentsData.length === 0) {
        showToast('⚠️ Nessuna assegnazione disponibile per il file ZIP.');
        return;
    }

    showToast('⏳ Creazione archivio ZIP con tutte le assegnazioni singole...');

    try {
        const response = await fetch('/api/generate-zip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ assegnazioni: assignmentsData })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `S-89_Singole_JwSchool_${currentMonthFilter}.zip`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            setTimeout(() => window.URL.revokeObjectURL(url), 1000);
            showToast('✅ Archivio ZIP scaricato con successo!');
        } else {
            showToast('❌ Errore durante la creazione del file ZIP.');
        }
    } catch (err) {
        showToast(`❌ Errore: ${err.message}`);
    }
}

async function generateSinglePdf(index) {
    const item = assignmentsData[index];
    if (!item) return;

    showToast(`⏳ Generazione biglietto singolo per ${item.studente}...`);

    try {
        const response = await fetch('/api/generate-single', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const nomeSafe = (item.studente || 'studente').replace(/[^a-zA-Z0-9]/g, '_');
            a.download = `S-89_${nomeSafe}_Parte${item.parte_n}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            setTimeout(() => window.URL.revokeObjectURL(url), 1000);
            showToast('✅ Tagliandino singolo scaricato!');
        } else {
            showToast('❌ Errore nella generazione del biglietto.');
        }
    } catch (err) {
        showToast(`❌ Errore: ${err.message}`);
    }
}

function resetApp() {
    assignmentsData = [];
    currentMonthFilter = 'Tutti';
    const fileInput = document.getElementById('fileInput');
    if (fileInput) fileInput.value = '';
    showEditor(false);
}

function showLoader(show) {
    const loader = document.getElementById('loader');
    if (loader) loader.classList.toggle('hidden', !show);
}

function showEditor(show) {
    const editor = document.getElementById('editorSection');
    if (editor) editor.classList.toggle('hidden', !show);
}

function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.innerText = message;
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3500);
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

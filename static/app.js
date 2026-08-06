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

function calculateStudentFrequencies(data) {
    const freq = {};
    data.forEach(item => {
        const stud = (item.studente || '').trim();
        const ass = (item.assistente || '').trim();

        if (stud) {
            const key = stud.toLowerCase();
            if (!freq[key]) freq[key] = { name: stud, studentCount: 0, assistantCount: 0, studentDates: [], assistantDates: [] };
            freq[key].studentCount++;
            freq[key].studentDates.push(item.data);
        }

        if (ass) {
            const key = ass.toLowerCase();
            if (!freq[key]) freq[key] = { name: ass, studentCount: 0, assistantCount: 0, studentDates: [], assistantDates: [] };
            freq[key].assistantCount++;
            freq[key].assistantDates.push(item.data);
        }
    });
    return freq;
}

function renderTable() {
    const tableBody = document.getElementById('tableBody');
    if (!tableBody) return;

    const searchInput = document.getElementById('searchInput');
    const searchQuery = searchInput ? searchInput.value.toLowerCase().trim() : '';

    tableBody.innerHTML = '';

    const frequencies = calculateStudentFrequencies(assignmentsData);

    const uniqueDates = [...new Set(assignmentsData.map(a => a.data))];
    const dateColorMap = {};
    uniqueDates.forEach((d, idx) => {
        dateColorMap[d] = idx % 5;
    });

    const filtered = assignmentsData.filter(a => {
        const matchesMonth = currentMonthFilter === 'Tutti' || a.mese === currentMonthFilter;
        const matchesSearch = !searchQuery ||
            (a.studente || '').toLowerCase().includes(searchQuery) ||
            (a.assistente || '').toLowerCase().includes(searchQuery) ||
            (a.data || '').toLowerCase().includes(searchQuery) ||
            (a.tipo || '').toLowerCase().includes(searchQuery);
        return matchesMonth && matchesSearch;
    });

    if (filtered.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 24px; color: var(--text-muted);">Nessuna assegnazione trovata per i filtri selezionati.</td></tr>`;
        return;
    }

    let prevDate = null;

    filtered.forEach((item) => {
        const realIndex = assignmentsData.indexOf(item);
        const tr = document.createElement('tr');

        const isNewWeek = prevDate !== null && item.data !== prevDate;
        if (isNewWeek) {
            tr.classList.add('week-divider-row');
        }
        prevDate = item.data;

        if (item.sentWhatsApp || item.sentTelegram) {
            tr.classList.add('row-sent');
        }

        const dateColorIdx = dateColorMap[item.data] !== undefined ? dateColorMap[item.data] : 0;

        const studKey = (item.studente || '').trim().toLowerCase();
        const studStats = frequencies[studKey];
        let studClass = 'cell-input student-input';
        let studBadgeHtml = '';

        if (studStats && studStats.studentCount >= 2) {
            studClass += ' input-repeat-red';
            const datesList = studStats.studentDates.join(', ');
            studBadgeHtml = `<span class="repeat-badge-red" title="Clicca per vedere le adunanze di ${escapeHtml(item.studente)}" onclick="showStudentPopover(event, '${escapeHtml(item.studente)}')">⚠️ ${studStats.studentCount}x</span>`;
        }

        const assKey = (item.assistente || '').trim().toLowerCase();
        const assStats = frequencies[assKey];
        let assClass = 'cell-input assistant-input';
        let assBadgeHtml = '';

        if (assKey && assStats && assStats.studentCount > 0) {
            assClass += ' input-role-mix';
            const studDates = assStats.studentDates.join(', ');
            assBadgeHtml = `<span class="role-badge-mix" title="Clicca per vedere le adunanze di ${escapeHtml(item.assistente)}" onclick="showStudentPopover(event, '${escapeHtml(item.assistente)}')">ℹ️ S+A</span>`;
        }

        const waBtn = item.sentWhatsApp
            ? `<button class="btn btn-primary btn-icon" style="background: #10b981; border-color: #10b981; color: #ffffff; padding: 5px 8px;" title="Promemoria WhatsApp inviato!" onclick="toggleSentStatus(${realIndex}, 'sentWhatsApp')">✅ WA</button>`
            : `<button class="btn btn-primary btn-icon" style="background: #25d366; border-color: #25d366; color: #ffffff; padding: 5px 8px;" title="Invia promemoria via WhatsApp" onclick="sendWhatsApp(${realIndex})">💬 WA</button>`;

        const tgBtn = item.sentTelegram
            ? `<button class="btn btn-primary btn-icon" style="background: #10b981; border-color: #10b981; color: #ffffff; padding: 5px 8px;" title="Promemoria Telegram inviato!" onclick="toggleSentStatus(${realIndex}, 'sentTelegram')">✅ TG</button>`
            : `<button class="btn btn-primary btn-icon" style="background: #0088cc; border-color: #0088cc; color: #ffffff; padding: 5px 8px;" title="Invia promemoria via Telegram" onclick="sendTelegram(${realIndex})">💬 TG</button>`;

        const studFilterBtn = item.studente ? `<button class="btn-filter-name" title="Filtra tutte le parti di ${escapeHtml(item.studente)}" onclick="filterByName('${escapeHtml(item.studente)}')">🔍</button>` : '';
        const assFilterBtn = item.assistente ? `<button class="btn-filter-name" title="Filtra tutte le parti di ${escapeHtml(item.assistente)}" onclick="filterByName('${escapeHtml(item.assistente)}')">🔍</button>` : '';

        tr.innerHTML = `
            <td>
                <div class="cell-input-container">
                    <span class="date-badge date-badge-${dateColorIdx}" title="Badge Settimana">📅</span>
                    <input type="text" class="cell-input" style="font-weight:600;" value="${escapeHtml(item.data)}" onchange="updateItem(${realIndex}, 'data', this.value)">
                </div>
            </td>
            <td class="text-center">
                <span class="badge-part">Parte ${escapeHtml(item.parte_n)}</span>
            </td>
            <td>
                <input type="text" class="cell-input" value="${escapeHtml(item.tipo)}" onchange="updateItem(${realIndex}, 'tipo', this.value)">
            </td>
            <td>
                <div class="cell-input-container">
                    <input type="text" class="${studClass}" style="font-weight:600;" value="${escapeHtml(item.studente)}" onchange="updateItem(${realIndex}, 'studente', this.value)">
                    ${studFilterBtn}
                    ${studBadgeHtml}
                </div>
            </td>
            <td>
                <div class="cell-input-container">
                    <input type="text" class="${assClass}" value="${escapeHtml(item.assistente || '')}" placeholder="Nessun assistente" onchange="updateItem(${realIndex}, 'assistente', this.value)">
                    ${assFilterBtn}
                    ${assBadgeHtml}
                </div>
            </td>
            <td class="text-center">
                <div class="action-buttons-container">
                    <button class="btn btn-secondary btn-icon" style="padding: 5px 8px;" title="Scarica Biglietto Singolo S-89" onclick="generateSinglePdf(${realIndex})">🖨️</button>
                    ${waBtn}
                    ${tgBtn}
                    <button class="btn btn-secondary btn-icon" style="color: #ef4444; border-color: rgba(239, 68, 68, 0.4); padding: 5px 8px;" title="Elimina Assegnazione" onclick="deleteAssignment(${realIndex})">🗑️</button>
                </div>
            </td>
        `;

        tableBody.appendChild(tr);
    });

    const sentCount = assignmentsData.filter(a => a.sentWhatsApp || a.sentTelegram).length;
    const repeatCount = Object.values(frequencies).filter(f => f.studentCount >= 2).length;
    const summaryElem = document.getElementById('extractionSummary');
    if (summaryElem) {
        summaryElem.innerText = `Visualizzando ${filtered.length} di ${assignmentsData.length} assegnazioni totali • Studenti con 2+ parti: ${repeatCount} • Promemoria inviati: ${sentCount} di ${assignmentsData.length}`;
    }
}

function addManualAssignment() {
    showEditor(true);

    let defaultDate = "9 settembre 2026";
    let defaultMonth = "Settembre";
    let defaultParte = "4";

    if (assignmentsData.length > 0) {
        const last = assignmentsData[assignmentsData.length - 1];
        defaultDate = last.data || defaultDate;
        defaultMonth = last.mese || defaultMonth;
        const lastParteNum = parseInt(last.parte_n, 10);
        if (!isNaN(lastParteNum)) {
            defaultParte = String(lastParteNum + 1);
        }
    }

    // Estrai il mese dalla data se disponibile
    if (defaultDate) {
        const parts = defaultDate.split(' ');
        if (parts.length >= 2) {
            defaultMonth = parts[1].charAt(0).toUpperCase() + parts[1].slice(1);
        }
    }

    const newItem = {
        data: defaultDate,
        mese: defaultMonth,
        parte_n: defaultParte,
        tipo: "Iniziare una conversazione (3 min)",
        studente: "",
        assistente: ""
    };

    assignmentsData.push(newItem);
    buildMonthTabs();
    renderTable();
    showToast('➕ Nuova assegnazione aggiunta! Compila i campi nella riga inserita.');
}

function deleteAssignment(index) {
    if (assignmentsData[index]) {
        const removed = assignmentsData.splice(index, 1);
        buildMonthTabs();
        renderTable();
        showToast('🗑️ Assegnazione eliminata');
    }
}

function updateItem(index, key, value) {
    if (assignmentsData[index]) {
        assignmentsData[index][key] = value;
        if (key === 'data') {
            const parts = value.split(' ');
            if (parts.length >= 2) {
                assignmentsData[index].mese = parts[1].charAt(0).toUpperCase() + parts[1].slice(1);
            }
        }
        showToast(`✏️ Aggiornata assegnazione per ${assignmentsData[index].studente || 'lo studente'}`);
        if (key === 'studente' || key === 'assistente' || key === 'data') {
            buildMonthTabs();
            renderTable();
        }
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

function sendWhatsApp(index) {
    const item = assignmentsData[index];
    if (!item) return;

    item.sentWhatsApp = true;
    renderTable();
    showToast(`✅ Promemoria WhatsApp inviato a ${item.studente || 'lo studente'}`);

    let msg = `Ciao ${item.studente || ''}, ti ricordo la tua assegnazione per l'adunanza del ${item.data}:\n\n` +
              `• Parte n. ${item.parte_n}: ${item.tipo}`;

    if (item.assistente && item.assistente.trim()) {
        msg += `\n• Assistente: ${item.assistente}`;
    }

    msg += `\n\nBuon lavoro!`;

    const encodedMsg = encodeURIComponent(msg);
    const whatsappUrl = `https://api.whatsapp.com/send?text=${encodedMsg}`;
    window.open(whatsappUrl, '_blank');
}

function sendTelegram(index) {
    const item = assignmentsData[index];
    if (!item) return;

    item.sentTelegram = true;
    renderTable();
    showToast(`✅ Promemoria Telegram inviato a ${item.studente || 'lo studente'}`);

    let msg = `Ciao ${item.studente || ''}, ti ricordo la tua assegnazione per l'adunanza del ${item.data}:\n\n` +
              `• Parte n. ${item.parte_n}: ${item.tipo}`;

    if (item.assistente && item.assistente.trim()) {
        msg += `\n• Assistente: ${item.assistente}`;
    }

    msg += `\n\nBuon lavoro!`;

    const encodedMsg = encodeURIComponent(msg);
    const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    if (isMobile) {
        window.location.href = `tg://msg?text=${encodedMsg}`;
    } else {
        const telegramUrl = `https://t.me/share/url?url=&text=${encodedMsg}`;
        window.open(telegramUrl, '_blank');
    }
}

function toggleSentStatus(index, key) {
    const item = assignmentsData[index];
    if (!item) return;

    item[key] = !item[key];
    renderTable();
    const statusText = item[key] ? 'marca come inviato' : 'ripristinato come da inviare';
    showToast(`🔄 Stato promemoria per ${item.studente}: ${statusText}`);
}

function openPrivacyModal(event) {
    if (event) event.preventDefault();
    const modal = document.getElementById('privacyModal');
    if (modal) modal.classList.remove('hidden');
}

function closePrivacyModal() {
    const modal = document.getElementById('privacyModal');
    if (modal) modal.classList.add('hidden');
}

function closePrivacyModalOnOverlay(event) {
    if (event.target.id === 'privacyModal') {
        closePrivacyModal();
    }
}

function openHelpModal(event) {
    if (event) event.preventDefault();
    const modal = document.getElementById('helpModal');
    if (modal) modal.classList.remove('hidden');
}

function closeHelpModal() {
    const modal = document.getElementById('helpModal');
    if (modal) modal.classList.add('hidden');
}

function closeHelpModalOnOverlay(event) {
    if (event.target.id === 'helpModal') {
        closeHelpModal();
    }
}

/* Popover Dettaglio Partecipazioni Studente */
function showStudentPopover(event, name) {
    if (event) event.stopPropagation();
    closeStudentPopover();

    if (!name || !name.trim()) return;
    const key = name.trim().toLowerCase();
    const frequencies = calculateStudentFrequencies(assignmentsData);
    const stats = frequencies[key];

    if (!stats) return;

    const list = [];
    assignmentsData.forEach(item => {
        if ((item.studente || '').trim().toLowerCase() === key) {
            list.push({ data: item.data, parte: item.parte_n, tipo: item.tipo, role: 'Studente' });
        }
        if ((item.assistente || '').trim().toLowerCase() === key) {
            list.push({ data: item.data, parte: item.parte_n, tipo: item.tipo, role: 'Assistente' });
        }
    });

    const popover = document.createElement('div');
    popover.id = 'studentPopover';
    popover.className = 'student-popover';

    const itemsHtml = list.map(entry => `
        <li class="student-popover-item">
            <div>
                <strong>📅 ${escapeHtml(entry.data)}</strong> &bull; Parte ${escapeHtml(entry.parte)}
                <div style="font-size: 11px; color: var(--text-body); margin-top: 2px;">${escapeHtml(entry.tipo)}</div>
            </div>
            <span class="badge-role-tag ${entry.role === 'Studente' ? 'tag-student' : 'tag-assistant'}">${entry.role}</span>
        </li>
    `).join('');

    const safeName = escapeHtml(name).replace(/'/g, "\\'");

    popover.innerHTML = `
        <div class="student-popover-header">
            <div>
                <strong>👤 ${escapeHtml(name)}</strong>
                <div style="font-size: 11px; color: var(--text-body); margin-top: 2px;">
                    ${stats.studentCount}x Studente &bull; ${stats.assistantCount}x Assistente
                </div>
            </div>
            <button class="student-popover-close" onclick="closeStudentPopover()">&times;</button>
        </div>
        <ul class="student-popover-list">
            ${itemsHtml}
        </ul>
        <div style="margin-top: 12px; text-align: right;">
            <button class="btn btn-secondary" style="font-size: 11px; padding: 4px 10px;" onclick="filterByName('${safeName}'); closeStudentPopover();">🔍 Filtra nella tabella</button>
        </div>
    `;

    document.body.appendChild(popover);

    const rect = event.currentTarget.getBoundingClientRect();
    const popoverWidth = 320;
    const popoverHeight = popover.offsetHeight || 220;

    let left = rect.left;
    let top = rect.bottom + 6;

    // Se il popover va oltre il bordo inferiore dello schermo, posizionalo SOPRA il badge
    if (rect.bottom + popoverHeight + 10 > window.innerHeight) {
        top = rect.top - popoverHeight - 6;
    }

    if (left + popoverWidth > window.innerWidth - 20) {
        left = window.innerWidth - popoverWidth - 20;
    }

    popover.style.position = 'fixed';
    popover.style.left = `${Math.max(10, left)}px`;
    popover.style.top = `${Math.max(10, top)}px`;
}

function closeStudentPopover() {
    const existing = document.getElementById('studentPopover');
    if (existing) existing.remove();
}

function filterByName(name) {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.value = name;
        renderTable();
        showToast(`🔍 Filtrate assegnazioni per: ${name}`);
    }
}

document.addEventListener('click', (e) => {
    if (!e.target.closest('#studentPopover') && !e.target.closest('.repeat-badge-red') && !e.target.closest('.role-badge-mix')) {
        closeStudentPopover();
    }
});


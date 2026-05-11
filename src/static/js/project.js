// Patent drafting assistant - project workspace

const projectId = document.querySelector('.workspace')?.dataset.projectId;
let currentChapter = null;
let chapters = [];
let projectInfo = null;  // full project data with concept

// === Initialization ===
document.addEventListener('DOMContentLoaded', async () => {
    if (!projectId) return;
    await loadProjectInfo();
    await loadChapters();
    await loadFigures();
    showConceptPanel();
});

// === Load Project Info ===
async function loadProjectInfo() {
    try {
        projectInfo = await api.get(`/api/projects/${projectId}`);
        document.getElementById('concept-text').value = projectInfo.technical_concept || '';
        document.getElementById('concept-title').value = projectInfo.title || '';
        document.querySelector('.nav-logo').textContent = '📄 ' + (projectInfo.title || '未命名项目');
    } catch (e) {
        showToast('加载项目信息失败: ' + e.message, 'error');
    }
}

// === Panel Switching ===
function showConceptPanel() {
    currentChapter = null;
    document.getElementById('concept-panel').style.display = 'block';
    document.getElementById('chapter-editor').style.display = 'none';
    renderChapterNav(chapters);
}

function backToConcept() {
    showConceptPanel();
}

function showChapterEditor(ch) {
    currentChapter = ch;
    document.getElementById('concept-panel').style.display = 'none';
    document.getElementById('chapter-editor').style.display = 'flex';
    document.getElementById('editor-chapter-title').textContent = `${ch.chapter_order}. ${ch.chapter_name}`;
    document.getElementById('editor-chapter-status').className = `badge badge-${ch.status}`;
    document.getElementById('editor-chapter-status').textContent = statusLabel(ch.status);
    document.getElementById('editor-textarea').value = ch.content || '';
    document.getElementById('editor-preview').style.display = 'none';
    document.getElementById('editor-textarea').style.display = 'block';
    document.getElementById('btn-preview').textContent = '👁 预览';

    // Wire up buttons
    document.getElementById('btn-generate-chapter').onclick = () => generateChapter(ch.id);
    document.getElementById('btn-preview').onclick = togglePreview;
    document.getElementById('btn-save').onclick = saveChapter;

    const btnVer = document.getElementById('btn-version');
    if (ch.versions && ch.versions.length) {
        btnVer.style.display = '';
        btnVer.textContent = `🕐 历史版本 (${ch.versions.length})`;
        btnVer.onclick = showVersions;
    } else {
        btnVer.style.display = 'none';
    }

    renderChapterNav(chapters);
}

// === Concept Management ===
async function saveConcept() {
    const title = document.getElementById('concept-title').value.trim();
    const concept = document.getElementById('concept-text').value.trim();

    if (concept.length < 10) {
        showToast('请至少输入10个字符描述您的核心技术构思', 'error');
        document.getElementById('concept-text').focus();
        return;
    }

    try {
        const updated = await api.put(`/api/projects/${projectId}`, {
            title: title || undefined,
            technical_concept: concept,
        });
        projectInfo = updated;
        document.querySelector('.nav-logo').textContent = '📄 ' + (updated.title || '未命名项目');
        showToast('核心技术构思已保存，可以开始撰写', 'success');
    } catch (e) {
        showToast('保存失败: ' + e.message, 'error');
    }
}

async function analyzeConcept() {
    // Save first
    await saveConcept();

    const resultDiv = document.getElementById('concept-analysis-result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div class="loading">正在分析技术特征...</div>';

    try {
        const analysis = await api.post(`/api/projects/${projectId}/generate/analyze`);
        resultDiv.innerHTML = `
            <h3>📊 技术特征分析结果</h3>
            <div class="analysis-grid">
                <div class="analysis-item">
                    <strong>核心发明构思</strong>
                    <p>${escapeHtml(analysis.core_inventive_concept || '—')}</p>
                </div>
                <div class="analysis-item">
                    <strong>要解决的技术问题</strong>
                    <p>${escapeHtml(analysis.technical_problem || '—')}</p>
                </div>
                <div class="analysis-item">
                    <strong>关键构件</strong>
                    <p>${(analysis.key_components || []).map(escapeHtml).join('、') || '—'}</p>
                </div>
                <div class="analysis-item">
                    <strong>连接方式</strong>
                    <p>${(analysis.connection_types || []).map(escapeHtml).join('、') || '—'}</p>
                </div>
                <div class="analysis-item">
                    <strong>创新点</strong>
                    <p>${(analysis.novel_features || []).map(escapeHtml).join('；') || '—'}</p>
                </div>
                <div class="analysis-item">
                    <strong>预期技术效果</strong>
                    <p>${(analysis.technical_effects || []).map(escapeHtml).join('；') || '—'}</p>
                </div>
            </div>
        `;
        showToast('技术特征分析完成', 'success');
    } catch (e) {
        resultDiv.innerHTML = `<div class="error">分析失败: ${e.message}</div>`;
    }
}

// === Chapter Navigation ===
async function loadChapters() {
    try {
        const resp = await api.get(`/api/projects/${projectId}/chapters`);
        chapters = resp;
        renderChapterNav(resp);
    } catch (e) {
        document.getElementById('chapter-nav').innerHTML = `<div class="error">加载失败: ${e.message}</div>`;
    }
}

function renderChapterNav(chapters) {
    const nav = document.getElementById('chapter-nav');
    nav.innerHTML = chapters.map(ch => `
        <div class="chapter-item ${currentChapter?.id === ch.id ? 'active' : ''}"
             onclick="selectChapter(${ch.id})">
            <span class="chapter-order">${ch.chapter_order}</span>
            <div class="chapter-info">
                <div class="chapter-name">${escapeHtml(ch.chapter_name)}</div>
                <div class="chapter-status">
                    <span class="badge badge-${ch.status}">${statusLabel(ch.status)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// === Chapter Selection ===
async function selectChapter(chapterId) {
    try {
        const ch = await api.get(`/api/projects/${projectId}/chapters/${chapterId}`);
        showChapterEditor(ch);
    } catch (e) {
        showToast('加载章节失败: ' + e.message, 'error');
    }
}

// === Save Chapter ===
const saveChapter = debounce(async () => {
    if (!currentChapter) return;
    const textarea = document.getElementById('editor-textarea');
    if (!textarea) return;

    try {
        const ch = await api.put(
            `/api/projects/${projectId}/chapters/${currentChapter.id}`,
            { content: textarea.value }
        );
        currentChapter = ch;
        const idx = chapters.findIndex(c => c.id === ch.id);
        if (idx >= 0) {
            chapters[idx] = ch;
            renderChapterNav(chapters);
        }
        document.getElementById('editor-chapter-status').className = `badge badge-${ch.status}`;
        document.getElementById('editor-chapter-status').textContent = statusLabel(ch.status);
        showToast('保存成功', 'success');
    } catch (e) {
        showToast('保存失败: ' + e.message, 'error');
    }
}, 800);

function togglePreview() {
    const preview = document.getElementById('editor-preview');
    const textarea = document.getElementById('editor-textarea');
    if (preview && textarea) {
        const show = preview.style.display === 'none';
        preview.style.display = show ? 'block' : 'none';
        textarea.style.display = show ? 'none' : 'block';
        document.getElementById('btn-preview').textContent = show ? '📝 编辑' : '👁 预览';
        if (show) {
            const figures = (currentChapter?.figure_placeholders || []).map(f =>
                `<div class="figure-marker">[${f.position_label}] ${escapeHtml(f.description)}</div>`
            ).join('');
            preview.innerHTML = renderMarkdown(textarea.value) + (figures ? `<div class="figure-markers">${figures}</div>` : '');
        }
    }
}

// === AI Generation ===
async function generateChapter(chapterId) {
    // Ensure concept is saved
    const concept = document.getElementById('concept-text').value.trim();
    if (concept.length < 10) {
        showToast('请先在核心技术构思中输入足够的技术描述', 'error');
        showConceptPanel();
        document.getElementById('concept-text').focus();
        return;
    }
    await saveConcept();

    const overlay = document.getElementById('streaming-overlay');
    const title = document.getElementById('streaming-title');
    const output = document.getElementById('streaming-output');

    const ch = chapters.find(c => c.id === chapterId);
    title.textContent = `基于核心技术构思，正在生成: ${ch?.chapter_name || ''}`;
    output.textContent = '';
    overlay.style.display = 'flex';

    try {
        const resp = await fetch(`/api/projects/${projectId}/generate/chapter/${chapterId}/stream`, { method: 'POST' });
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullContent = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';
            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.token) {
                        fullContent += data.token;
                        output.textContent = fullContent;
                        output.scrollTop = output.scrollHeight;
                    }
                    if (data.done) {
                        title.textContent = '✅ 生成完成';
                        setTimeout(async () => {
                            overlay.style.display = 'none';
                            await loadChapters();
                            await selectChapter(chapterId);
                            await loadFigures();
                        }, 1500);
                    }
                    if (data.error) {
                        title.textContent = '❌ ' + data.error;
                    }
                } catch (e) { /* skip */ }
            }
        }
    } catch (e) {
        title.textContent = '❌ 生成失败: ' + e.message;
        setTimeout(() => { overlay.style.display = 'none'; }, 3000);
    }
}

async function generateAll() {
    // Ensure concept exists
    const concept = document.getElementById('concept-text').value.trim();
    if (concept.length < 10) {
        showToast('请先输入关键核心技术构思（至少10个字符）', 'error');
        showConceptPanel();
        document.getElementById('concept-text').focus();
        return;
    }
    await saveConcept();

    const overlay = document.getElementById('streaming-overlay');
    const title = document.getElementById('streaming-title');
    const output = document.getElementById('streaming-output');

    title.textContent = '基于核心技术构思，正在生成全部章节...';
    output.textContent = '';
    overlay.style.display = 'flex';

    try {
        const resp = await fetch(`/api/projects/${projectId}/generate/all`, { method: 'POST' });
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let currentChapterName = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';
            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.chapter_name && data.status === 'generating') {
                        currentChapterName = data.chapter_name;
                        title.textContent = `正在生成: ${currentChapterName}`;
                        output.textContent += `\n\n### ${currentChapterName}\n\n`;
                    }
                    if (data.token) {
                        output.textContent += data.token;
                        output.scrollTop = output.scrollHeight;
                    }
                    if (data.done) {
                        output.textContent += `\n\n✅ ${currentChapterName} 完成\n`;
                    }
                    if (data.all_done) {
                        title.textContent = '✅ 全部章节生成完成';
                        setTimeout(async () => {
                            overlay.style.display = 'none';
                            await loadChapters();
                            await loadFigures();
                        }, 1500);
                    }
                    if (data.error) {
                        output.textContent += `\n❌ 错误: ${data.error}\n`;
                    }
                } catch (e) { /* skip */ }
            }
        }
    } catch (e) {
        title.textContent = '❌ 生成失败: ' + e.message;
        setTimeout(() => { overlay.style.display = 'none'; }, 3000);
    }
}

// === Version History ===
async function showVersions() {
    if (!currentChapter || !currentChapter.versions || !currentChapter.versions.length) {
        showToast('暂无历史版本', 'info');
        return;
    }
    const latest = currentChapter.versions[0];
    if (confirm(`恢复到版本 ${latest.version_number}？当前内容将被保存为历史版本。`)) {
        try {
            const ch = await api.post(
                `/api/projects/${projectId}/chapters/${currentChapter.id}/versions/${latest.id}/restore`
            );
            currentChapter = ch;
            document.getElementById('editor-textarea').value = ch.content;
            showToast('已恢复历史版本', 'success');
        } catch (e) {
            showToast('恢复失败: ' + e.message, 'error');
        }
    }
}

// === Figure Panel ===
async function loadFigures() {
    try {
        const figures = await api.get(`/api/projects/${projectId}/figures`);
        const list = document.getElementById('figure-list');
        const count = document.getElementById('figure-count');
        count.textContent = figures.length;
        if (!figures.length) {
            list.innerHTML = '<p class="hint">生成章节后，附图标记将自动显示在此处</p>';
            return;
        }
        list.innerHTML = figures.map(f => `
            <div class="figure-item">
                <div class="figure-number">${escapeHtml(f.position_label)}</div>
                <div class="figure-desc">${escapeHtml(f.description)}</div>
                <div class="figure-chapter">类型: ${escapeHtml(f.content_type)}</div>
            </div>
        `).join('');
    } catch (e) { /* silent */ }
}

// === Export ===
async function exportDocx() {
    try {
        const resp = await api.post(`/api/projects/${projectId}/export/docx`);
        if (resp.filename) {
            window.open(`/api/projects/${projectId}/export/download/${resp.filename}`, '_blank');
            showToast('DOCX 导出成功', 'success');
        }
    } catch (e) {
        try {
            const resp = await api.get(`/api/projects/${projectId}/export/docx`);
            if (resp.filename) {
                window.open(`/api/projects/${projectId}/export/download/${resp.filename}`, '_blank');
                showToast('DOCX 导出成功', 'success');
            }
        } catch (e2) {
            showToast('导出失败: ' + e2.message, 'error');
        }
    }
}

async function exportMarkdown() {
    try {
        const resp = await api.post(`/api/projects/${projectId}/export/markdown`);
        if (resp.filename) {
            window.open(`/api/projects/${projectId}/export/download/${resp.filename}`, '_blank');
            showToast('Markdown 导出成功', 'success');
        }
    } catch (e) {
        showToast('导出失败: ' + e.message, 'error');
    }
}

// === Simple Markdown Render ===
function renderMarkdown(md) {
    if (!md) return '';
    let html = md
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/^(\d+)[\.\)] (.+)$/gm, '<li>$2</li>')
        .replace(/\[插入图(\d+)[：:]\s*([^\]]+)\]/g, '<div class="figure-marker">[图$1] $2</div>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    return '<p>' + html + '</p>';
}

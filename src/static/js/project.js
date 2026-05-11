// Patent drafting assistant - project workspace

const projectId = document.querySelector('.workspace')?.dataset.projectId;
let currentChapter = null;
let chapters = [];

// === Initialization ===
document.addEventListener('DOMContentLoaded', async () => {
    if (!projectId) return;
    await loadChapters();
    await loadFigures();
});

// === Chapter Navigation ===
async function loadChapters() {
    try {
        const data = await api.get(`/api/projects/${projectId}`);
        document.querySelector('.nav-logo').textContent = '📄 ' + (data.title || '未命名项目');

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

function statusLabel(s) {
    const map = { pending: '待生成', ai_generated: 'AI生成', user_edited: '已编辑', finalized: '已定稿' };
    return map[s] || s;
}

// === Chapter Selection & Editor ===
async function selectChapter(chapterId) {
    try {
        const ch = await api.get(`/api/projects/${projectId}/chapters/${chapterId}`);
        currentChapter = ch;
        renderChapterNav(chapters);
        renderEditor(ch);
    } catch (e) {
        showToast('加载章节失败: ' + e.message, 'error');
    }
}

function renderEditor(ch) {
    const panel = document.getElementById('editor-panel');
    const figures = (ch.figure_placeholders || []).map((f, i) =>
        `<div class="figure-marker">[${f.position_label}] ${escapeHtml(f.description)}</div>`
    ).join('');

    panel.innerHTML = `
        <div class="editor-toolbar">
            <h3>${ch.chapter_order}. ${escapeHtml(ch.chapter_name)}</h3>
            <span class="badge badge-${ch.status}">${statusLabel(ch.status)}</span>
            <button class="btn btn-outline btn-sm" onclick="generateChapter(${ch.id})">🤖 AI生成</button>
            <button class="btn btn-secondary btn-sm" onclick="togglePreview()">👁 预览</button>
            <button class="btn btn-primary btn-sm" onclick="saveChapter()">💾 保存</button>
            ${ch.versions?.length ? `<button class="btn btn-secondary btn-sm" onclick="showVersions()">🕐 历史版本 (${ch.versions.length})</button>` : ''}
        </div>
        <div class="editor-body">
            <textarea class="editor-textarea" id="editor-textarea"
                placeholder="请在此编辑章节内容，或点击「AI生成」自动撰写...">${ch.content || ''}</textarea>
            <div class="editor-preview" id="editor-preview" style="display:none">
                ${ch.content ? renderMarkdown(ch.content) : '<p>暂无内容</p>'}
                ${figures ? `<div class="figure-markers">${figures}</div>` : ''}
            </div>
        </div>
    `;
}

function togglePreview() {
    const preview = document.getElementById('editor-preview');
    const textarea = document.getElementById('editor-textarea');
    if (preview && textarea) {
        const show = preview.style.display === 'none';
        preview.style.display = show ? 'block' : 'none';
        textarea.style.display = show ? 'none' : 'block';
        if (show) {
            const figures = (currentChapter?.figure_placeholders || []).map((f, i) =>
                `<div class="figure-marker">[${f.position_label}] ${escapeHtml(f.description)}</div>`
            ).join('');
            preview.innerHTML = renderMarkdown(textarea.value) + (figures ? `<div class="figure-markers">${figures}</div>` : '');
        }
    }
}

// === Simple Markdown Renderer ===
function renderMarkdown(md) {
    if (!md) return '';
    let html = md
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        // Headings
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        // Bold and italic
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // Lists
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/^(\d+)[\.\)] (.+)$/gm, '<li>$2</li>')
        // Figure markers
        .replace(/\[插入图(\d+)[：:]\s*([^\]]+)\]/g, '<div class="figure-marker">[图$1] $2</div>')
        // Paragraphs
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');

    html = '<p>' + html + '</p>';
    return html;
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
        // Refresh the chapter in the list
        const idx = chapters.findIndex(c => c.id === ch.id);
        if (idx >= 0) {
            chapters[idx] = ch;
            renderChapterNav(chapters);
        }
        showToast('保存成功', 'success');
    } catch (e) {
        showToast('保存失败: ' + e.message, 'error');
    }
}, 800);

// === AI Generation ===
async function generateChapter(chapterId) {
    const overlay = document.getElementById('streaming-overlay');
    const title = document.getElementById('streaming-title');
    const output = document.getElementById('streaming-output');

    const ch = chapters.find(c => c.id === chapterId);
    title.textContent = `正在生成: ${ch?.chapter_name || ''}`;
    output.textContent = '';
    overlay.style.display = 'flex';

    try {
        const resp = await fetch(`/api/projects/${projectId}/generate/chapter/${chapterId}/stream`, {
            method: 'POST',
        });

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
                } catch (e) { /* parse error, skip */ }
            }
        }
    } catch (e) {
        title.textContent = '❌ 生成失败: ' + e.message;
        setTimeout(() => { overlay.style.display = 'none'; }, 3000);
    }
}

async function generateAll() {
    const overlay = document.getElementById('streaming-overlay');
    const title = document.getElementById('streaming-title');
    const output = document.getElementById('streaming-output');

    title.textContent = '正在生成全部章节...';
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
    // Simple: restore latest version
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
    } catch (e) {
        // silently fail for figure panel
    }
}

// === Export ===
async function exportDocx() {
    try {
        const resp = await api.get(`/api/projects/${projectId}/export/docx`);
        if (resp.filepath) {
            const finalUrl = `/api/projects/${projectId}/export/download/${resp.filename}`;
            window.open(finalUrl, '_blank');
            showToast('DOCX 导出成功', 'success');
        }
    } catch (e) {
        // Try POST instead
        try {
            const resp = await api.post(`/api/projects/${projectId}/export/docx`);
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


// Shared utility functions

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function statusLabel(s) {
    const map = {
        drafting: '起草中', reviewing: '审核中', completed: '已完成',
        pending: '待生成', ai_generated: 'AI生成', user_edited: '已编辑', finalized: '已定稿'
    };
    return map[s] || s;
}

function formatDate(d) {
    if (!d) return '';
    return new Date(d).toLocaleString('zh-CN');
}

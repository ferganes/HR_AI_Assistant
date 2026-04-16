const input = document.getElementById('questionInput');
const messages = document.getElementById('messages');
const btn = document.getElementById('sendBtn');

input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') send();
});

async function send() {
    const question = input.value.trim();
    if (!question) return;

    // Убрать empty state
    if (messages.querySelector('.empty')) {
        messages.innerHTML = '';
    }

    // Добавить вопрос (здесь экранирование нужно — пользовательский ввод)
    addMessage(question, 'user', true);
    input.value = '';
    btn.disabled = true;

    // Показать "печатает..."
    const loadingId = addLoading();

    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        if (!response.ok) throw new Error('Ошибка сервера');

        const data = await response.json();
        removeMessage(loadingId);

        // Форматируем ответ: заменяем \n на <br> без экранирования
        const formattedAnswer = data.answer.replace(/\n/g, '<br>');
        let html = formattedAnswer;
        if (data.source) {
            html += `<div class="source">📄 ${escapeHtml(data.source)}</div>`;
        }

        addMessage(html, 'bot', true);

    } catch (err) {
        removeMessage(loadingId);
        addMessage('❌ Ошибка: ' + err.message, 'bot', true);
    } finally {
        btn.disabled = false;
        input.focus();
    }
}

function addMessage(text, type, isHtml = false) {
    const div = document.createElement('div');
    div.className = 'message ' + type;
    div.innerHTML = text;  // Всегда innerHTML, т.к. доверяем источнику
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
}

function addLoading() {
    const id = 'load-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message bot';
    div.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

input.focus();
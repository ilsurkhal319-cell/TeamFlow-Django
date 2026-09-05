// ============================================================
// Модалка создания доски - TeamFlow
// ============================================================

// Выбранный цвет доски
let selectedBoardColor = 'violet';

// Открыть модалку создания доски
function openBoardModal() {
    // Сбрасываем форму
    document.getElementById('boardTitle').value = '';
    document.getElementById('boardDescription').value = '';
    var workspaceSelect = document.getElementById('boardWorkspace');
    var activeWorkspace = new URLSearchParams(window.location.search).get('workspace') || workspaceSelect.options[0]?.value;
    workspaceSelect.value = workspaceSelect.querySelector('option[value="' + activeWorkspace + '"]') ? activeWorkspace : workspaceSelect.options[0]?.value;

    // Сбрасываем ошибку
    document.getElementById('boardTitle').classList.remove('border-red-500');
    document.getElementById('boardTitleError').classList.add('hidden');

    // Сбрасываем цвет
    selectedBoardColor = 'violet';
    updateBoardColorButtons();

    // Показываем модалку
    document.getElementById('boardModal').classList.remove('hidden');

    // Фокус на поле названия
    setTimeout(function() {
        document.getElementById('boardTitle').focus();
    }, 100);
}

// Закрыть модалку создания доски
function closeBoardModal() {
    document.getElementById('boardModal').classList.add('hidden');
}

// Выбрать цвет доски
function selectBoardColor(btn, color) {
    selectedBoardColor = color;
    updateBoardColorButtons();

    // Обновляем цвет полосы
    var colorMap = {
        violet: 'bg-violet-600',
        pink: 'bg-pink-500',
        cyan: 'bg-cyan-500',
        blue: 'bg-blue-600',
        orange: 'bg-orange-500',
        red: 'bg-red-500',
        emerald: 'bg-emerald-500',
        zinc: 'bg-zinc-600'
    };
    var stripe = document.getElementById('boardColorStripe');
    stripe.className = 'h-[10px] transition-colors ' + colorMap[color];
}

// Обновить вид кнопок цвета
function updateBoardColorButtons() {
    var buttons = document.querySelectorAll('.color-btn');
    buttons.forEach(function(btn) {
        if (btn.dataset.color === selectedBoardColor) {
            btn.classList.add('ring-white');
            btn.classList.remove('ring-transparent');
        } else {
            btn.classList.remove('ring-white');
            btn.classList.add('ring-transparent');
        }
    });
}

// Создать доску
function createBoard() {
    var title = document.getElementById('boardTitle').value.trim();

    if (!title) {
        // Показываем ошибку с анимацией
        var input = document.getElementById('boardTitle');
        var error = document.getElementById('boardTitleError');

        input.classList.add('border-red-500');
        error.classList.remove('hidden');

        // Анимация тряски
        input.classList.add('animate-shake');
        setTimeout(function() {
            input.classList.remove('animate-shake');
        }, 500);

        input.focus();
        return;
    }

    var description = document.getElementById('boardDescription').value.trim();
    var workspace = document.getElementById('boardWorkspace').value;

    // Отправка данных на сервер
    var csrfToken = getCookie('csrftoken') || '';

    fetch('/api/board/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            title: title,
            description: description,
            color: selectedBoardColor,
            workspace: workspace
        })
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            closeBoardModal();
            showNotification('Доска "' + title + '" создана');
            // Перезагрузка страницы для обновления списка
            setTimeout(function() {
                window.location.reload();
            }, 1000);
        } else {
            showNotification('Ошибка: ' + (data.error || 'Не удалось создать доску'), true);
        }
    })
    .catch(function(error) {
        console.error('Fetch error:', error);
        showNotification('Ошибка при создании доски', true);
    });
}

// Получить CSRF токен
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Показать уведомление
function showNotification(message, isError) {
    var notification = document.createElement('div');
    var iconColor = isError ? 'text-red-400' : 'text-emerald-400';
    var icon = isError
        ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>'
        : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>';
    notification.className = 'fixed bottom-6 right-6 bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 shadow-2xl z-[200] flex items-center gap-2 animate-notification-in';
    notification.innerHTML = '<svg class="w-5 h-5 ' + iconColor + '" fill="none" stroke="currentColor" viewBox="0 0 24 24">' + icon + '</svg><span class="text-sm text-zinc-100">' + message + '</span>';
    document.body.appendChild(notification);

    setTimeout(function() {
        notification.classList.add('opacity-0', 'translate-y-2');
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 3000);
}

// Подтверждение удаления доски
function confirmDeleteBoard(event, boardId, boardTitle) {
    event.preventDefault();
    event.stopPropagation();

    if (confirm('Вы уверены, что хотите удалить доску "' + boardTitle + '"? Все задачи и колонки будут удалены безвозвратно.')) {
        deleteBoard(boardId);
    }
}

// Удаление доски
function deleteBoard(boardId) {
    var csrfToken = getCookie('csrftoken') || '';

    fetch('/api/board/delete/' + boardId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            // Находим карточку доски
            var boardCard = document.querySelector('.board-card[data-board-id="' + boardId + '"]');
            if (boardCard) {
                // Анимация исчезновения
                boardCard.style.transition = 'all 0.3s ease';
                boardCard.style.opacity = '0';
                boardCard.style.transform = 'scale(0.9)';

                setTimeout(function() {
                    boardCard.remove();
                    // Если карточек не осталось - перезагрузим страницу
                    var remainingCards = document.querySelectorAll('.board-card');
                    if (remainingCards.length === 0) {
                        window.location.reload();
                    }
                }, 300);
            }
            showNotification(data.message || 'Доска удалена');
        } else {
            showNotification('Ошибка: ' + (data.error || 'Не удалось удалить доску'), true);
        }
    })
    .catch(function(error) {
        console.error('Delete error:', error);
        showNotification('Ошибка при удалении доски', true);
    });
}

// Переключение избранного
function toggleFavorite(boardId) {
    var csrfToken = getCookie('csrftoken') || '';

    fetch('/api/board/favorite/' + boardId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            showNotification(data.message);
            // Перезагрузим страницу для обновления состояния звездочки
            setTimeout(function() {
                window.location.reload();
            }, 500);
        } else {
            showNotification('Ошибка: ' + (data.error || 'Не удалось добавить в избранное'), true);
        }
    })
    .catch(function(error) {
        console.error('Favorite error:', error);
        showNotification('Ошибка при добавлении в избранное', true);
    });
}

function toggleArchive(boardId) {
    var csrfToken = getCookie('csrftoken') || '';

    fetch('/api/board/archive/' + boardId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            showNotification(data.message);
            setTimeout(function() {
                window.location.reload();
            }, 500);
        } else {
            showNotification('Ошибка: ' + (data.error || 'Не удалось архивировать'), true);
        }
    })
    .catch(function(error) {
        console.error('Archive error:', error);
        showNotification('Ошибка при архивировании', true);
    });
}

// Закрытие по Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeBoardModal();
    }
});
        // Подсветка активного пункта меню
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const sidebarItems = document.querySelectorAll('.sidebar-item');

    sidebarItems.forEach(item => {
        const page = item.getAttribute('data-page');
        if (page === 'home' && (currentPath === '/' || currentPath === '/home/')) {
            item.classList.add('active');
        } else if (page === 'dashboard' && currentPath.includes('dashboard')) {
            item.classList.add('active');
        } else if (page === 'favorites' && currentPath.includes('favorites')) {
            item.classList.add('active');
        } else if (page === 'archive' && currentPath.includes('archive')) {
            item.classList.add('active');
        }
    });
});

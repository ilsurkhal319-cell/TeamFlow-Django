// ============================================================
// Drag & Drop функциональность для доски задач TeamFlow
// ============================================================

// Получаем все карточки задач и зоны для Drop
const taskCards = document.querySelectorAll('.task-card');
const dropZones = document.querySelectorAll('.drop-zone');

const taskSearch = document.getElementById('taskSearch');
if (taskSearch) {
    taskSearch.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        document.querySelectorAll('.task-card').forEach(card => {
            card.classList.toggle('hidden', !card.textContent.toLowerCase().includes(query));
        });
    });
}

// Переменная для хранения перетаскиваемой карточки
let draggedCard = null;

// Генерируем уникальный ID для новых задач
let taskIdCounter = 100;

// Текущая зона для добавления задачи
let currentDropZone = null;

// Выбранный приоритет по умолчанию
let selectedPriority = 'medium';

// ============================================================
// Инициализация Drag & Drop
// ============================================================

// Добавляем обработчики событий к карточкам задач
taskCards.forEach(card => {
    card.addEventListener('dragstart', handleDragStart);
    card.addEventListener('dragend', handleDragEnd);
});
// Добавляем обработчики событий к зонам Drop
dropZones.forEach(zone => {
    zone.addEventListener('dragover', handleDragOver);
    zone.addEventListener('dragenter', handleDragEnter);
    zone.addEventListener('dragleave', handleDragLeave);
    zone.addEventListener('drop', handleDrop);
});

// Показываем empty state для пустых колонок при загрузке
dropZones.forEach(zone => {
    checkAndShowEmptyState(zone);
});

// ============================================================
// Обработчики Drag & Drop
// ============================================================

/**
 * Начало перетаскивания карточки
 */
function handleDragStart(e) {
    draggedCard = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', this.dataset.taskId);
}

/**
 * Окончание перетаскивания
 */
function handleDragEnd(e) {
    this.classList.remove('dragging');
    draggedCard = null;

    // Убираем подсветку со всех зон
    dropZones.forEach(zone => {
        zone.classList.remove('drag-over');
    });
}

/**
 * Перетаскивание над зоной - разрешаем Drop
 */
function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

/**
 * Вход в зону - подсвечиваем её
 */
function handleDragEnter(e) {
    e.preventDefault();
    this.classList.add('drag-over');
}

/**
 * Выход из зоны - убираем подсветку
 */
function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

/**
 * Drop - перемещение карточки в новую колонку
 */
function handleDrop(e) {
    e.preventDefault();
    this.classList.remove('drag-over');

    if (draggedCard) {
        // Находим зону Drop
        let dropZone = e.target.closest('.drop-zone');

        if (dropZone) {
            const previousDropZone = draggedCard.parentElement;
            const previousNextSibling = draggedCard.nextElementSibling;

            function restoreCardPosition() {
                if (previousNextSibling) {
                    previousDropZone.insertBefore(draggedCard, previousNextSibling);
                } else {
                    const addButton = previousDropZone.querySelector('button');
                    previousDropZone.insertBefore(draggedCard, addButton);
                }

                updateColumnCounter(previousDropZone);
                updateColumnCounter(dropZone);
                checkAndShowEmptyState(previousDropZone);
                checkAndShowEmptyState(dropZone);
            }

            // Получаем все карточки в этой зоне
            const existingCards = dropZone.querySelectorAll('.task-card');

            // Находим позицию для вставки
            let inserted = false;
            const mouseY = e.clientY;

            for (let card of existingCards) {
                if (card === draggedCard) continue;

                const cardRect = card.getBoundingClientRect();
                const cardMiddle = cardRect.top + cardRect.height / 2;

                if (mouseY < cardMiddle) {
                    dropZone.insertBefore(draggedCard, card);
                    inserted = true;
                    break;
                }
            }

            if (!inserted) {
                const addButton = dropZone.querySelector('button');
                if (addButton) {
                    dropZone.insertBefore(draggedCard, addButton);
                } else {
                    dropZone.appendChild(draggedCard);
                }
            }

            // Обновляем счётчик задач
            updateColumnCounter(dropZone);

            // Проверяем empty state
            checkAndShowEmptyState(dropZone);

            const taskId = draggedCard.dataset.taskId;
            const columnId = dropZone.dataset.columnId;

            fetch(`/api/task/${taskId}/move/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ column_id: columnId })
            })
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        restoreCardPosition();
                        alert(data.error || 'Не удалось переместить задачу');
                    }
                })
                .catch(() => {
                    restoreCardPosition();
                    alert('Ошибка сети при перемещении задачи');
                });
        }
    }
}

// ============================================================
// Модальное окно добавления задачи
// ============================================================

/**
 * Открывает модальное окно добавления задачи
 * @param {HTMLElement} btn - Кнопка, которая вызвала функцию
 */
function addNewTask(btn) {
    // Сохраняем текущую зону для добавления
    currentDropZone = btn.closest('.drop-zone');

    // Сбрасываем форму
    document.getElementById('taskTitle').value = '';
    document.getElementById('taskDescription').value = '';

    // Сбрасываем приоритет на Medium
    selectedPriority = 'medium';
    updatePriorityButtons();

    // Показываем модальное окно
    document.getElementById('taskModal').classList.remove('hidden');

    // Фокус на поле ввода названия
    setTimeout(() => {
        document.getElementById('taskTitle').focus();
    }, 100);
}

/**
 * Закрывает модальное окно
 */
function closeTaskModal() {
    document.getElementById('taskModal').classList.add('hidden');
    currentDropZone = null;
}

/**
 * Выбирает приоритет задачи
 * @param {HTMLElement} btn - Кнопка приоритета
 * @param {string} priority - Значение приоритета (low, medium, high)
 */
function selectPriority(btn, priority) {
    selectedPriority = priority;
    updatePriorityButtons();
}

/**
 * Обновляет визуальное состояние кнопок приоритета
 */
function updatePriorityButtons() {
    const buttons = document.querySelectorAll('.priority-btn');
    buttons.forEach(btn => {
        if (btn.dataset.priority === selectedPriority) {
            btn.classList.add('selected');
            btn.dataset.selected = 'true';
        } else {
            btn.classList.remove('selected');
            btn.dataset.selected = 'false';
        }
    });
}

/**
 * Создаёт задачу из данных формы
 */
function createTask() {
    const title = document.getElementById('taskTitle').value.trim();
    const description = document.getElementById('taskDescription').value.trim();

    // Проверяем название задачи
    if (!title) {
        document.getElementById('taskTitle').focus();
        return;
    }

    // Проверяем, что зона для добавления существует
    if (!currentDropZone) {
        closeTaskModal();
        return;
    }

    // Получаем ID колонки из data-атрибута
    const columnId = currentDropZone.dataset.columnId;
    // Отправка данных на сервер
    fetch('/api/task/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({
            title: title,
            description: description,
            priority: selectedPriority,
            column_id: columnId
        })
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            // Создаём карточку с ID с сервера
            const newTask = createTaskCard(title, description, selectedPriority, data.task.id);

            // Находим кнопку добавления
            const addButton = currentDropZone.querySelector('button');

            // Вставляем перед кнопкой с анимацией
            currentDropZone.insertBefore(newTask, addButton);
            newTask.classList.add('animate-in');

            // Обновляем счётчик
            updateColumnCounter(currentDropZone);

            // Проверяем empty state
            checkAndShowEmptyState(currentDropZone);

            // Закрываем модалку
            closeTaskModal();

        } else {
            alert('Ошибка: ' + (data.error || 'Не удалось создать задачу'));
        }
    })
    .catch(function(error) {
        console.error('Error:', error);
        alert('Ошибка при создании задачи');
    });
}

/**
 * Получить CSRF токен
 */
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

// ============================================================
// Создание карточки задачи
// ============================================================

/**
 * Создаёт HTML-элемент карточки задачи
 * @param {string} title - Название задачи
 * @param {string} description - Описание задачи
 * @param {string} priority - Приоритет (low, medium, high)
 * @param {number} taskId - ID задачи с сервера (опционально)
 * @returns {HTMLElement} Элемент карточки
 */
function createTaskCard(title, description, priority, taskId) {
    const card = document.createElement('div');
    card.className = 'bg-zinc-900 rounded-3xl p-5 shadow-xl hover:shadow-2xl transition-all duration-300 cursor-grab hover:-translate-y-1 task-card';
    card.setAttribute('draggable', 'true');
    card.dataset.taskId = taskId || ++taskIdCounter;

    // CSS классы для приоритета
    const priorityClasses = {
        low: 'bg-green-500/10 text-green-400',
        medium: 'bg-yellow-500/10 text-yellow-400',
        high: 'bg-red-500/10 text-red-400'
    };

    const priorityLabels = {
        low: 'Low',
        medium: 'Medium',
        high: 'High'
    };

    // Описание по умолчанию, если не указано
    const descText = description || 'Описание задачи';
    const currentUserAvatar = window.teamflowCurrentUserAvatar || '';
    const currentUserInitial = window.teamflowCurrentUserInitial || '?';
    const currentUserMarkup = currentUserAvatar
        ? `<img src="${escapeHtml(currentUserAvatar)}" alt="Ваш аватар" class="w-7 h-7 rounded-full object-cover">`
        : `<span role="img" aria-label="Ваш аватар" class="flex w-7 h-7 items-center justify-center rounded-full bg-violet-600 text-xs font-semibold text-white">${escapeHtml(currentUserInitial)}</span>`;

    card.innerHTML = `
        <div class="flex items-start justify-between mb-3">
            <span class="${priorityClasses[priority]} text-xs px-2 py-1 rounded-2xl font-medium">${priorityLabels[priority]}</span>
        </div>
        <h3 class="font-semibold text-base mb-2">${escapeHtml(title)}</h3>
        <p class="text-zinc-400 text-sm line-clamp-2 mb-3">${escapeHtml(descText)}</p>
        <div class="flex items-center justify-between pt-3 border-t border-zinc-800">
            <div class="flex items-center gap-2">
                ${currentUserMarkup}
            </div>
            <div class="flex items-center gap-1 text-sm text-zinc-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <span>Сегодня</span>
            </div>
        </div>
    `;

    // Добавляем обработчики Drag & Drop
    card.addEventListener('dragstart', handleDragStart);
    card.addEventListener('dragend', handleDragEnd);

    return card;
}

/**
 * Обновляет счётчик задач в заголовке колонки
 * @param {HTMLElement} dropZone - Зона Drop колонки
 */
function updateColumnCounter(dropZone) {
    const header = dropZone.previousElementSibling;

    if (header) {
        const counter = header.querySelector('span');

        if (counter) {
            const taskCount = dropZone.querySelectorAll('.task-card').length;
            counter.textContent = taskCount;
        }
    }
}

/**
 * Экранирует HTML для защиты от XSS
 * @param {string} text - Текст для экранирования
 * @returns {string} Экранированный текст
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================
// Empty State для пустых колонок
// ============================================================

/**
 * Создаёт HTML элемент empty state для пустой колонки
 * @returns {HTMLElement} Элемент empty state
 */
function createEmptyState() {
    const empty = document.createElement('div');
    empty.className = 'empty-state flex flex-col items-center justify-center py-8 px-4 text-center';

    empty.innerHTML = `
        <svg class="w-12 h-12 text-zinc-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
        </svg>
        <h3 class="text-zinc-300 font-medium mb-1">Колонка пуста</h3>
        <p class="text-zinc-500 text-sm">Перетащите задачу сюда<br>или нажмите кнопку ниже</p>
    `;

    return empty;
}

/**
 * Проверяет и показывает empty state для колонки
 * @param {HTMLElement} dropZone - Зона Drop колонки
 */
function checkAndShowEmptyState(dropZone) {
    const taskCards = dropZone.querySelectorAll('.task-card');
    const emptyState = dropZone.querySelector('.empty-state');

    if (taskCards.length === 0) {
        // Колонка пуста - показываем empty state
        if (!emptyState) {
            const empty = createEmptyState();
            const addButton = dropZone.querySelector('button');
            if (addButton) {
                dropZone.insertBefore(empty, addButton);
            } else {
                dropZone.appendChild(empty);
            }
        }
    } else {
        // Колонка не пуста - убираем empty state
        if (emptyState) {
            emptyState.remove();
        }
    }
}

// ============================================================
// Закрытие модалки по Escape
// ============================================================

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeTaskModal();
    }
});
// Сворачивание колонок
// ====================== СВОРАЧИВАНИЕ КОЛОНОК ======================
function toggleColumn(columnId) {
    const column = document.querySelector(`[data-column="${columnId}"]`);
    if (!column) return;

    const header = column.querySelector('.bg-zinc-900.rounded-t-3xl');
    const content = column.querySelector('.bg-zinc-900\\/50'); // более точный селектор
    const toggleIcon = column.querySelector('button[onclick*="toggleColumn"] svg');

    const isCollapsed = column.classList.contains('collapsed');

    if (isCollapsed) {
        // === РАЗВОРАЧИВАЕМ ===
        column.classList.remove('collapsed');
        column.style.width = '340px';

        if (content) {
            content.style.display = 'block';
            // Плавное появление
            content.style.opacity = '0';
            setTimeout(() => {
                content.style.transition = 'opacity 0.25s ease';
                content.style.opacity = '1';
            }, 10);
        }

        if (toggleIcon) toggleIcon.style.transform = 'rotate(0deg)';
    } else {
        // === СВОРАЧИВАЕМ ===
        column.classList.add('collapsed');
        column.style.width = '68px'; // чуть шире, чтобы иконка нормально выглядела

        if (content) {
            content.style.transition = 'opacity 0.2s ease';
            content.style.opacity = '0';

            setTimeout(() => {
                content.style.display = 'none';
            }, 200);
        }

        if (toggleIcon) toggleIcon.style.transform = 'rotate(90deg)';
    }
}

// Плавный горизонтальный скролл колесиком мыши (только с Shift)
const boardContainer = document.querySelector('.overflow-x-auto');
if (boardContainer) {
    boardContainer.addEventListener('wheel', function(e) {
        // Разрешаем вертикальный скролл без Shift
        if (!e.shiftKey && e.deltaY !== 0) {
            return; // обычный вертикальный скролл
        }
        // С Shift - горизонтальный скролл
        if (e.deltaY !== 0) {
            e.preventDefault();
            this.scrollLeft += e.deltaY;
        }
    }, { passive: false });
}

// Разрешаем скролл везде внутри доски
document.addEventListener('wheel', function(e) {
    // Не делаем preventDefault - пусть работает нативный скролл
}, { passive: true });

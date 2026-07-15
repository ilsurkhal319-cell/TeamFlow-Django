// ============================================================
// Избранное - TeamFlow
// ============================================================

// Убрать доску из избранного
function removeFromFavorites(button, boardId) {
    event.preventDefault();
    event.stopPropagation();

    var card = button.closest('.favorite-card');

    // Анимация удаления
    card.classList.add('removing');

    setTimeout(function() {
        card.style.display = 'none';

        // Здесь можно добавить AJAX запрос для удаления из избранного
        console.log('Удалено из избранного, ID доски:', boardId);

        // Если это была последняя карточка, показать пустое состояние
        var remainingCards = document.querySelectorAll('.favorite-card:not([style*="display: none"])');
        if (remainingCards.length === 0) {
            showEmptyState();
        }
    }, 300);
}

// Показать пустое состояние
function showEmptyState() {
    var content = document.querySelector('main');
    var grid = document.querySelector('.grid');

    if (grid) {
        grid.style.display = 'none';
    }

    // Создаём пустое состояние
    var emptyState = document.createElement('div');
    emptyState.className = 'flex flex-col items-center justify-center py-20';
    emptyState.innerHTML = `
        <div class="w-24 h-24 bg-zinc-900 rounded-3xl flex items-center justify-center mb-6">
            <svg class="w-12 h-12 text-amber-500" fill="currentColor" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
            </svg>
        </div>
        <h2 class="text-2xl font-semibold mb-2">Здесь пока пусто</h2>
        <p class="text-zinc-400 mb-8 max-w-md text-center">Отметьте звёздочкой важные доски, и они появятся здесь</p>
        <a href="/dashboard/" class="bg-violet-600 hover:bg-violet-700 text-white px-6 py-3 rounded-xl text-base font-semibold transition-all hover:shadow-lg hover:shadow-violet-600/25 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2"/>
            </svg>
            Перейти ко всем доскам
        </a>
    `;

    content.insertBefore(emptyState, grid);
}

// Плавный горизонтальный скролл колесиком мыши
var scrollContainer = document.querySelector('.overflow-x-auto');
if (scrollContainer) {
    scrollContainer.addEventListener('wheel', function(e) {
        if (e.deltaY !== 0) {
            e.preventDefault();
            this.scrollLeft += e.deltaY;
        }
    }, { passive: false });
}

// Поиск по избранным доскам
var searchInput = document.querySelector('input[placeholder*="Поиск"]');
if (searchInput) {
    searchInput.addEventListener('input', function(e) {
        var query = e.target.value.toLowerCase();
        var cards = document.querySelectorAll('.favorite-card');

        cards.forEach(function(card) {
            var title = card.querySelector('h3').textContent.toLowerCase();
            var description = card.querySelector('p').textContent.toLowerCase();

            if (title.includes(query) || description.includes(query)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// Фильтры (Все, Personal, Team)
var filterButtons = document.querySelectorAll('.flex.bg-zinc-900 button');
filterButtons.forEach(function(btn) {
    btn.addEventListener('click', function() {
        // Убираем активный класс со всех кнопок
        filterButtons.forEach(function(b) {
            b.classList.remove('bg-violet-600', 'text-white');
            b.classList.add('text-zinc-400');
        });

        // Добавляем активный класс на нажатую кнопку
        this.classList.add('bg-violet-600', 'text-white');
        this.classList.remove('text-zinc-400');

        var filter = this.textContent.trim();
        var cards = document.querySelectorAll('.favorite-card');

        cards.forEach(function(card) {
            // Здесь должна быть логика фильтрации по workspace
            // Для примера просто показываем все
            card.style.display = 'block';
        });
    });
});

// Drag & Drop для изменения порядка
var draggableCards = document.querySelectorAll('.favorite-card');
draggableCards.forEach(function(card) {
    card.setAttribute('draggable', 'true');

    card.addEventListener('dragstart', function(e) {
        this.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    });

    card.addEventListener('dragend', function() {
        this.classList.remove('dragging');
    });
});

// Drop зона
var grid = document.querySelector('.grid');
if (grid) {
    grid.addEventListener('dragover', function(e) {
        e.preventDefault();
        var dragging = document.querySelector('.dragging');
        var afterElement = getDragAfterElement(grid, e.clientY);

        if (afterElement == null) {
            grid.appendChild(dragging);
        } else {
            grid.insertBefore(dragging, afterElement);
        }
    });
}

// Определение позиции для вставки
function getDragAfterElement(container, y) {
    var draggableElements = [].slice.call(container.querySelectorAll('.favorite-card:not(.dragging)'));

    return draggableElements.reduce(function(closest, child) {
        var box = child.getBoundingClientRect();
        var offset = y - box.top - box.height / 2;

        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// Добавить страницу в body для специфичных стилей
document.body.classList.add('favorites-page');
// ============================================================
// Страница архива - TeamFlow
// ============================================================

// Текущее состояние фильтров
let currentTypeFilter = 'all';
let currentSort = 'date_new';
let searchQuery = '';

// Показать/скрыть dropdown сортировки
function toggleSortDropdown() {
    var dropdown = document.getElementById('sortDropdown');
    dropdown.classList.toggle('hidden');
}

// Закрыть dropdown при клике вне его
document.addEventListener('click', function(e) {
    var dropdown = document.getElementById('sortDropdown');
    var sortBtn = e.target.closest('button:has(.fa)');

    if (!dropdown.contains(e.target) && !sortBtn) {
        dropdown.classList.add('hidden');
    }
});

// Установить фильтр типа
function setTypeFilter(type) {
    currentTypeFilter = type;

    // Обновить вид кнопок
    document.querySelectorAll('.filter-btn').forEach(function(btn) {
        btn.classList.remove('bg-violet-600', 'text-white');
        btn.classList.add('text-zinc-400');
    });

    var activeBtn = document.getElementById('filter' + type.charAt(0).toUpperCase() + type.slice(1));
    if (activeBtn) {
        activeBtn.classList.add('bg-violet-600', 'text-white');
        activeBtn.classList.remove('text-zinc-400');
    }

    filterArchive();
}

// Установить сортировку
function setSort(sort) {
    currentSort = sort;

    // Закрыть dropdown
    document.getElementById('sortDropdown').classList.add('hidden');

    // Обновить текст кнопки
    var sortTexts = {
        'date_new': 'По дате (новые)',
        'date_old': 'По дате (старые)',
        'name_asc': 'По названию (А→Я)',
        'name_desc': 'По названию (Я→А)',
        'tasks_desc': 'По задачам'
    };

    var sortBtn = document.querySelector('button[onclick="toggleSortDropdown()"]');
    var sortLabel = sortBtn.querySelector('svg:first-of-type');
    if (sortLabel && sortTexts[sort]) {
        sortBtn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"/></svg>' +
            sortTexts[sort] +
            '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>';
    }

    filterArchive();
}

// Поиск
function setSearchQuery(query) {
    searchQuery = query.toLowerCase();
    filterArchive();
}

// Основная функция фильтрации и сортировки
function filterArchive() {
    var cards = document.querySelectorAll('.archive-card');
    var searchInput = document.getElementById('archiveSearch');
    var query = searchInput ? searchInput.value.toLowerCase() : '';

    // Фильтрация
    cards.forEach(function(card) {
        var type = card.dataset.type;
        var title = card.dataset.title || '';
        var description = card.querySelector('p.text-zinc-500')?.textContent || '';

        var showByType = currentTypeFilter === 'all' || type === currentTypeFilter;
        var showBySearch = !query || title.toLowerCase().includes(query) || description.toLowerCase().includes(query);

        if (showByType && showBySearch) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });

    // Сортировка
    var grid = document.getElementById('archiveGrid');
    var visibleCards = Array.from(cards).filter(function(card) {
        return card.style.display !== 'none';
    });

    visibleCards.sort(function(a, b) {
        switch (currentSort) {
            case 'date_new':
                return new Date(b.dataset.date) - new Date(a.dataset.date);
            case 'date_old':
                return new Date(a.dataset.date) - new Date(b.dataset.date);
            case 'name_asc':
                return (a.dataset.title || '').localeCompare(b.dataset.title || '');
            case 'name_desc':
                return (b.dataset.title || '').localeCompare(a.dataset.title || '');
            case 'tasks_desc':
                return parseInt(b.dataset.tasks || 0) - parseInt(a.dataset.tasks || 0);
            default:
                return 0;
        }
    });

    // Переставить элементы
    visibleCards.forEach(function(card) {
        grid.appendChild(card);
    });

    // Обновить счётчик
    updateCount();
}

// Обновить счётчик досок
function updateCount() {
    var visibleCards = document.querySelectorAll('.archive-card[style=""]');
    var count = 0;
    document.querySelectorAll('.archive-card').forEach(function(card) {
        if (card.style.display !== 'none') {
            count++;
        }
    });

    var countEl = document.getElementById('archiveCount');
    if (countEl) {
        var text = count === 1 ? 'элемент' : (count < 5 ? 'элемента' : 'элементов');
        countEl.textContent = 'Архивированные доски • ' + count + ' ' + text;
    }
}

// Восстановить доску из архива
function restoreBoard(button) {
    var card = button.closest('.archive-card');

    // Анимация восстановления (доска "улетает")
    card.style.transition = 'all 0.5s ease';
    card.style.transform = 'translateX(100%) scale(0.8)';
    card.style.opacity = '0';

    setTimeout(function() {
        // Скрываем карточку
        card.style.display = 'none';

        // Обновляем счётчик
        updateCount();

        // Показываем уведомление
        if (typeof showNotification === 'function') {
            showNotification('Доска восстановлена из архива');
        } else {
            alert('Доска восстановлена из архива');
        }

        console.log('Доска восстановлена');
    }, 500);
}

// Удалить доску навсегда
function deleteBoardForever(button) {
    if (!confirm('Вы уверены, что хотите удалить эту доску навсегда? Это действие нельзя отменить.')) {
        return;
    }

    var card = button.closest('.archive-card');

    // Анимация удаления
    card.style.transition = 'all 0.5s ease';
    card.style.transform = 'translateY(-20px) scale(0.8)';
    card.style.opacity = '0';

    setTimeout(function() {
        // Удаляем карточку
        card.remove();

        // Обновляем счётчик
        updateCount();

        // Показываем уведомление
        if (typeof showNotification === 'function') {
            showNotification('Доска удалена навсегда');
        } else {
            alert('Доска удалена навсегда');
        }

        console.log('Доска удалена навсегда');
    }, 500);
}

// Очистить весь архив
function clearArchive() {
    if (!confirm('Вы уверены, что хотите очистить весь архив? Все архивированные доски будут удалены навсегда.')) {
        return;
    }

    var cards = document.querySelectorAll('.archive-card');
    var count = 0;

    cards.forEach(function(card, index) {
        setTimeout(function() {
            card.style.transition = 'all 0.3s ease';
            card.style.transform = 'translateY(-20px)';
            card.style.opacity = '0';

            setTimeout(function() {
                card.style.display = 'none';
            }, 300);
        }, index * 100);
        count++;
    });

    setTimeout(function() {
        updateCount();

        if (typeof showNotification === 'function') {
            showNotification('Архив очищен');
        } else {
            alert('Архив очищен');
        }
    }, count * 100 + 300);
}
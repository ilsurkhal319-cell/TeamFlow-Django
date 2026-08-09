// Переключение табов
function switchTab(tabName) {
    // Скрываем все вкладки
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Убираем активный класс у всех кнопок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Показываем выбранную вкладку
    document.getElementById('tab-' + tabName).classList.add('active');

    // Добавляем активный класс кнопке
    document.querySelector('[data-tab="' + tabName + '"]').classList.add('active');
}

// Открыть модалку редактирования
function openEditModal() {
    document.getElementById('editProfileModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

// Закрыть модалку редактирования
function closeEditModal() {
    document.getElementById('editProfileModal').classList.add('hidden');
    document.body.style.overflow = '';
}

// Закрытие по Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeEditModal();
    }
});

// Закрытие при клике вне модалки
document.addEventListener('click', function(e) {
    var modal = document.getElementById('editProfileModal');
    if (!modal) {
        return;
    }

    var modalContent = modal.querySelector('.modal-content');

    if (!modal.classList.contains('hidden') && !modalContent.contains(e.target)) {
        closeEditModal();
    }
});

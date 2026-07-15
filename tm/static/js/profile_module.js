// ============================================================
// Модалка профиля - TeamFlow
// ============================================================

// Открыть/закрыть модалку профиля
function toggleProfileModal() {
    var modal = document.getElementById('profileModal');
    if (!modal) return;
    modal.classList.toggle('hidden');
}

// Закрыть модалку профиля
function closeProfileModal() {
    var modal = document.getElementById('profileModal');
    if (!modal) return;
    modal.classList.add('hidden');
}

// Закрытие по Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeProfileModal();
    }
});

// Закрытие при клике вне модалки
document.addEventListener('click', function(e) {
    var modal = document.getElementById('profileModal');
    if (!modal) return;

    var profileBtn = e.target.closest('button[onclick="toggleProfileModal()"]');

    if (!modal.classList.contains('hidden') && !profileBtn && !modal.contains(e.target)) {
        closeProfileModal();
    }
});
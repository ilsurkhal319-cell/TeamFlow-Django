var editProfileTrigger = null;

function switchTab(tabName, updateHash) {
    var tab = document.getElementById('tab-' + tabName);
    var button = document.querySelector('[data-tab="' + tabName + '"]');
    if (!tab || !button) return;

    document.querySelectorAll('.tab-content').forEach(function(item) {
        item.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(function(item) {
        item.classList.remove('active');
        item.setAttribute('aria-selected', 'false');
    });

    tab.classList.add('active');
    button.classList.add('active');
    button.setAttribute('aria-selected', 'true');

    if (updateHash !== false && window.history.replaceState) {
        window.history.replaceState(null, '', '#' + tabName);
    }
}

function openEditModal() {
    var modal = document.getElementById('editProfileModal');
    if (!modal) return;
    editProfileTrigger = document.activeElement;
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    var firstInput = modal.querySelector('input:not([type="hidden"]):not([readonly])');
    if (firstInput) firstInput.focus();
}

function closeEditModal() {
    var modal = document.getElementById('editProfileModal');
    if (!modal || modal.classList.contains('hidden')) return;
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (editProfileTrigger && typeof editProfileTrigger.focus === 'function') {
        editProfileTrigger.focus();
    }
}

function setActiveFilter(buttons, activeButton) {
    buttons.forEach(function(button) {
        button.classList.toggle('active', button === activeButton);
    });
}

function filterBoards(filter, button) {
    var cards = Array.from(document.querySelectorAll('.profile-board'));
    var visible = 0;
    cards.forEach(function(card) {
        var show = filter === 'all' || card.dataset[filter] === 'true';
        card.classList.toggle('hidden', !show);
        if (show) visible += 1;
    });
    setActiveFilter(document.querySelectorAll('[data-board-filter]'), button);
    var empty = document.getElementById('boardsFilterEmpty');
    if (empty) empty.classList.toggle('hidden', visible !== 0 || cards.length === 0);
}

function filterTasks(filter, button) {
    var tasks = Array.from(document.querySelectorAll('.profile-task'));
    var visible = 0;
    tasks.forEach(function(task) {
        var show = filter === 'all' || task.dataset.status === filter;
        task.classList.toggle('hidden', !show);
        if (show) visible += 1;
    });
    setActiveFilter(document.querySelectorAll('[data-task-filter]'), button);
    var empty = document.getElementById('tasksFilterEmpty');
    if (empty) empty.classList.toggle('hidden', visible !== 0 || tasks.length === 0);
}

document.addEventListener('DOMContentLoaded', function() {
    var initialTab = window.location.hash.replace('#', '');
    if (!document.getElementById('tab-' + initialTab)) initialTab = 'overview';
    switchTab(initialTab, false);

    document.querySelectorAll('[data-board-filter]').forEach(function(button) {
        button.addEventListener('click', function() {
            filterBoards(button.dataset.boardFilter, button);
        });
    });

    document.querySelectorAll('[data-task-filter]').forEach(function(button) {
        button.addEventListener('click', function() {
            filterTasks(button.dataset.taskFilter, button);
        });
    });

    var activeTaskButton = document.querySelector('[data-task-filter="active"]');
    if (activeTaskButton) filterTasks('active', activeTaskButton);

    document.querySelectorAll('[data-close-edit]').forEach(function(button) {
        button.addEventListener('click', closeEditModal);
    });

    var avatarInput = document.getElementById('id_avatar');
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            var file = avatarInput.files && avatarInput.files[0];
            var preview = document.getElementById('avatarPreview');
            if (!file || !preview) return;
            if (preview.tagName !== 'IMG') {
                var image = document.createElement('img');
                image.id = preview.id;
                image.alt = preview.getAttribute('aria-label') || 'Предпросмотр аватара';
                image.className = 'h-20 w-20 rounded-full border-4 border-zinc-800 object-cover';
                preview.replaceWith(image);
                preview = image;
            }
            var reader = new FileReader();
            reader.addEventListener('load', function(event) {
                preview.src = event.target.result;
            });
            reader.readAsDataURL(file);
        });
    }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') closeEditModal();
});

window.addEventListener('hashchange', function() {
    var tabName = window.location.hash.replace('#', '');
    if (document.getElementById('tab-' + tabName)) switchTab(tabName, false);
});

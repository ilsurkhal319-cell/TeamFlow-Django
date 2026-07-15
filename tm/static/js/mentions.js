// @mention autocomplete functionality

var MentionsManager = {
    dropdown: null,
    currentTextarea: null,
    searchQuery: '',
    selectedIndex: -1,
    users: [],

    init: function() {
        this.createDropdown();
        this.attachListeners();
    },

    createDropdown: function() {
        var dropdown = document.createElement('div');
        dropdown.id = 'mentionsDropdown';
        dropdown.className = 'hidden absolute z-50 w-72 mt-1 bg-zinc-800 rounded-xl border border-zinc-700 shadow-xl overflow-hidden';
        dropdown.innerHTML = '<div class="p-2 max-h-48 overflow-y-auto" id="mentionsList"></div>';
        document.body.appendChild(dropdown);
        this.dropdown = dropdown;
    },

    attachListeners: function() {
        var self = this;

        // Делегирование событий на document для динамических textarea
        document.addEventListener('input', function(e) {
            if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') {
                var value = e.target.value;
                var cursorPos = e.target.selectionStart;
                self.checkForMention(e.target, value, cursorPos);
            }
        });

        document.addEventListener('keydown', function(e) {
            if (!self.dropdown || self.dropdown.classList.contains('hidden')) return;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                self.selectNext();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                self.selectPrev();
            } else if (e.key === 'Enter') {
                e.preventDefault();
                self.selectCurrent();
            } else if (e.key === 'Escape') {
                self.hideDropdown();
            }
        });

        // Закрыть dropdown при клике вне
        document.addEventListener('click', function(e) {
            if (self.dropdown && !self.dropdown.contains(e.target) && !e.target.closest('.mention-trigger')) {
                self.hideDropdown();
            }
        });
    },

    checkForMention: function(textarea, value, cursorPos) {
        var textBeforeCursor = value.substring(0, cursorPos);
        var lastAtPos = textBeforeCursor.lastIndexOf('@');

        if (lastAtPos === -1) {
            this.hideDropdown();
            return;
        }

        // Проверяем, есть ли пробел после последнего @
        var textAfterAt = textBeforeCursor.substring(lastAtPos + 1);
        if (textAfterAt.includes(' ') || textAfterAt.includes('\n')) {
            this.hideDropdown();
            return;
        }

        this.searchQuery = textAfterAt;
        this.currentTextarea = textarea;
        this.searchUsers(textAfterAt);
    },

    searchUsers: function(query) {
        var self = this;

        fetch('/api/users/search/?q=' + encodeURIComponent(query))
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success && data.users.length > 0) {
                    self.users = data.users;
                    self.showDropdown(data.users);
                } else {
                    self.hideDropdown();
                }
            })
            .catch(function() {
                self.hideDropdown();
            });
    },

    showDropdown: function(users) {
        var list = document.getElementById('mentionsList');
        var self = this;
        this.selectedIndex = -1;

        if (users.length === 0) {
            list.innerHTML = '<p class="text-zinc-500 text-sm text-center py-2">Пользователи не найдены</p>';
        } else {
            list.innerHTML = '';
            users.forEach(function(user, index) {
                var item = document.createElement('div');
                item.className = 'flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-700 cursor-pointer mention-item';
                item.dataset.index = index;
                item.dataset.username = user.username;
                item.innerHTML =
                    '<img src="https://api.dicebear.com/7.x/avataaars/svg?seed=' + user.username + '" class="w-8 h-8 rounded-full">' +
                    '<div><p class="text-sm text-white">' + user.name + '</p>' +
                    '<p class="text-xs text-zinc-400">@' + user.username + '</p></div>';
                item.onclick = function() { self.insertMention(user.username); };
                list.appendChild(item);
            });
        }

        // Позиционирование dropdown
        this.positionDropdown();

        this.dropdown.classList.remove('hidden');
    },

    positionDropdown: function() {
        if (!this.currentTextarea) return;

        var textarea = this.currentTextarea;
        var rect = textarea.getBoundingClientRect();
        var cursorPos = textarea.selectionStart;
        var textBeforeCursor = textarea.value.substring(0, cursorPos);
        var lines = textBeforeCursor.split('\n');
        var currentLineNum = lines.length - 1;
        var lineHeight = 24; // примерная высота строки

        var top = rect.top + (currentLineNum * lineHeight) + 60; // +60 для отступа
        var left = rect.left + 20;

        this.dropdown.style.top = top + 'px';
        this.dropdown.style.left = left + 'px';
    },

    hideDropdown: function() {
        if (this.dropdown) {
            this.dropdown.classList.add('hidden');
        }
        this.users = [];
        this.searchQuery = '';
        this.currentTextarea = null;
    },

    selectNext: function() {
        var items = this.dropdown.querySelectorAll('.mention-item');
        if (items.length === 0) return;
        this.selectedIndex = (this.selectedIndex + 1) % items.length;
        this.updateSelection(items);
    },

    selectPrev: function() {
        var items = this.dropdown.querySelectorAll('.mention-item');
        if (items.length === 0) return;
        this.selectedIndex = this.selectedIndex <= 0 ? items.length - 1 : this.selectedIndex - 1;
        this.updateSelection(items);
    },

    updateSelection: function(items) {
        items.forEach(function(item, index) {
            item.classList.toggle('bg-violet-600', index === 0);
            item.classList.toggle('bg-zinc-700', index !== 0);
        });
    },

    selectCurrent: function() {
        var items = this.dropdown.querySelectorAll('.mention-item');
        if (this.selectedIndex >= 0 && this.selectedIndex < items.length) {
            var username = items[this.selectedIndex].dataset.username;
            this.insertMention(username);
        }
    },

    insertMention: function(username) {
        if (!this.currentTextarea) return;

        var textarea = this.currentTextarea;
        var value = textarea.value;
        var cursorPos = textarea.selectionStart;
        var textBeforeCursor = value.substring(0, cursorPos);
        var lastAtPos = textBeforeCursor.lastIndexOf('@');

        var textBefore = value.substring(0, lastAtPos);
        var textAfter = value.substring(cursorPos);

        textarea.value = textBefore + '@' + username + ' ' + textAfter;

        // Установка курсора после вставленного username
        var newPos = lastAtPos + username.length + 2;
        textarea.setSelectionRange(newPos, newPos);
        textarea.focus();

        this.hideDropdown();
    }
};

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    MentionsManager.init();
});
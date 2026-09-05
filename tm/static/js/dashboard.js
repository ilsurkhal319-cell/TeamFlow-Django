function closeRecentActivityModal() {
    document.getElementById("recentActivityModal").classList.add("hidden");
}

function openJoinBoardModal() {
    const modal = document.getElementById("joinBoardModal");
    const input = document.getElementById("joinBoardCode");
    const error = document.getElementById("joinBoardError");
    modal.classList.remove("hidden");
    input.value = "";
    error.classList.add("hidden");
    input.focus();
}

function closeJoinBoardModal() {
    document.getElementById("joinBoardModal").classList.add("hidden");
}

async function joinBoard() {
    const input = document.getElementById("joinBoardCode");
    const error = document.getElementById("joinBoardError");
    const code = input.value.trim().toUpperCase();

    if (!code) {
        error.textContent = "Введите код доски.";
        error.classList.remove("hidden");
        input.focus();
        return;
    }

    try {
        const response = await fetch("/api/board/join/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken") || "",
            },
            body: JSON.stringify({code}),
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.error || "Не удалось присоединиться к доске.");
        }
        window.location.href = `/board/${data.board_id}/`;
    } catch (joinError) {
        error.textContent = joinError.message;
        error.classList.remove("hidden");
    }
}

async function openRecentActivityModal() {
    const modal = document.getElementById("recentActivityModal");
    const list = document.getElementById("recentActivityList");

    modal.classList.remove("hidden");
    list.innerHTML = '<p class="px-3 py-8 text-center text-sm text-zinc-400">Загружаем изменения...</p>';

    try {
        const response = await fetch("/api/drf/activity/");
        if (!response.ok) {
            throw new Error("Не удалось загрузить изменения");
        }

        const data = await response.json();
        renderRecentActivity(data.results, list);
    } catch (error) {
        list.innerHTML = '<p class="px-3 py-8 text-center text-sm text-red-400">Не удалось загрузить изменения.</p>';
    }
}

function renderRecentActivity(activity, container) {
    if (!activity.length) {
        container.innerHTML = '<p class="px-3 py-8 text-center text-sm text-zinc-400">Изменений пока нет.</p>';
        return;
    }

    container.innerHTML = activity.map((item) => {
        const typeLabel = item.type === "task" ? "Задача" : "Доска";
        const updatedAt = new Date(item.updated_at).toLocaleString("ru-RU", {
            day: "2-digit",
            month: "short",
            hour: "2-digit",
            minute: "2-digit",
        });

        return `
            <a href="${item.link}" class="block rounded-lg px-3 py-3 transition-colors hover:bg-zinc-800">
                <div class="flex items-start justify-between gap-4">
                    <div class="min-w-0">
                        <p class="text-sm text-zinc-400">${typeLabel}</p>
                        <p class="truncate font-medium text-zinc-100">${escapeActivityHtml(item.title)}</p>
                        <p class="truncate text-sm text-zinc-400">${escapeActivityHtml(item.detail)}</p>
                    </div>
                    <time class="shrink-0 text-xs text-zinc-500">${updatedAt}</time>
                </div>
            </a>
        `;
    }).join("");
}

function escapeActivityHtml(value) {
    const element = document.createElement("div");
    element.textContent = value;
    return element.innerHTML;
}

function loadListList() {
    fetch('/api/lists')
        .then(response => response.json())
        .then(lists => {
            const listList = document.getElementById('list-list');
            listList.innerHTML = `
                <ul class="list-group">
                    ${lists.map(list => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="/list/${list.id}">${list.name}</a>
                            <span class="badge bg-primary rounded-pill">${list.book_count} books</span>
                        </li>
                    `).join('')}
                </ul>
            `;
        });
}

// Keep the existing loadListDetails function

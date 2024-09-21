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
                            <span class="badge bg-success rounded-pill">${list.read_percentage.toFixed(1)}% read</span>
                        </li>
                    `).join('')}
                </ul>
            `;
        });
}

function loadListDetails(listId) {
    fetch(`/api/lists/${listId}`)
        .then(response => response.json())
        .then(list => {
            const listDetails = document.getElementById('list-details');
            listDetails.innerHTML = `
                <h2>${list.name}</h2>
                <p>Books: ${list.books.length}</p>
                <p>Read Percentage: ${list.read_percentage.toFixed(1)}%</p>
                <h3>Books:</h3>
                <ul class="list-group">
                    ${list.books.map(book => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            ${book.title} by ${book.author}
                            <span class="badge ${book.is_read ? 'bg-success' : 'bg-secondary'} rounded-pill">
                                ${book.is_read ? 'Read' : 'Unread'}
                            </span>
                        </li>
                    `).join('')}
                </ul>
            `;
        });
}

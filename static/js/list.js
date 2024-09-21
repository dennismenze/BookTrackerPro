function loadListDetails(listId) {
    fetch(`/api/lists/${listId}`)
        .then(response => response.json())
        .then(list => {
            const listDetails = document.getElementById('list-details');
            listDetails.innerHTML = `
                <h2>${list.name}</h2>
                <p>Books: ${list.books.length}</p>
                <p>Read Percentage: ${list.read_percentage.toFixed(2)}%</p>
                <ul>
                    ${list.books.map(book => `
                        <li>
                            ${book.title} by ${book.author}
                            <input type="checkbox" ${book.is_read ? 'checked' : ''} 
                                onchange="updateBookStatus(${book.id}, this.checked)">
                        </li>
                    `).join('')}
                </ul>
            `;
        });
}

function updateBookStatus(bookId, isRead) {
    fetch(`/api/books/${bookId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: isRead }),
    })
    .then(response => response.json())
    .then(() => {
        // Reload the list details to update the statistics
        const listId = new URLSearchParams(window.location.search).get('id');
        loadListDetails(listId);
    });
}

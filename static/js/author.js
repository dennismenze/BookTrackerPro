function loadAuthorDetails(authorId) {
    fetch(`/api/authors/${authorId}`)
        .then(response => response.json())
        .then(author => {
            const authorDetails = document.getElementById('author-details');
            authorDetails.innerHTML = `
                <h2>${author.name}</h2>
                <p>Books: ${author.books.length}</p>
                <p>Read Percentage: ${author.read_percentage.toFixed(2)}%</p>
                <ul>
                    ${author.books.map(book => `
                        <li>
                            ${book.title}
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
        // Reload the author details to update the statistics
        const authorId = new URLSearchParams(window.location.search).get('id');
        loadAuthorDetails(authorId);
    });
}

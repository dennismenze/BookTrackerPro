function loadAuthorList() {
    fetch('/api/authors')
        .then(response => response.json())
        .then(authors => {
            const authorList = document.getElementById('author-list');
            authorList.innerHTML = `
                <ul class="list-group">
                    ${authors.map(author => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="/author/${author.id}">${author.name}</a>
                            <span class="badge bg-primary rounded-pill">${author.book_count} books</span>
                            <span class="badge bg-success rounded-pill">${author.read_percentage.toFixed(1)}% read</span>
                        </li>
                    `).join('')}
                </ul>
            `;
        });
}

function loadAuthorDetails(authorId) {
    fetch(`/api/authors/${authorId}`)
        .then(response => response.json())
        .then(author => {
            const authorDetails = document.getElementById('author-details');
            authorDetails.innerHTML = `
                <h2>${author.name}</h2>
                <p>Books: ${author.books.length}</p>
                <p>Read Percentage: ${author.read_percentage.toFixed(1)}%</p>
                <h3>Books:</h3>
                <ul class="list-group">
                    ${author.books.map(book => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            ${book.title}
                            <span class="badge ${book.is_read ? 'bg-success' : 'bg-secondary'} rounded-pill">
                                ${book.is_read ? 'Read' : 'Unread'}
                            </span>
                        </li>
                    `).join('')}
                </ul>
            `;
        });
}

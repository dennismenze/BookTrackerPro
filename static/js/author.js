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
                        </li>
                    `).join('')}
                </ul>
            `;
        });
}

// Keep the existing loadAuthorDetails function

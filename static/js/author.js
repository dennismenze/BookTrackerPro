function handleUnauthorized(response) {
    if (response.status === 401) {
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        throw new Error('Unauthorized');
    }
    return response;
}

function loadAuthorList() {
    console.log('Loading author list...');
    fetch('/api/authors')
        .then(handleUnauthorized)
        .then(response => {
            console.log('Author list response status:', response.status);
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
                });
            }
            return response.json();
        })
        .then(authors => {
            console.log('Received authors:', authors);
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
        })
        .catch(error => {
            console.error('Error fetching author list:', error);
            const authorList = document.getElementById('author-list');
            authorList.innerHTML = `<p>Error loading author list: ${error.message}. Please try again.</p>`;
        });
}

function loadAuthorDetails(authorId) {
    console.log('Loading author details for id:', authorId);
    fetch(`/api/authors/${authorId}`)
        .then(handleUnauthorized)
        .then(response => {
            console.log('Author details response status:', response.status);
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
                });
            }
            return response.json();
        })
        .then(author => {
            console.log('Received author details:', author);
            const authorDetails = document.getElementById('author-details');
            authorDetails.innerHTML = `
                <h2>${author.name}</h2>
                <p>Books: ${author.books.length}</p>
                <p>Read Percentage: ${author.read_percentage.toFixed(1)}%</p>
                <h3>Books:</h3>
                <ul class="list-group">
                    ${author.books.map(book => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href='/book/${book.id}?id=${book.id}'>${book.title}</a>
                            <span class="badge ${book.is_read ? 'bg-success' : 'bg-secondary'} rounded-pill">
                                ${book.is_read ? 'Read' : 'Unread'}
                            </span>
                        </li>
                    `).join('')}
                </ul>
            `;
        })
        .catch(error => {
            console.error('Error fetching author details:', error);
            const authorDetails = document.getElementById('author-details');
            authorDetails.innerHTML = `<p>Error loading author details: ${error.message}. Please try again.</p>`;
        });
}

function handleUnauthorized(response) {
    if (response.status === 401) {
        console.log('Unauthorized access, redirecting to login');
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        throw new Error('Unauthorized');
    }
    return response;
}

function loadAuthorList(searchQuery = '') {
    console.log('Loading author list...');
    fetch(`/api/authors?search=${encodeURIComponent(searchQuery)}`, {
        method: 'GET',
        credentials: 'include'
    })
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
        .then(data => {
            console.log('Received authors data:', data);
            if (!data || !data.user_authors || !data.all_authors) {
                throw new Error('Invalid data structure received from server');
            }
            const authorList = document.getElementById('author-list');
            if (!authorList) {
                throw new Error('Author list element not found in the DOM');
            }
            authorList.innerHTML = `
                <h2 class="text-2xl font-bold mb-4">Your Authors</h2>
                <ul class="list-group mb-8">
                    ${data.user_authors.map(author => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="/author/${author.id}">${author.name}</a>
                            <span class="badge bg-primary rounded-pill">${author.book_count} books</span>
                            <span class="badge bg-success rounded-pill">${author.read_percentage.toFixed(1)}% read</span>
                        </li>
                    `).join('')}
                </ul>
                <h2 class="text-2xl font-bold mb-4">All Authors</h2>
                <ul class="list-group">
                    ${data.all_authors.map(author => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="/author/${author.id}">${author.name}</a>
                            <span class="badge bg-primary rounded-pill">${author.book_count} books</span>
                        </li>
                    `).join('')}
                </ul>
            `;
        })
        .catch(error => {
            console.error('Error fetching author list:', error);
            const authorList = document.getElementById('author-list');
            if (authorList) {
                authorList.innerHTML = `<p class="text-red-500">Error loading author list: ${error.message}. Please try again.</p>`;
            } else {
                console.error('Author list element not found in the DOM');
            }
        });
}

function loadAuthorDetails(authorId) {
    console.log('Loading author details for id:', authorId);
    fetch(`/api/authors/${authorId}`, {
        method: 'GET',
        credentials: 'include'
    })
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
                            <button onclick="toggleReadStatus(${book.id}, ${!book.is_read}, ${authorId})" class="btn btn-sm ${book.is_read ? 'btn-secondary' : 'btn-success'}">
                                Mark as ${book.is_read ? 'Unread' : 'Read'}
                            </button>
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

function toggleReadStatus(bookId, isRead, authorId) {
    fetch(`/api/books/${bookId}/read_status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: isRead }),
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(() => loadAuthorDetails(authorId))
    .catch(error => {
        console.error('Error updating book read status:', error);
        alert('Failed to update book status. Please try again.');
    });
}

function searchAuthors() {
    const searchQuery = document.getElementById('author-search').value;
    loadAuthorList(searchQuery);
}

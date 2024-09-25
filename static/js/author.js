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
        .then(response => response.json())
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
                            ${isAdmin() ? `<button class="btn btn-danger btn-sm delete-author" data-author-id="${author.id}">Delete</button>` : ''}
                        </li>
                    `).join('')}
                </ul>
            `;
            setupEventListeners();
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
                            <button class="btn btn-sm ${book.is_read ? 'btn-secondary' : 'btn-success'} toggle-read-status" data-book-id="${book.id}" data-is-read="${!book.is_read}" data-author-id="${authorId}">
                                Mark as ${book.is_read ? 'Unread' : 'Read'}
                            </button>
                        </li>
                    `).join('')}
                </ul>
                ${isAdmin() ? `<button class="btn btn-danger mt-4 delete-author" data-author-id="${author.id}">Delete Author</button>` : ''}
            `;
            setupEventListeners();
        })
        .catch(error => {
            console.error('Error fetching author details:', error);
            const authorDetails = document.getElementById('author-details');
            authorDetails.innerHTML = `<p>Error loading author details: ${error.message}. Please try again.</p>`;
        });
}

function toggleReadStatus(bookId, isRead, authorId) {
    console.log(`Toggling read status for book ${bookId} to ${isRead}`);
    fetch(`/api/books/${bookId}/read_status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: isRead }),
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => {
        console.log(`Response status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log(`Response data:`, data);
        loadAuthorDetails(authorId);
    })
    .catch(error => {
        console.error('Error updating book read status:', error);
        alert('Failed to update book status. Please try again.');
    });
}

function searchAuthors() {
    const searchQuery = document.getElementById('author-search').value;
    loadAuthorList(searchQuery);
}

function deleteAuthor(authorId) {
    if (confirm('Are you sure you want to delete this author? This action cannot be undone.')) {
        fetch(`/api/authors/${authorId}`, {
            method: 'DELETE',
            credentials: 'include'
        })
        .then(handleUnauthorized)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete author');
            }
            return response.json();
        })
        .then(data => {
            alert(data.message);
            window.location.href = '/authors';
        })
        .catch(error => {
            console.error('Error deleting author:', error);
            alert('Failed to delete author. Please try again.');
        });
    }
}

function isAdmin() {
    return document.body.dataset.isAdmin === 'true';
}

function setupEventListeners() {
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-author')) {
            const authorId = event.target.dataset.authorId;
            deleteAuthor(authorId);
        } else if (event.target.classList.contains('toggle-read-status')) {
            const bookId = event.target.dataset.bookId;
            const isRead = event.target.dataset.isRead === 'true';
            const authorId = event.target.dataset.authorId;
            toggleReadStatus(bookId, isRead, authorId);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('search-authors-btn');
    if (searchButton) {
        searchButton.addEventListener('click', searchAuthors);
    }
});

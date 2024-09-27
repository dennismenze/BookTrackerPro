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
                <div class="bg-white shadow-md rounded-lg p-6 mb-8">
                    <h2 class="text-2xl font-semibold mb-4">Your Authors</h2>
                    <ul class="space-y-4">
                        ${data.user_authors.map(author => `
                            <li class="flex items-center justify-between bg-gray-100 p-4 rounded-md">
                                <a href="/author/${author.id}" class="text-blue-600 hover:underline">${author.name}</a>
                                <div class="flex space-x-4">
                                    <span class="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">${author.book_count} books</span>
                                    <span class="bg-green-500 text-white px-3 py-1 rounded-full text-sm">${author.read_percentage.toFixed(1)}% read</span>
                                    <span class="bg-yellow-500 text-white px-3 py-1 rounded-full text-sm">${author.main_works_count} main works</span>
                                    <span class="bg-purple-500 text-white px-3 py-1 rounded-full text-sm">${author.read_main_works_percentage.toFixed(1)}% main works read</span>
                                </div>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div class="bg-white shadow-md rounded-lg p-6">
                    <h2 class="text-2xl font-semibold mb-4">All Authors</h2>
                    <ul class="space-y-4">
                        ${data.all_authors.map(author => `
                            <li class="flex items-center justify-between bg-gray-100 p-4 rounded-md">
                                <a href="/author/${author.id}" class="text-blue-600 hover:underline">${author.name}</a>
                                <div class="flex space-x-4">
                                    <span class="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">${author.book_count} books</span>
                                    <span class="bg-yellow-500 text-white px-3 py-1 rounded-full text-sm">${author.main_works_count} main works</span>
                                    ${isAdmin() ? `<button class="bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 transition duration-300 delete-author" data-author-id="${author.id}">Delete</button>` : ''}
                                </div>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        })
        .catch(error => {
            console.error('Error fetching author list:', error);
            const authorList = document.getElementById('author-list');
            if (authorList) {
                authorList.innerHTML = `<p class="text-red-500 p-4 bg-white shadow-md rounded-lg">Error loading author list: ${error.message}. Please try again.</p>`;
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
                <p>Main Works: ${author.main_works_count}</p>
                <p>Main Works Read Percentage: ${author.read_main_works_percentage.toFixed(1)}%</p>
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

function setupEventListenersAuthors() {
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

    const searchButton = document.getElementById('search-authors-btn');
    if (searchButton) {
        searchButton.addEventListener('click', searchAuthors);
    }

    const searchInput = document.getElementById('author-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                searchAuthors();
            }
        });
    }
}

function searchAuthors() {
    const searchQuery = document.getElementById('author-search').value;
    loadAuthorList(searchQuery);
}

document.addEventListener('DOMContentLoaded', function() {
    loadAuthorList();
    setupEventListenersAuthors();
});
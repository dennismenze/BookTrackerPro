function handleUnauthorized(response) {
    if (response.status === 401) {
        console.log('Unauthorized access, redirecting to login');
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        throw new Error('Unauthorized');
    }
    return response;
}

function loadListList(searchQuery = '') {
    console.log('Loading list list...');
    fetch(`/api/lists?search=${encodeURIComponent(searchQuery)}`, {
        method: 'GET',
        credentials: 'include'
    })
        .then(handleUnauthorized)
        .then(response => {
            console.log('List list response status:', response.status);
            return response.json();
        })
        .then(lists => {
            console.log('Received lists:', lists);
            const listList = document.getElementById('list-list');
            listList.innerHTML = `
                <h2>Your Reading Lists</h2>
                <div id="private-lists">
                    <h3>Private Lists</h3>
                    <ul class="list-group">
                        ${lists.filter(list => !list.is_public).map(list => `
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <a href="/list/${list.id}">${list.name}</a>
                                <span class="badge bg-primary rounded-pill">${list.book_count} books</span>
                                <span class="badge bg-success rounded-pill">${list.read_percentage.toFixed(1)}% read</span>
                                <button onclick="toggleListVisibility(${list.id}, true)" class="btn btn-sm btn-outline-primary">Make Public</button>
                                <button onclick="deleteList(${list.id})" class="btn btn-sm btn-danger">Delete</button>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div id="public-lists">
                    <h3>Public Lists</h3>
                    <ul class="list-group">
                        ${lists.filter(list => list.is_public).map(list => `
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <a href="/list/${list.id}">${list.name}</a>
                                <span class="badge bg-primary rounded-pill">${list.book_count} books</span>
                                <span class="badge bg-success rounded-pill">${list.read_percentage.toFixed(1)}% read</span>
                                ${list.user_id === null ? `
                                    <button onclick="toggleListVisibility(${list.id}, false)" class="btn btn-sm btn-outline-secondary">Make Private</button>
                                ` : ''}
                                ${isAdmin() ? `<button onclick="deleteList(${list.id})" class="btn btn-sm btn-danger">Delete</button>` : ''}
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <button onclick="showCreateListForm()" class="btn btn-primary mt-3">Create New List</button>
            `;
        })
        .catch(error => {
            console.error('Error fetching list list:', error);
            const listList = document.getElementById('list-list');
            listList.innerHTML = '<p>Error loading list list. Please try again.</p>';
        });
}

function showCreateListForm() {
    const listList = document.getElementById('list-list');
    listList.innerHTML += `
        <div id="create-list-form" class="mt-3">
            <h3>Create New List</h3>
            <input type="text" id="new-list-name" class="form-control" placeholder="Enter list name">
            <div class="form-check mt-2">
                <input type="checkbox" id="new-list-public" class="form-check-input">
                <label for="new-list-public" class="form-check-label">Make list public</label>
            </div>
            <button onclick="createList()" class="btn btn-success mt-2">Create List</button>
        </div>
    `;
}

function createList() {
    const listName = document.getElementById('new-list-name').value;
    const isPublic = document.getElementById('new-list-public').checked;
    if (!listName) {
        alert('Please enter a list name');
        return;
    }

    console.log('Creating new list:', listName, 'Public:', isPublic);
    fetch('/api/lists', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: listName, is_public: isPublic }),
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => {
        console.log('Create list response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Create list response:', data);
        alert(data.message);
        loadListList();
    })
    .catch(error => {
        console.error('Error creating list:', error);
        alert('Failed to create list. Please try again.');
    });
}

let currentListId;

function loadListDetails(listId) {
    currentListId = listId;
    console.log('Loading list details for id:', listId);
    fetch(`/api/lists/${listId}`, {
        method: 'GET',
        credentials: 'include'
    })
        .then(handleUnauthorized)
        .then(response => {
            console.log('List details response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(list => {
            console.log('Received list details:', list);
            const listDetails = document.getElementById('list-details');
            listDetails.innerHTML = `
                <h2>${list.name}</h2>
                <p>Books: ${list.books.length}</p>
                <p>Read Percentage: ${list.read_percentage.toFixed(1)}%</p>
                <p>Status: ${list.is_public ? 'Public' : 'Private'}</p>
                <button onclick="toggleListVisibility(${list.id}, ${!list.is_public})" class="btn btn-sm ${list.is_public ? 'btn-warning' : 'btn-success'}">
                    Make ${list.is_public ? 'Private' : 'Public'}
                </button>
                <h3>Books:</h3>
                <ul class="list-group">
                    ${list.books.map(book => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="/book/${book.id}?id=${book.id}">${book.title}</a> by <a href="/author/${book.author_id}">${book.author}</a>
                            <button onclick="toggleReadStatus(${book.id}, ${!book.is_read})" class="btn btn-sm ${book.is_read ? 'btn-secondary' : 'btn-success'}">
                                Mark as ${book.is_read ? 'Unread' : 'Read'}
                            </button>
                            <button onclick="removeBookFromList(${book.id})" class="btn btn-sm btn-danger">Remove</button>
                        </li>
                    `).join('')}
                </ul>
                <button onclick="showAddBookForm()" class="btn btn-primary mt-3">Add Book to List</button>
            `;
        })
        .catch(error => {
            console.error('Error fetching list details:', error);
            const listDetails = document.getElementById('list-details');
            listDetails.innerHTML = `<p>Error loading list details: ${error.message}. Please try again.</p>`;
        });
}

function toggleListVisibility(listId, isPublic) {
    fetch(`/api/lists/${listId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_public: isPublic }),
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(() => {
        loadListList();
        if (currentListId) {
            loadListDetails(currentListId);
        }
    })
    .catch(error => {
        console.error('Error updating list visibility:', error);
        alert('Failed to update list visibility. Please try again.');
    });
}

function toggleReadStatus(bookId, isRead) {
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
    .then(() => loadListDetails(currentListId))
    .catch(error => {
        console.error('Error updating book read status:', error);
        alert('Failed to update book status. Please try again.');
    });
}

function removeBookFromList(bookId) {
    fetch(`/api/lists/${currentListId}/books/${bookId}`, {
        method: 'DELETE',
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(() => loadListDetails(currentListId))
    .catch(error => {
        console.error('Error removing book from list:', error);
        alert('Failed to remove book from list. Please try again.');
    });
}

function showAddBookForm() {
    const listDetails = document.getElementById('list-details');
    listDetails.innerHTML += `
        <div id="add-book-form" class="mt-3">
            <h3>Add Book to List</h3>
            <input type="text" id="book-search" class="form-control" placeholder="Search for a book">
            <ul id="book-search-results" class="list-group mt-2"></ul>
        </div>
    `;

    document.getElementById('book-search').addEventListener('input', debounce(searchBooks, 300));
}

function debounce(func, delay) {
    let debounceTimer;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(context, args), delay);
    }
}

function searchBooks() {
    const query = document.getElementById('book-search').value;
    if (query.length < 2) return;

    fetch(`/api/books?search=${encodeURIComponent(query)}`, {
        method: 'GET',
        credentials: 'include'
    })
        .then(handleUnauthorized)
        .then(response => response.json())
        .then(books => {
            const searchResults = document.getElementById('book-search-results');
            searchResults.innerHTML = books.map(book => `
                <li class="list-group-item">
                    ${book.title} by ${book.author}
                    <button onclick="addBookToList(${book.id})" class="btn btn-sm btn-primary float-end">Add</button>
                </li>
            `).join('');
        })
        .catch(error => {
            console.error('Error searching books:', error);
            alert('Failed to search books. Please try again.');
        });
}

function addBookToList(bookId) {
    fetch(`/api/lists/${currentListId}/books`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ book_id: bookId }),
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(() => {
        alert('Book added to list successfully');
        loadListDetails(currentListId);
    })
    .catch(error => {
        console.error('Error adding book to list:', error);
        alert('Failed to add book to list. Please try again.');
    });
}

function searchLists() {
    const searchQuery = document.getElementById('list-search').value;
    loadListList(searchQuery);
}

function deleteList(listId) {
    if (confirm('Are you sure you want to delete this list? This action cannot be undone.')) {
        fetch(`/api/lists/${listId}`, {
            method: 'DELETE',
            credentials: 'include'
        })
        .then(handleUnauthorized)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete list');
            }
            return response.json();
        })
        .then(data => {
            alert(data.message);
            loadListList();
        })
        .catch(error => {
            console.error('Error deleting list:', error);
            alert('Failed to delete list. Please try again.');
        });
    }
}

function isAdmin() {
    return true;
}
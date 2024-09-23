function handleUnauthorized(response) {
    if (response.status === 401) {
        console.log('Unauthorized access, redirecting to login');
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        throw new Error('Unauthorized');
    }
    return response;
}

function loadBooks(searchQuery = '') {
    console.log('Loading books...');
    fetch(`/api/books?search=${encodeURIComponent(searchQuery)}`, {
        method: 'GET',
        credentials: 'include'
    })
        .then(handleUnauthorized)
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(books => {
            console.log('Received books:', books);
            const bookList = document.getElementById('book-list');
            bookList.innerHTML = '';
            books.forEach(book => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <div class="book-item">
                        <img src="${book.cover_image_url || '/static/images/default-cover.jpg'}" alt="${book.title} cover" class="book-cover">
                        <div class="book-info">
                            <span>${book.title} by ${book.author}</span>
                            <input type="checkbox" ${book.is_read ? 'checked' : ''} onchange="updateBookStatus(${book.id}, this.checked)">
                            <button onclick="showBookDetails(${book.id})">Details</button>
                            <button onclick="deleteBook(${book.id})">Delete</button>
                            <select onchange="addBookToList(${book.id}, this.value)">
                                <option value="">Add to list</option>
                            </select>
                        </div>
                    </div>
                `;
                bookList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error loading books:', error);
        });
}

let isSubmitting = false;

function addBook(title, author) {
    if (isSubmitting) return;
    isSubmitting = true;
    console.log('Adding book:', title, 'by', author);
    fetch('/api/books', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, author }),
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('API response:', data);
        loadBooks();
        document.getElementById('add-book-form').reset();
    })
    .catch(error => {
        console.error('Error adding book:', error);
        alert('Failed to add book. Please try again.');
    })
    .finally(() => {
        isSubmitting = false;
    });
}

function updateBookStatus(id, isRead) {
    fetch(`/api/books/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: isRead }),
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(() => loadBooks());
}

function deleteBook(id) {
    fetch(`/api/books/${id}`, {
        method: 'DELETE',
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(() => loadBooks());
}

function showBookDetails(id) {
    fetch(`/api/books/${id}`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(book => {
        const bookDetails = document.getElementById('book-details');
        bookDetails.innerHTML = `
            <h2>${book.title}</h2>
            <p>Author: ${book.author}</p>
            <img src="${book.cover_image_url || '/static/images/default-cover.jpg'}" alt="${book.title} cover" class="book-cover">
            <p>ISBN: ${book.isbn || 'N/A'}</p>
            <p>Page Count: ${book.page_count || 'N/A'}</p>
            <p>Published Date: ${book.published_date || 'N/A'}</p>
            <p>Description: ${book.description || 'No description available.'}</p>
            <p>Status: ${book.is_read ? 'Read' : 'Unread'}</p>
        `;
    })
    .catch(error => {
        console.error('Error fetching book details:', error);
    });
}

function loadLists() {
    fetch('/api/lists', {
        method: 'GET',
        credentials: 'include'
    })
        .then(handleUnauthorized)
        .then(response => response.json())
        .then(lists => {
            const listSelects = document.querySelectorAll('select');
            lists.forEach(list => {
                listSelects.forEach(select => {
                    const option = document.createElement('option');
                    option.value = list.id;
                    option.textContent = list.name;
                    select.appendChild(option);
                });
            });
        });
}

function addBookToList(bookId, listId) {
    if (!listId) return;
    fetch(`/api/lists/${listId}/books`, {
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
        loadBooks();
    })
    .catch(error => {
        console.error('Error adding book to list:', error);
        alert('Failed to add book to list. Please try again.');
    });
}

function searchBooks() {
    const searchQuery = document.getElementById('book-search').value;
    loadBooks(searchQuery);
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded');
    loadBooks();
    setupEventListeners();
    loadLists();
});

function loadBooks() {
    console.log('Loading books...');
    fetch('https://c3e4260a-6536-436d-a00a-a2ad1e9344db-00-1gx8hgbvt0nyh.picard.replit.dev/api/books')
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
                    <span>${book.title} by ${book.author}</span>
                    <input type="checkbox" ${book.is_read ? 'checked' : ''} onchange="updateBookStatus(${book.id}, this.checked)">
                    <button onclick="showBookDetails(${book.id})">Details</button>
                    <button onclick="deleteBook(${book.id})">Delete</button>
                    <select onchange="addBookToList(${book.id}, this.value)">
                        <option value="">Add to list</option>
                    </select>
                `;
                bookList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error loading books:', error);
        });
}

function setupEventListeners() {
    console.log('Setting up event listeners');
    const addBookForm = document.getElementById('add-book-form');
    if (addBookForm) {
        addBookForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('Form submitted');
            const title = document.getElementById('book-title').value;
            const author = document.getElementById('book-author').value;
            addBook(title, author);
        });
    } else {
        console.error('Add book form not found');
    }
}

function addBook(title, author) {
    console.log('Attempting to add book:', title, 'by', author);
    fetch('https://c3e4260a-6536-436d-a00a-a2ad1e9344db-00-1gx8hgbvt0nyh.picard.replit.dev/api/books', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, author }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Book added successfully:', data);
        loadBooks();
        document.getElementById('add-book-form').reset();
    })
    .catch(error => {
        console.error('Error adding book:', error);
        alert('Failed to add book. Please try again.');
    });
}

function updateBookStatus(id, isRead) {
    fetch(`https://c3e4260a-6536-436d-a00a-a2ad1e9344db-00-1gx8hgbvt0nyh.picard.replit.dev/api/books/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: isRead }),
    })
    .then(response => response.json())
    .then(() => loadBooks());
}

function deleteBook(id) {
    fetch(`https://c3e4260a-6536-436d-a00a-a2ad1e9344db-00-1gx8hgbvt0nyh.picard.replit.dev/api/books/${id}`, {
        method: 'DELETE',
    })
    .then(() => loadBooks());
}

function showBookDetails(id) {
    fetch(`https://c3e4260a-6536-436d-a00a-a2ad1e9344db-00-1gx8hgbvt0nyh.picard.replit.dev/api/books/${id}`)
        .then(response => response.json())
        .then(book => {
            const detailsDiv = document.getElementById('book-details');
            detailsDiv.innerHTML = `
                <h3>${book.title}</h3>
                <p>Author: ${book.author}</p>
                <p>Status: ${book.is_read ? 'Read' : 'Unread'}</p>
                <p>Lists: ${book.lists.join(', ') || 'None'}</p>
            `;
        });
}

function loadLists() {
    fetch('https://c3e4260a-6536-436d-a00a-a2ad1e9344db-00-1gx8hgbvt0nyh.picard.replit.dev/api/lists')
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
    fetch(`https://c3e4260a-6536-436d-a00a-a2ad1e9344db-00-1gx8hgbvt0nyh.picard.replit.dev/api/lists/${listId}/books`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ book_id: bookId }),
    })
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

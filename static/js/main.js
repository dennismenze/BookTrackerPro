document.addEventListener('DOMContentLoaded', () => {
    loadBooks();
    setupEventListeners();
});

function loadBooks() {
    fetch('/api/books')
        .then(response => response.json())
        .then(books => {
            const bookList = document.getElementById('book-list');
            bookList.innerHTML = '';
            books.forEach(book => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span>${book.title} by ${book.author}</span>
                    <input type="checkbox" ${book.is_read ? 'checked' : ''} onchange="updateBookStatus(${book.id}, this.checked)">
                    <button onclick="deleteBook(${book.id})">Delete</button>
                `;
                bookList.appendChild(li);
            });
        });
}

function setupEventListeners() {
    const addBookForm = document.getElementById('add-book-form');
    addBookForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const title = document.getElementById('book-title').value;
        const author = document.getElementById('book-author').value;
        addBook(title, author);
    });
}

function addBook(title, author) {
    fetch('/api/books', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, author }),
    })
    .then(response => response.json())
    .then(() => {
        loadBooks();
        document.getElementById('add-book-form').reset();
    });
}

function updateBookStatus(id, isRead) {
    fetch(`/api/books/${id}`, {
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
    fetch(`/api/books/${id}`, {
        method: 'DELETE',
    })
    .then(() => loadBooks());
}

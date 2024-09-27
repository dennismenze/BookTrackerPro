document.addEventListener('DOMContentLoaded', () => {
    const authorId = document.getElementById('author-details').dataset.authorId;
    if (authorId) {
        loadAuthorDetails(authorId);
    } else {
        console.error('Author ID not found');
        document.getElementById('author-details').innerHTML = '<p class="text-red-500">Error: Author ID not provided. Please go back and try again.</p>';
    }
});

function loadAuthorDetails(authorId) {
    fetch(`/api/authors/${authorId}`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(author => {
        document.getElementById('author-name').textContent = author.name;
        document.getElementById('total-books').textContent = `Total Books: ${author.total_books}`;
        document.getElementById('read-books').textContent = `Read Books: ${author.read_books}`;
        document.getElementById('read-percentage').textContent = `Read Percentage: ${author.read_percentage.toFixed(1)}%`;
        document.getElementById('total-main-works').textContent = `Total Main Works: ${author.total_main_works}`;
        document.getElementById('read-main-works').textContent = `Read Main Works: ${author.read_main_works}`;
        document.getElementById('read-main-works-percentage').textContent = `Read Main Works Percentage: ${author.read_main_works_percentage.toFixed(1)}%`;

        const bookList = document.getElementById('book-list');
        bookList.innerHTML = author.books.map(book => `
            <div class="book-item bg-gray-100 p-4 rounded-lg shadow ${book.is_read ? 'opacity-50' : ''}">
                <img src="${book.cover_image_url || '/static/images/no-cover.png'}" alt="${book.title} cover" class="w-full h-48 object-cover rounded-md mb-2">
                <h3 class="font-semibold text-lg mb-1">${book.title}</h3>
                ${book.is_main_work ? '<span class="inline-block bg-yellow-200 text-yellow-800 text-xs px-2 py-1 rounded-full mb-2">Main Work</span>' : ''}
                <button class="toggle-read-status w-full px-2 py-1 rounded ${book.is_read ? 'bg-green-500' : 'bg-yellow-500'} text-white flex items-center justify-center"
                        data-book-id="${book.id}" data-is-read="${book.is_read}">
                    <i class="fas fa-eye${book.is_read ? '' : '-slash'} mr-2"></i>
                    ${book.is_read ? 'Read' : 'Unread'}
                </button>
            </div>
        `).join('');

        setupEventListeners();
    })
    .catch(error => {
        console.error('Error fetching author details:', error);
        document.getElementById('author-details').innerHTML = `<p class="text-red-500">Error loading author details: ${error.message}. Please try again.</p>`;
    });
}

function setupEventListeners() {
    document.querySelectorAll('.toggle-read-status').forEach(button => {
        button.addEventListener('click', (e) => {
            const bookId = e.target.dataset.bookId;
            const isRead = e.target.dataset.isRead === 'true';
            toggleReadStatus(bookId, !isRead);
        });
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
    .then(() => {
        const authorId = document.getElementById('author-details').dataset.authorId;
        loadAuthorDetails(authorId);
    })
    .catch(error => {
        console.error('Error updating book read status:', error);
        alert('Failed to update book status. Please try again.');
    });
}

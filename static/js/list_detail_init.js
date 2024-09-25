document.addEventListener('DOMContentLoaded', () => {
    const listId = document.getElementById('list-details').dataset.listId;
    if (listId) {
        loadListDetails(listId);
    } else {
        console.error('List ID not found');
        document.getElementById('list-details').innerHTML = '<p class="text-red-500">Error: List ID not provided. Please go back and try again.</p>';
    }
});

function loadListDetails(listId) {
    fetch(`/api/lists/${listId}`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(list => {
        document.getElementById('list-name').textContent = list.name;
        document.getElementById('book-count').textContent = `Books: ${list.books.length}`;
        document.getElementById('read-percentage').textContent = `Read: ${list.read_percentage.toFixed(1)}%`;
        document.getElementById('list-visibility').textContent = `Visibility: ${list.is_public ? 'Public' : 'Private'}`;

        const bookList = document.getElementById('book-list');
        bookList.innerHTML = list.books.map(book => `
            <li class="flex items-center justify-between bg-gray-100 p-2 rounded">
                <div>
                    <a href="/book/${book.id}" class="text-blue-600 hover:underline">${book.title}</a>
                    <span class="text-gray-600 text-sm ml-2">by ${book.author}</span>
                </div>
                <button class="toggle-read-status px-2 py-1 rounded ${book.is_read ? 'bg-green-500' : 'bg-yellow-500'} text-white"
                        data-book-id="${book.id}" data-is-read="${book.is_read}">
                    ${book.is_read ? 'Read' : 'Unread'}
                </button>
            </li>
        `).join('');

        setupEventListeners();
    })
    .catch(error => {
        console.error('Error fetching list details:', error);
        document.getElementById('list-details').innerHTML = `<p class="text-red-500">Error loading list details: ${error.message}. Please try again.</p>`;
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
        const listId = document.getElementById('list-details').dataset.listId;
        loadListDetails(listId);
    })
    .catch(error => {
        console.error('Error updating book read status:', error);
        alert('Failed to update book status. Please try again.');
    });
}

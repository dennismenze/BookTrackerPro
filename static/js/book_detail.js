document.addEventListener('DOMContentLoaded', () => {
    const bookId = document.getElementById('book-details').dataset.bookId;
    if (bookId) {
        loadBookDetails(bookId);
    } else {
        console.error('Book ID not found');
        document.getElementById('book-details').innerHTML = '<p class="text-red-500">Error: Book ID not provided. Please go back and try again.</p>';
    }
});

function loadBookDetails(bookId) {
    fetch(`/api/books/${bookId}`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(book => {
        document.getElementById('book-title').textContent = book.title;
        document.getElementById('book-author').innerHTML = `By <a href="/author/${book.author_id}" class="text-blue-600 hover:underline">${book.author}</a>`;
        document.getElementById('book-isbn').textContent = `ISBN: ${book.isbn || 'N/A'}`;
        document.getElementById('book-page-count').textContent = `Pages: ${book.page_count || 'N/A'}`;
        document.getElementById('book-published-date').textContent = `Published: ${book.published_date || 'N/A'}`;
        document.getElementById('book-description').textContent = book.description || 'No description available.';

        const bookCover = document.getElementById('book-cover');
        if (book.cover_image_url) {
            bookCover.src = book.cover_image_url;
            bookCover.alt = `${book.title} cover`;
        } else {
            bookCover.src = '/static/images/no-cover.png';
            bookCover.alt = 'No cover available';
        }

        const toggleReadStatusBtn = document.getElementById('toggle-read-status');
        toggleReadStatusBtn.textContent = book.is_read ? 'Mark as Unread' : 'Mark as Read';
        toggleReadStatusBtn.className = `w-full py-2 px-4 rounded text-white font-semibold ${book.is_read ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'}`;
        toggleReadStatusBtn.onclick = () => toggleReadStatus(bookId, !book.is_read);

        const bookLists = document.getElementById('book-lists');
        bookLists.innerHTML = book.lists.map(list => `
            <li><a href="/list/${list.id}" class="text-blue-600 hover:underline">${list.name}</a></li>
        `).join('');
    })
    .catch(error => {
        console.error('Error fetching book details:', error);
        document.getElementById('book-details').innerHTML = `<p class="text-red-500">Error loading book details: ${error.message}. Please try again.</p>`;
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
        loadBookDetails(bookId);
    })
    .catch(error => {
        console.error('Error updating book read status:', error);
        alert('Failed to update book status. Please try again.');
    });
}

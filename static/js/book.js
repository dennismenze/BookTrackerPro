function loadBookDetails(bookId) {
    fetch(`/api/books/${bookId}`)
        .then(response => response.json())
        .then(book => {
            const bookDetails = document.getElementById('book-details');
            bookDetails.innerHTML = `
                <h2>${book.title}</h2>
                <p>Author: <a href='/author/${book.author_id}'>${book.author}</a></p>
                <p>Status: ${book.is_read ? 'Read' : 'Unread'}</p>
                <p>Lists: ${book.lists.map(list => `<a href='/list/${list.id}'>${list.name}</a>`).join(', ') || 'Not in any list'}</p>
                <button onclick='toggleReadStatus(${book.id}, ${!book.is_read})'>
                    Mark as ${book.is_read ? 'Unread' : 'Read'}
                </button>
            `;
        });
}

function toggleReadStatus(bookId, isRead) {
    fetch(`/api/books/${bookId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: isRead }),
    })
    .then(response => response.json())
    .then(() => loadBookDetails(bookId));
}

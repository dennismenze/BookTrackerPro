document.addEventListener('DOMContentLoaded', function() {
    const bookItems = document.querySelectorAll('.book-item');

    bookItems.forEach(bookItem => {
        bookItem.addEventListener('click', function(event) {
            if (event.target.tagName !== 'A') {
                event.preventDefault();
                const bookId = this.dataset.bookId;
                const isRead = this.classList.contains('read');
                toggleReadStatus(bookId, !isRead);
            }
        });
    });

    function toggleReadStatus(bookId, newStatus) {
        fetch('/book/toggle_read_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ book_id: bookId, is_read: newStatus }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateBookItemStatus(bookId, newStatus);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function updateBookItemStatus(bookId, isRead) {
        const bookItem = document.querySelector(`.book-item[data-book-id="${bookId}"]`);
        if (bookItem) {
            bookItem.classList.toggle('read', isRead);
            const statusSpan = bookItem.querySelector('span');
            if (statusSpan) {
                statusSpan.textContent = isRead ? 'Read' : 'Unread';
                statusSpan.classList.toggle('text-green-600', isRead);
                statusSpan.classList.toggle('text-gray-500', !isRead);
            }
        }
    }
});

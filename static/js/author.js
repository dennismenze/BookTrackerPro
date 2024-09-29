document.addEventListener('DOMContentLoaded', function() {
    const bookItems = document.querySelectorAll('.book-item');
    const readBooksCount = document.getElementById('read-books-count');
    const readPercentage = document.getElementById('read-percentage');

    bookItems.forEach(bookItem => {
        const toggleButton = bookItem.querySelector('.toggle-read-status');
        toggleButton.addEventListener('click', function(event) {
            event.preventDefault();
            const bookId = bookItem.dataset.bookId;
            const isRead = bookItem.dataset.isRead === 'true';
            toggleReadStatus(bookId, !isRead);
        });
    });

    function toggleReadStatus(bookId, newStatus) {
        fetch('/author/toggle_read_status', {
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
                updateReadStats(data.read_books, data.read_percentage);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function updateBookItemStatus(bookId, isRead) {
        const bookItem = document.querySelector(`.book-item[data-book-id="${bookId}"]`);
        if (bookItem) {
            bookItem.dataset.isRead = isRead.toString();
            bookItem.classList.toggle('read', isRead);
            const icon = bookItem.querySelector('.toggle-read-status i');
            icon.classList.toggle('fa-eye', !isRead);
            icon.classList.toggle('fa-eye-slash', isRead);
        }
    }

    function updateReadStats(readBooks, readPercent) {
        if (readBooksCount) readBooksCount.textContent = readBooks;
        if (readPercentage) readPercentage.textContent = readPercent.toFixed(1);
    }
});

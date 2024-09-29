document.addEventListener('DOMContentLoaded', function() {
    const bookItems = document.querySelectorAll('.book-item');
    const readPercentage = document.getElementById('read-percentage');

    bookItems.forEach(bookItem => {
        const toggleButton = bookItem.querySelector('.toggle-read-status');
        toggleButton.addEventListener('click', function(event) {
            event.preventDefault();
            const bookId = bookItem.dataset.bookId;
            const isRead = bookItem.classList.contains('read');
            toggleReadStatus(bookId, !isRead);
        });
    });

    function toggleReadStatus(bookId, newStatus) {
        const listId = window.location.pathname.split('/').pop();
        fetch('/list/toggle_read_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ book_id: bookId, list_id: listId, is_read: newStatus }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateBookItemStatus(bookId, newStatus);
                updateReadPercentage(data.read_percentage);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function updateBookItemStatus(bookId, isRead) {
        const bookItem = document.querySelector(`.book-item[data-book-id="${bookId}"]`);
        if (bookItem) {
            bookItem.classList.toggle('read', isRead);
            const icon = bookItem.querySelector('.toggle-read-status i');
            icon.classList.toggle('fa-eye', !isRead);
            icon.classList.toggle('fa-eye-slash', isRead);
        }
    }

    function updateReadPercentage(percentage) {
        if (readPercentage) {
            readPercentage.textContent = percentage.toFixed(1);
        }
    }
});

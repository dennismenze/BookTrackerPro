document.addEventListener('DOMContentLoaded', function() {
    const bookItems = document.querySelectorAll('.book-item');
    const readBooksCount = document.getElementById('read-books-count');
    const readPercentage = document.getElementById('read-percentage');
    const readProgressBar = document.getElementById('read-progress-bar');
    const mainWorksReadCount = document.getElementById('main-works-read-count');
    const mainWorksReadPercentage = document.getElementById('main-works-read-percentage');
    const mainWorksProgressBar = document.getElementById('main-works-progress-bar');

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
                updateReadStats(data.read_books, data.read_percentage, data.main_works_read, data.main_works_read_percentage);
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

    function updateReadStats(readBooks, readPercent, mainWorksRead, mainWorksReadPercent) {
        if (readBooksCount) readBooksCount.textContent = readBooks;
        if (readPercentage) readPercentage.textContent = readPercent.toFixed(1);
        if (readProgressBar) readProgressBar.style.width = `${readPercent}%`;
        if (mainWorksReadCount) mainWorksReadCount.textContent = mainWorksRead;
        if (mainWorksReadPercentage) mainWorksReadPercentage.textContent = mainWorksReadPercent.toFixed(1);
        if (mainWorksProgressBar) mainWorksProgressBar.style.width = `${mainWorksReadPercent}%`;
    }
});

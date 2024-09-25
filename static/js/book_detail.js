document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const bookId = urlParams.get('id') || document.getElementById('book-details').dataset.bookId;
    if (bookId) {
        loadBookDetails(bookId);
    } else {
        console.error('Book ID not found');
        document.getElementById('book-details').innerHTML = '<p class="text-red-500">Error: Book ID not provided. Please go back and try again.</p>';
    }
});

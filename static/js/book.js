document.addEventListener('DOMContentLoaded', function() {
    const bookId = document.querySelector('[data-book-id]').dataset.bookId;

    fetch(`/book/book/${bookId}`)
        .then(response => response.json())
        .then(book => {
            document.getElementById('book-title').textContent = book.title;
            document.getElementById('book-author').textContent = book.author;
            document.getElementById('book-author').href = `/author/${book.author_id}`;
            document.getElementById('book-cover').src = book.cover_image_url || '/static/images/no-cover.png';
            document.getElementById('book-description').textContent = book.description;
            document.getElementById('book-isbn').textContent = book.isbn;
            document.getElementById('book-page-count').textContent = book.page_count;
            document.getElementById('book-published-date').textContent = book.published_date;
        })
        .catch(error => console.error('Error fetching book details:', error));
});

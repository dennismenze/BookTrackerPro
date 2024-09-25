document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired');
    loadBooks();
    const addBookForm = document.getElementById('add-book-form');
    addBookForm.addEventListener('submit', (e) => {
        console.log('Form submit event triggered');
        e.preventDefault();
        const title = document.getElementById('book-title').value;
        const author = document.getElementById('book-author').value;
        addBook(title, author);
    });
});

function addBook(title, author) {
    fetch('/api/books', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, author }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Book added:', data);
        loadBooks(); // Reload the book list
        document.getElementById('book-title').value = '';
        document.getElementById('book-author').value = '';
    })
    .catch(error => {
        console.error('Error adding book:', error);
        alert('Failed to add book. Please try again.');
    });
}

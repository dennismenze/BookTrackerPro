document.addEventListener('DOMContentLoaded', function() {
    const toggleButtons = document.querySelectorAll('.toggle-main-work');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.dataset.bookId;
            const isMainWork = this.dataset.isMainWork === 'true';
            fetch(`/api/books/${bookId}/toggle_main_work`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ is_main_work: !isMainWork }),
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_main_work) {
                    this.textContent = 'Main Work';
                    this.classList.remove('bg-gray-300');
                    this.classList.add('bg-green-500');
                } else {
                    this.textContent = 'Not Main Work';
                    this.classList.remove('bg-green-500');
                    this.classList.add('bg-gray-300');
                }
                this.dataset.isMainWork = data.is_main_work;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating the main work status.');
            });
        });
    });

    const addBookForm = document.getElementById('add-book-form');
    if (addBookForm) {
        addBookForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const title = document.getElementById('book-title').value;
            const author = document.getElementById('book-author').value;
            const isbn = document.getElementById('book-isbn').value;

            fetch('/api/books', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title, author, isbn }),
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    alert('Book added successfully');
                    location.reload(); // Reload the page to show the new book
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while adding the book.');
            });
        });
    }
});

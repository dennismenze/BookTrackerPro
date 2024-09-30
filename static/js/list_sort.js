document.addEventListener('DOMContentLoaded', function() {
    const bookList = document.getElementById('book-list');
    const sortSelect = document.getElementById('sort-select');
    const listId = bookList.dataset.listId;

    // Initialize Sortable
    const sortable = new Sortable(bookList, {
        animation: 150,
        onEnd: function(evt) {
            const bookIds = Array.from(bookList.children).map(li => li.dataset.bookId);
            updateRanks(bookIds);
        }
    });

    // Handle sorting dropdown changes
    sortSelect.addEventListener('change', function() {
        const sortBy = this.value;
        fetch(`/list/${listId}?sort=${sortBy}`)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newBookList = doc.getElementById('book-list');
                bookList.innerHTML = newBookList.innerHTML;
                updateRanks(Array.from(bookList.children).map(li => li.dataset.bookId));
            });
    });

    // Function to update ranks
    function updateRanks(bookIds) {
        fetch('/list/update_ranks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                list_id: listId,
                book_ids: bookIds
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Ranks updated successfully');
                // Update displayed ranks
                bookList.querySelectorAll('li').forEach((li, index) => {
                    li.querySelector('span').textContent = `Rank: ${index + 1}`;
                    li.dataset.rank = index + 1;
                });
            } else {
                console.error('Failed to update ranks:', data.error);
            }
        });
    }

    // Handle toggle read status
    bookList.addEventListener('click', function(e) {
        if (e.target.closest('.toggle-read-status')) {
            const bookItem = e.target.closest('.book-item');
            const bookId = bookItem.dataset.bookId;
            const isRead = !bookItem.classList.contains('read');

            fetch('/list/toggle_read_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    book_id: bookId,
                    list_id: listId,
                    is_read: isRead
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    bookItem.classList.toggle('read');
                    const icon = bookItem.querySelector('.toggle-read-status i');
                    icon.classList.toggle('fa-eye');
                    icon.classList.toggle('fa-eye-slash');
                    document.getElementById('read-percentage').textContent = data.read_percentage;
                }
            });
        }
    });

    // Handle remove book
    bookList.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-book')) {
            const bookItem = e.target.closest('.book-item');
            const bookId = bookItem.dataset.bookId;

            fetch('/list/remove_book_from_list', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    book_id: bookId,
                    list_id: listId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    bookItem.remove();
                    updateRanks(Array.from(bookList.children).map(li => li.dataset.bookId));
                } else {
                    console.error('Failed to remove book:', data.error);
                }
            });
        }
    });

    // Handle add book form
    const addBookForm = document.getElementById('add-book-form');
    const bookSearch = document.getElementById('book-search');
    const searchResults = document.getElementById('search-results');

    addBookForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = bookSearch.value;

        fetch(`/list/search_books?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(books => {
                searchResults.innerHTML = '';
                books.forEach(book => {
                    const bookElement = document.createElement('div');
                    bookElement.classList.add('book-result', 'p-2', 'border-b', 'cursor-pointer', 'hover:bg-gray-100');
                    bookElement.innerHTML = `
                        <h4 class="font-semibold">${book.title}</h4>
                        <p class="text-sm text-gray-600">${book.author}</p>
                    `;
                    bookElement.addEventListener('click', () => addBookToList(book.id));
                    searchResults.appendChild(bookElement);
                });
            });
    });

    function addBookToList(bookId) {
        fetch('/list/add_book_to_list', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                book_id: bookId,
                list_id: listId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Reload the page to show the updated list
            } else {
                console.error('Failed to add book:', data.error);
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const bookList = document.getElementById('book-list');
    const toggleVisibilityButton = document.getElementById('toggle-visibility');
    const sortSelect = document.getElementById('sort-select');

    if (bookList) {
        bookList.addEventListener('click', function(e) {
            if (e.target.classList.contains('toggle-read-status') || e.target.closest('.toggle-read-status')) {
                const button = e.target.classList.contains('toggle-read-status') ? e.target : e.target.closest('.toggle-read-status');
                const listItem = button.closest('li');
                const bookId = listItem.dataset.bookId;
                const listId = bookList.dataset.listId;
                const isRead = !listItem.classList.contains('read');

                fetch('/list/toggle_read_status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ book_id: bookId, list_id: listId, is_read: isRead }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        listItem.classList.toggle('read');
                        const icon = button.querySelector('i');
                        icon.classList.toggle('fa-eye');
                        icon.classList.toggle('fa-eye-slash');

                        // Update progress bars and counts
                        document.getElementById('read-progress-bar').style.width = `${data.read_percentage}%`;
                        document.getElementById('read-books-count').textContent = data.read_books;
                        document.getElementById('read-percentage').textContent = Math.round(data.read_percentage);

                        document.getElementById('main-works-progress-bar').style.width = `${data.main_works_read_percentage}%`;
                        document.getElementById('main-works-read-count').textContent = data.main_works_read;
                        document.getElementById('main-works-read-percentage').textContent = Math.round(data.main_works_read_percentage);
                    }
                });
            }

            if (e.target.classList.contains('remove-book')) {
                const listItem = e.target.closest('li');
                const bookId = listItem.dataset.bookId;
                const listId = bookList.dataset.listId;

                fetch('/list/remove_book_from_list', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ book_id: bookId, list_id: listId }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        listItem.remove();
                    }
                });
            }
        });
    }

    if (toggleVisibilityButton) {
        toggleVisibilityButton.addEventListener('click', function() {
            const listId = this.dataset.listId;
            const isPublic = this.dataset.isPublic === 'true';

            fetch('/list/toggle_visibility', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ list_id: listId, is_public: !isPublic }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.dataset.isPublic = data.is_public.toString();
                    this.previousElementSibling.textContent = data.is_public ? 'Public' : 'Private';
                }
            });
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('sort', this.value);
            currentUrl.searchParams.set('page', '1');  // Reset to first page when sorting
            window.location.href = currentUrl.toString();
        });
    }

    const addBookForm = document.getElementById('add-book-form');
    const bookSearch = document.getElementById('book-search');
    const searchResults = document.getElementById('search-results');

    if (addBookForm) {
        addBookForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = bookSearch.value;

            fetch(`/list/search_books?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                searchResults.innerHTML = '';
                data.forEach(book => {
                    const bookElement = document.createElement('div');
                    bookElement.classList.add('book-result', 'flex', 'items-center', 'justify-between', 'p-2', 'border-b');
                    bookElement.innerHTML = `
                        <div>
                            <img src="${book.cover_image_url || '/static/images/no-cover.png'}" alt="${book.title} cover" class="w-12 h-16 object-cover mr-2 inline-block">
                            <span>${book.title} by ${book.author}</span>
                        </div>
                        <button class="add-book bg-green-500 text-white p-1 rounded" data-book-id="${book.id}">Add</button>
                    `;
                    searchResults.appendChild(bookElement);
                });
            });
        });

        searchResults.addEventListener('click', function(e) {
            if (e.target.classList.contains('add-book')) {
                const bookId = e.target.dataset.bookId;
                const listId = bookList.dataset.listId;

                fetch('/list/add_book_to_list', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ book_id: bookId, list_id: listId }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();  // Refresh the page to show the updated list
                    }
                });
            }
        });
    }
});

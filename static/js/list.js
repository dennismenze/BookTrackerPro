document.addEventListener('DOMContentLoaded', function() {
    const bookItems = document.querySelectorAll('.book-item');
    const readPercentage = document.getElementById('read-percentage');
    const readProgressBar = document.getElementById('read-progress-bar');
    const mainWorksReadCount = document.getElementById('main-works-read-count');
    const mainWorksReadPercentage = document.getElementById('main-works-read-percentage');
    const mainWorksProgressBar = document.getElementById('main-works-progress-bar');
    const addBookForm = document.getElementById('add-book-form');
    const bookSearchInput = document.getElementById('book-search');
    const searchResults = document.getElementById('search-results');
    const sortSelect = document.getElementById('sort-select');
    const toggleVisibilityButton = document.getElementById('toggle-visibility');

    bookItems.forEach(bookItem => {
        const toggleButton = bookItem.querySelector('.toggle-read-status');
        toggleButton.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            const bookId = bookItem.dataset.bookId;
            const isRead = bookItem.classList.contains('read');
            toggleReadStatus(bookId, !isRead);
        });

        const removeButton = bookItem.querySelector('.remove-book');
        if (removeButton) {
            removeButton.addEventListener('click', function(event) {
                event.preventDefault();
                event.stopPropagation();
                const bookId = bookItem.dataset.bookId;
                removeBookFromList(bookId);
            });
        }
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
                updateReadStats(data.read_percentage, data.main_works_read, data.main_works_read_percentage);
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

    function updateReadStats(readPercent, mainWorksRead, mainWorksReadPercent) {
        if (readPercentage) readPercentage.textContent = readPercent.toFixed(1);
        if (readProgressBar) readProgressBar.style.width = `${readPercent}%`;
        if (mainWorksReadCount) mainWorksReadCount.textContent = mainWorksRead;
        if (mainWorksReadPercentage) mainWorksReadPercentage.textContent = mainWorksReadPercent.toFixed(1);
        if (mainWorksProgressBar) mainWorksProgressBar.style.width = `${mainWorksReadPercent}%`;
    }

    addBookForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const query = bookSearchInput.value.trim();
        if (query) {
            searchBooks(query);
        }
    });

    function searchBooks(query) {
        fetch(`/list/search_books?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(books => {
                displaySearchResults(books);
            })
            .catch(error => console.error('Error:', error));
    }

    function displaySearchResults(books) {
        searchResults.innerHTML = '';
        books.forEach(book => {
            const bookElement = document.createElement('div');
            bookElement.className = 'flex items-center justify-between p-2 border-b';
            bookElement.innerHTML = `
                <div>
                    <img src="${book.cover_image_url || '/static/images/no-cover.png'}" alt="${book.title} cover" class="w-12 h-16 object-cover mr-2 inline-block">
                    <span>${book.title} by ${book.author}</span>
                </div>
                <button class="add-book-button bg-green-500 text-white p-1 rounded" data-book-id="${book.id}">Add</button>
            `;
            searchResults.appendChild(bookElement);
        });

        const addButtons = searchResults.querySelectorAll('.add-book-button');
        addButtons.forEach(button => {
            button.addEventListener('click', function() {
                const bookId = this.dataset.bookId;
                addBookToList(bookId);
            });
        });
    }

    function addBookToList(bookId) {
        const listId = window.location.pathname.split('/').pop();
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
                location.reload();
            } else {
                console.error(data.error || 'Failed to add book to list');
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function removeBookFromList(bookId) {
        const listId = window.location.pathname.split('/').pop();
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
                location.reload();
            } else {
                console.error(data.error || 'Failed to remove book from list');
            }
        })
        .catch(error => console.error('Error:', error));
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('sort', this.value);
            window.location.href = currentUrl.toString();
        });
    }

    if (toggleVisibilityButton) {
        toggleVisibilityButton.addEventListener('click', function() {
            const listId = this.dataset.listId;
            const isPublic = this.dataset.isPublic === 'true';
            toggleListVisibility(listId, !isPublic);
        });
    }

    function toggleListVisibility(listId, newStatus) {
        fetch('/list/toggle_visibility', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ list_id: listId, is_public: newStatus }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                toggleVisibilityButton.dataset.isPublic = newStatus.toString();
                const visibilityText = toggleVisibilityButton.previousElementSibling;
                visibilityText.textContent = newStatus ? 'Public' : 'Private';
            } else {
                console.error(data.error || 'Failed to update list visibility');
            }
        })
        .catch(error => console.error('Error:', error));
    }
});
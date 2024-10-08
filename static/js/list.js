document.addEventListener('DOMContentLoaded', function() {
    const bookList = document.getElementById('book-list');
    const toggleVisibilityButton = document.getElementById('toggle-visibility');
    const sortSelect = document.getElementById('sort-select');
    const bookSearchInput = document.getElementById('book-search');
    const bookDirectSearchInput = document.getElementById('book-direct-search');
    const paginationContainer = document.getElementById('pagination');

    function scrollToBook(bookId) {
        const bookElement = document.querySelector(`[data-book-id="${bookId}"]`);
        if (bookElement) {
            bookElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            bookElement.classList.add('highlight');
            setTimeout(() => bookElement.classList.remove('highlight'), 2000);
        }
    }

    const urlParams = new URLSearchParams(window.location.search);
    const bookIdFromUrl = urlParams.get('book_id');
    if (bookIdFromUrl) {
        scrollToBook(bookIdFromUrl);
    }

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

            const bookLink = e.target.closest('a[href^="/book/"]');
            if (bookLink) {
                e.preventDefault();
                const bookId = bookLink.closest('li').dataset.bookId;
                const listId = bookList.dataset.listId;
                const currentUrl = new URL(bookLink.href);
                currentUrl.searchParams.append('ref_list_id', listId);
                currentUrl.searchParams.append('ref_book_id', bookId);
                window.location.href = currentUrl.toString();
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
            currentUrl.searchParams.set('page', '1');
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
                        location.reload();
                    }
                });
            }
        });
    }

    if (bookSearchInput) {
        bookSearchInput.addEventListener('input', function() {
            const searchTerm = this.value.trim();
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('search', searchTerm);
            currentUrl.searchParams.set('page', '1');
            
            history.pushState(null, '', currentUrl.toString());
            
            fetchBooks(currentUrl);
        });
    }

    if (bookDirectSearchInput) {
        bookDirectSearchInput.addEventListener('input', debounce(function() {
            const searchTerm = this.value.trim();
            if (searchTerm.length > 2) {
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('direct_search', searchTerm);
                
                fetch(currentUrl.toString())
                    .then(response => response.json())
                    .then(data => {
                        if (data.book_found) {
                            const bookElement = document.querySelector(`[data-book-id="${data.book_id}"]`);
                            if (bookElement) {
                                bookElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                bookElement.classList.add('highlight');
                                setTimeout(() => bookElement.classList.remove('highlight'), 2000);
                            }
                        }
                    });
            }
        }, 300));
    }

    function fetchBooks(url) {
        fetch(url)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                const newBookList = doc.getElementById('book-list');
                if (newBookList) {
                    bookList.innerHTML = newBookList.innerHTML;
                }
                
                const newPagination = doc.getElementById('pagination');
                if (newPagination && paginationContainer) {
                    paginationContainer.innerHTML = newPagination.innerHTML;
                }
                
                updatePageContent(doc);
            })
            .catch(error => console.error('Error fetching books:', error));
    }

    function updatePageContent(newDoc) {
        const readPercentage = newDoc.getElementById('read-percentage');
        if (readPercentage) {
            document.getElementById('read-percentage').textContent = readPercentage.textContent;
        }

        const mainWorksReadPercentage = newDoc.getElementById('main-works-read-percentage');
        if (mainWorksReadPercentage) {
            document.getElementById('main-works-read-percentage').textContent = mainWorksReadPercentage.textContent;
        }

        const totalBooks = newDoc.getElementById('total-books');
        if (totalBooks) {
            document.getElementById('total-books').textContent = totalBooks.textContent;
        }
    }

    if (paginationContainer) {
        paginationContainer.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                e.preventDefault();
                const url = new URL(e.target.href);
                fetchBooks(url);
                history.pushState(null, '', url.toString());
            }
        });
    }

    window.addEventListener('popstate', function() {
        fetchBooks(new URL(window.location.href));
    });

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
});
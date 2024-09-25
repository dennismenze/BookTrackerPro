function handleUnauthorized(response) {
    if (response.status === 401) {
        console.log('Unauthorized access, redirecting to login');
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        throw new Error('Unauthorized');
    }
    return response;
}

function loadBookDetails(bookId) {
    console.log('Loading book details for id:', bookId);
    fetch(`/api/books/${bookId}`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => {
        console.log('Book details response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(book => {
        console.log('Received book details:', book);
        console.log('Cover image URL:', book.cover_image_url);
        const bookDetails = document.getElementById('book-details');
        bookDetails.innerHTML = `
            <h2 class="text-2xl font-bold mb-4">${book.title}</h2>
            <div class="flex flex-col md:flex-row">
                <div class="md:w-1/3 mb-4 md:mb-0">
                    ${book.cover_image_url && book.cover_image_url.trim() !== ''
                        ? `<img src="${book.cover_image_url}" alt="${book.title} cover" class="w-full rounded-lg shadow-lg">`
                        : `<div class="w-full h-64 bg-gray-200 flex items-center justify-center rounded-lg shadow-lg">
                               <span class="text-gray-500">No cover available</span>
                           </div>`
                    }
                </div>
                <div class="md:w-2/3 md:pl-6">
                    <p><strong>Author:</strong> <a href="/author/${book.author_id}" class="text-blue-500 hover:underline">${book.author}</a></p>
                    <p><strong>ISBN:</strong> ${book.isbn || 'N/A'}</p>
                    <p><strong>Page Count:</strong> ${book.page_count || 'N/A'}</p>
                    <p><strong>Published Date:</strong> ${book.published_date || 'N/A'}</p>
                    <p><strong>Status:</strong> ${book.is_read ? 'Read' : 'Unread'}</p>
                    <div class="mt-4">
                        <h3 class="text-xl font-semibold mb-2">Description:</h3>
                        <p>${book.description || 'No description available.'}</p>
                    </div>
                    <div class="mt-4">
                        <h3 class="text-xl font-semibold mb-2">Lists:</h3>
                        <ul>
                            ${book.lists.map(list => `<li>${list.name}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="mt-4">
                        <button class="toggle-read-status bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" data-book-id="${book.id}" data-is-read="${!book.is_read}">
                            Mark as ${book.is_read ? 'Unread' : 'Read'}
                        </button>
                    </div>
                </div>
            </div>
        `;
        console.log('Book details HTML updated');
        setupBookEventListeners();
    })
    .catch(error => {
        console.error('Error fetching book details:', error);
        const bookDetails = document.getElementById('book-details');
        bookDetails.innerHTML = `<p class="text-red-500">Error loading book details: ${error.message}. Please try again.</p>`;
    });
}

function toggleReadStatus(bookId, isRead) {
    fetch(`/api/books/${bookId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: isRead }),
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(() => {
        loadBookDetails(bookId);
        loadBooks();
    })
    .catch(error => {
        console.error('Error updating book status:', error);
        alert('Failed to update book status. Please try again.');
    });
}

function loadBooks() {
    console.log('Loading books...');
    fetch('/api/books', {
        method: 'GET',
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => {
        console.log('Books response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(books => {
        console.log('Received books:', books);
        const bookList = document.getElementById('book-list');
        if (books.length === 0) {
            bookList.innerHTML = '<p>You have not read any books yet.</p>';
        } else {
            bookList.innerHTML = books.map(book => `
                <li class="mb-4">
                    <div class="flex items-center">
                        ${book.cover_image_url 
                            ? `<img src="${book.cover_image_url}" alt="${book.title} cover" class="w-16 h-24 object-cover mr-4">`
                            : `<div class="w-16 h-24 bg-gray-200 flex items-center justify-center mr-4">
                                   <span class="text-xs text-gray-500">No cover</span>
                               </div>`
                        }
                        <div>
                            <h3 class="text-lg font-semibold">${book.title}</h3>
                            <p class="text-gray-600">${book.author}</p>
                            <button class="view-book-details text-blue-500 hover:underline" data-book-id="${book.id}">View Details</button>
                        </div>
                    </div>
                </li>
            `).join('');
        }
        setupBookEventListeners();
    })
    .catch(error => {
        console.error('Error fetching books:', error);
        const bookList = document.getElementById('book-list');
        bookList.innerHTML = `<p class="text-red-500">Error loading books: ${error.message}. Please try again.</p>`;
    });
}

function searchBooks() {
    const query = document.getElementById('book-search').value;
    console.log('Searching books with query:', query);
    fetch(`/api/books?search=${encodeURIComponent(query)}`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => {
        console.log('Search books response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(books => {
        console.log('Received search results:', books);
        const bookList = document.getElementById('book-list');
        if (books.length === 0) {
            bookList.innerHTML = '<p>No books found matching your search.</p>';
        } else {
            bookList.innerHTML = books.map(book => `
                <li class="mb-4">
                    <div class="flex items-center">
                        ${book.cover_image_url 
                            ? `<img src="${book.cover_image_url}" alt="${book.title} cover" class="w-16 h-24 object-cover mr-4">`
                            : `<div class="w-16 h-24 bg-gray-200 flex items-center justify-center mr-4">
                                   <span class="text-xs text-gray-500">No cover</span>
                               </div>`
                        }
                        <div>
                            <h3 class="text-lg font-semibold">${book.title}</h3>
                            <p class="text-gray-600">${book.author}</p>
                            <button class="view-book-details text-blue-500 hover:underline" data-book-id="${book.id}">View Details</button>
                        </div>
                    </div>
                </li>
            `).join('');
        }
        setupBookEventListeners();
    })
    .catch(error => {
        console.error('Error searching books:', error);
        const bookList = document.getElementById('book-list');
        bookList.innerHTML = `<p class="text-red-500">Error searching books: ${error.message}. Please try again.</p>`;
    });
}

function setupBookEventListeners() {
    document.querySelectorAll('.view-book-details').forEach(button => {
        button.addEventListener('click', (e) => {
            const bookId = e.target.dataset.bookId;
            loadBookDetails(bookId);
        });
    });

    document.querySelectorAll('.toggle-read-status').forEach(button => {
        button.addEventListener('click', (e) => {
            const bookId = e.target.dataset.bookId;
            const isRead = e.target.dataset.isRead === 'true';
            toggleReadStatus(bookId, isRead);
        });
    });

    const searchButton = document.querySelector('button[onclick="searchBooks()"]');
    if (searchButton) {
        searchButton.removeAttribute('onclick');
        searchButton.addEventListener('click', searchBooks);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadBooks();
    setupBookEventListeners();
});

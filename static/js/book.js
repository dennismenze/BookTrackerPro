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
        const bookDetails = document.getElementById('book-details');
        bookDetails.innerHTML = `
            <h2 class="text-2xl font-bold mb-4">${book.title}</h2>
            <div class="flex flex-col md:flex-row">
                <div class="md:w-1/3 mb-4 md:mb-0">
                    <img src="${book.cover_image_url || '/static/images/default-cover.jpg'}" alt="${book.title} cover" class="w-full rounded-lg shadow-lg">
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
                        <button onclick="toggleReadStatus(${book.id}, ${!book.is_read})" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                            Mark as ${book.is_read ? 'Unread' : 'Read'}
                        </button>
                    </div>
                </div>
            </div>
        `;
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
    })
    .catch(error => {
        console.error('Error updating book status:', error);
        alert('Failed to update book status. Please try again.');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const authorId = window.location.pathname.split('/').pop();
    
    fetch(`/api/authors/${authorId}`)
        .then(response => response.json())
        .then(data => {
            updateStatistics(data.books);
            renderBooks(data.books);
        })
        .catch(error => console.error('Error:', error));
});

function updateStatistics(books) {
    const totalBooks = books.length;
    const readBooks = books.filter(book => book.is_read).length;
    const percentage = totalBooks > 0 ? Math.round((readBooks / totalBooks) * 100) : 0;

    const totalPages = books.reduce((sum, book) => sum + (book.page_count || 0), 0);
    const readPages = books.filter(book => book.is_read).reduce((sum, book) => sum + (book.page_count || 0), 0);

    const ratings = books.filter(book => book.rating).map(book => book.rating);
    const averageRating = ratings.length > 0 ? (ratings.reduce((sum, rating) => sum + rating, 0) / ratings.length).toFixed(1) : 'N/A';

    document.getElementById('watched-count').textContent = readBooks;
    document.getElementById('total-count').textContent = totalBooks;
    document.getElementById('percentage').textContent = percentage;
    document.getElementById('progress-bar').style.width = `${percentage}%`;
    document.getElementById('pages-read').textContent = readPages;
    document.getElementById('average-rating').textContent = averageRating;

    // Update progress bar color based on percentage
    const progressBar = document.getElementById('progress-bar');
    if (percentage < 33) {
        progressBar.classList.remove('bg-blue-600', 'bg-green-600');
        progressBar.classList.add('bg-red-600');
    } else if (percentage < 66) {
        progressBar.classList.remove('bg-red-600', 'bg-green-600');
        progressBar.classList.add('bg-blue-600');
    } else {
        progressBar.classList.remove('bg-red-600', 'bg-blue-600');
        progressBar.classList.add('bg-green-600');
    }
}

function renderBooks(books) {
    const container = document.getElementById('books-container');
    container.innerHTML = '';

    books.forEach(book => {
        const bookElement = document.createElement('div');
        bookElement.className = 'bg-white shadow-md rounded-lg p-4';
        bookElement.innerHTML = `
            <img src="${book.cover_image_url || '/static/images/no-cover.png'}" alt="${book.title} cover" class="w-full h-48 object-cover mb-2">
            <h3 class="font-semibold">${book.title}</h3>
            <p class="text-sm text-gray-600">Pages: ${book.page_count || 'N/A'}</p>
            <p class="text-sm text-gray-600">Rating: ${book.rating ? book.rating.toFixed(1) : 'N/A'}</p>
            <button class="mt-2 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600" onclick="toggleReadStatus(${book.id}, this)">
                ${book.is_read ? 'Mark as Unread' : 'Mark as Read'}
            </button>
        `;
        container.appendChild(bookElement);
    });
}

function toggleReadStatus(bookId, button) {
    fetch(`/api/books/${bookId}/toggle-read`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                button.textContent = data.is_read ? 'Mark as Unread' : 'Mark as Read';
                // Refresh the statistics
                fetch(`/api/authors/${window.location.pathname.split('/').pop()}`)
                    .then(response => response.json())
                    .then(authorData => {
                        updateStatistics(authorData.books);
                    });
            }
        })
        .catch(error => console.error('Error:', error));
}

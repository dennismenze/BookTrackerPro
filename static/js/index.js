document.addEventListener('DOMContentLoaded', function() {
    fetchBooks();
    fetchAuthors();
});

function fetchBooks() {
    fetch('/api/books')
        .then(response => response.json())
        .then(books => {
            const bookList = document.getElementById('book-list');
            if (bookList) {
                bookList.innerHTML = books.map(book => `
                    <div class="bg-white shadow-md rounded-lg p-4">
                        <img src="${book.cover_image_url}" alt="${book.title} cover" class="w-full h-48 object-cover mb-2">
                        <h3 class="font-semibold">${book.title}</h3>
                        <p class="text-sm text-gray-600">${book.author}</p>
                        <p class="text-sm ${book.is_read ? 'text-green-600' : 'text-red-600'}">${book.is_read ? 'Read' : 'Unread'}</p>
                    </div>
                `).join('');
            }
        })
        .catch(error => console.error('Error fetching books:', error));
}

function fetchAuthors() {
    const searchQuery = new URLSearchParams(window.location.search).get('author_search') || '';
    fetch(`/api/authors?search=${searchQuery}`)
        .then(response => response.json())
        .then(authors => {
            const authorList = document.getElementById('author-list');
            if (authorList) {
                authorList.innerHTML = authors.map(author => `
                    <li class="bg-white shadow-md rounded-lg p-4">
                        <a href="/author/${author.id}" class="flex items-center">
                            <img src="${author.image_url}" alt="${author.name}" class="w-12 h-12 object-cover rounded-full mr-4">
                            <span class="text-blue-600 hover:text-blue-800">${author.name}</span>
                        </a>
                        <p class="text-sm text-gray-600 mt-2">Books: ${author.books_count}</p>
                    </li>
                `).join('');
            }
        })
        .catch(error => console.error('Error fetching authors:', error));
}

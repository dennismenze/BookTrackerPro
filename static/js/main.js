document.addEventListener('DOMContentLoaded', function() {
    // Fetch and display user's books
    fetch('/book/api/books')
        .then(response => response.json())
        .then(books => {
            const bookList = document.getElementById('book-list');
            if (bookList) {
                bookList.innerHTML = '';
                books.forEach(book => {
                    const bookElement = document.createElement('div');
                    bookElement.className = 'bg-white shadow-md rounded-lg p-4';
                    bookElement.innerHTML = `
                        <a href="/book/${book.id}">
                            <img src="${book.cover_image_url || '/static/images/no-cover.png'}" alt="${book.title} cover" class="h-48 object-cover mb-2">
                            <h3 class="font-semibold">${book.title}</h3>
                        </a>
                        <p class="text-sm text-gray-600">${book.author}</p>
                    `;
                    bookList.appendChild(bookElement);
                });
            }
        })
        .catch(error => console.error('Error fetching books:', error));

    // Fetch and display authors
    const searchAuthors = (query = '') => {
        fetch(`/author/api/authors?search=${query}`)
            .then(response => response.json())
            .then(authors => {
                const authorList = document.getElementById('author-list');
                if (authorList) {
                    authorList.innerHTML = '';
                    authors.forEach(author => {
                        const authorElement = document.createElement('li');
                        authorElement.className = 'bg-white shadow-md rounded-lg p-4';
                        authorElement.innerHTML = `
                            <a href="/author/${author.id}" class="flex items-center">
                                <img src="${author.image_url || '/static/images/default-author.png'}" alt="${author.name}" class="w-12 h-12 object-cover rounded-full mr-4">
                                <span class="text-blue-600 hover:text-blue-800">${author.name}</span>
                            </a>
                        `;
                        authorList.appendChild(authorElement);
                    });
                }
            })
            .catch(error => console.error('Error fetching authors:', error));
    };

    // Initial author search
    searchAuthors();

    // Add event listener for author search input
    const authorSearchInput = document.getElementById('author-search');
    if (authorSearchInput) {
        authorSearchInput.addEventListener('input', (e) => {
            searchAuthors(e.target.value);
        });
    }
});

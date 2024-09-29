document.addEventListener('DOMContentLoaded', function() {
    // Fetch and display user's books
    fetch('/book/api/books')
        .then(response => response.json())
        .then(books => {
            const bookList = document.getElementById('book-list');
            if (bookList) {
                books.forEach(book => {
                    const bookElement = document.createElement('div');
                    bookElement.innerHTML = `
                        <img src="${book.cover_image_url || '/static/images/no-cover.png'}" alt="${book.title} cover">
                        <h3>${book.title}</h3>
                        <p>${book.author}</p>
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
                        const authorElement = document.createElement('div');
                        authorElement.innerHTML = `
                            <img src="${author.image_url || '/static/images/default-author.png'}" alt="${author.name}">
                            <p>${author.name}</p>
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

document.addEventListener('DOMContentLoaded', function() {
    const authorId = document.querySelector('[data-author-id]').dataset.authorId;

    fetch(`/author/author/${authorId}`)
        .then(response => response.json())
        .then(author => {
            document.getElementById('author-name').textContent = author.name;
            document.getElementById('author-image').src = author.image_url || '/static/images/default-author.png';

            const booksList = document.getElementById('author-books');
            booksList.innerHTML = '';
            author.books.forEach(book => {
                const bookElement = document.createElement('div');
                bookElement.className = 'bg-gray-100 rounded-lg p-4';
                bookElement.innerHTML = `
                    <a href="/book/${book.id}" class="block">
                        <img src="${book.cover_image_url || '/static/images/no-cover.png'}" alt="${book.title} cover" class="w-full h-48 object-cover rounded-lg mb-2">
                        <h3 class="font-semibold text-blue-600 hover:text-blue-800">${book.title}</h3>
                    </a>
                `;
                booksList.appendChild(bookElement);
            });
        })
        .catch(error => console.error('Error fetching author details:', error));
});

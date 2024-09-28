function renderBook(book, container) {
    const bookElement = document.createElement('div');
    bookElement.className = 'bg-white shadow-md rounded-lg p-4 relative';
    bookElement.innerHTML = `
        <img src="${book.cover_image_url || '/static/images/no-cover.png'}" alt="${book.title} cover" class="w-full h-48 object-cover mb-2">
        <h3 class="font-semibold">${book.title}</h3>
        <p class="text-sm text-gray-600">${book.author}</p>
        ${book.is_main_work ? '<span class="absolute top-0 right-0 bg-yellow-400 text-yellow-800 p-1 rounded-bl"><i class="fas fa-bookmark"></i></span>' : ''}
    `;

    const toggleButton = document.createElement('button');
    toggleButton.className = 'mt-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded text-sm';
    toggleButton.textContent = book.is_read ? 'Mark as Unread' : 'Mark as Read';
    toggleButton.onclick = () => toggleReadStatus(book.id, !book.is_read);

    bookElement.appendChild(toggleButton);
    container.appendChild(bookElement);
}

function toggleReadStatus(bookId, newStatus) {
    fetch(`/api/books/${bookId}/toggle_read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: newStatus }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            console.error('Failed to update read status');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function renderBookItem(book) {
    return `
    <div class="bg-white shadow-md rounded-lg p-4 relative ${book.is_read ? 'opacity-50' : ''}">
        <img src="${book.cover_image_url || '/static/images/no-cover.png'}" alt="${book.title} cover" class="w-full h-48 object-cover mb-2">
        <h3 class="font-semibold">${book.title}</h3>
        ${book.is_main_work ? '<span class="absolute top-0 right-0 bg-yellow-400 text-yellow-800 p-1 rounded-bl"><i class="fas fa-bookmark"></i></span>' : ''}
        <button class="toggle-read-status absolute top-2 left-2 w-8 h-8 rounded-full bg-white bg-opacity-75 flex items-center justify-center" data-book-id="${book.id}" data-is-read="${book.is_read}">
            <i class="fas ${book.is_read ? 'fa-eye-slash' : 'fa-eye'}"></i>
        </button>
    </div>
    `;
}

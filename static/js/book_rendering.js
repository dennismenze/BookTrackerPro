function renderBookItem(book) {
    return `
        <div class="book-item bg-gray-100 p-4 rounded-lg shadow ${book.is_read ? 'opacity-50' : ''} relative">
            <img src="${book.cover_image_url || '/static/images/no-cover.png'}" alt="${book.title} cover" class="w-full h-48 object-cover rounded-md mb-2">
            <h3 class="font-semibold text-lg mb-1">${book.title}</h3>
            ${book.author ? `<p class="text-sm text-gray-600 mb-2">by ${book.author}</p>` : ''}
            ${book.is_main_work ? '<span class="inline-block bg-yellow-200 text-yellow-800 text-xs px-2 py-1 rounded-full mb-2">Main Work</span>' : ''}
            <button class="toggle-read-status absolute top-2 right-2 w-8 h-8 rounded-full bg-white bg-opacity-75 flex items-center justify-center"
                    data-book-id="${book.id}" data-is-read="${book.is_read}">
                <i class="fas fa-eye${book.is_read ? '' : '-slash'} text-gray-600"></i>
            </button>
        </div>
    `;
}

function handleUnauthorized(response) {
    if (response.status === 401) {
        // Check if we're already on the login page to prevent infinite loops
        if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        }
        throw new Error('Unauthorized');
    }
    return response;
}

function setupEventListeners() {
    console.log('Setting up event listeners');
    const addBookForm = document.getElementById('add-book-form');
    if (addBookForm) {
        console.log('Attaching event listener to add book form');
        addBookForm.removeEventListener('submit', handleAddBookSubmit);
        addBookForm.addEventListener('submit', handleAddBookSubmit);
    } else {
        console.error('Add book form not found');
    }
}

function handleAddBookSubmit(e) {
    e.preventDefault();
    console.log('Form submitted');
    const title = document.getElementById('book-title').value;
    const author = document.getElementById('book-author').value;
    addBook(title, author);
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded');
    setupEventListeners();
});

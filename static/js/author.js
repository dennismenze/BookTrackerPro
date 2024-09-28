function handleUnauthorized(response) {
    if (response.status === 401) {
        console.log('Unauthorized access, redirecting to login');
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        throw new Error('Unauthorized');
    }
    return response;
}

function loadAuthorList(searchQuery = '') {
    console.log('Loading author list...');
    fetch(`/api/authors?search=${encodeURIComponent(searchQuery)}`, {
        method: 'GET',
        credentials: 'include'
    })
        .then(handleUnauthorized)
        .then(response => response.json())
        .then(data => {
            console.log('Received authors data:', data);
            if (!data || !data.user_authors || !data.all_authors) {
                throw new Error('Invalid data structure received from server');
            }
            const authorList = document.getElementById('author-list');
            if (!authorList) {
                throw new Error('Author list element not found in the DOM');
            }
            authorList.innerHTML = `
                <div class="bg-white shadow-md rounded-lg p-6 mb-8">
                    <h2 class="text-2xl font-semibold mb-4">Your Authors</h2>
                    <ul class="space-y-4">
                        ${data.user_authors.map(author => `
                            <li class="flex items-center justify-between bg-gray-100 p-4 rounded-md">
                                <a href="/author/${author.id}" class="text-blue-600 hover:underline">${author.name}</a>
                                <div class="flex space-x-4">
                                    <span class="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">${author.book_count} books</span>
                                    <span class="bg-green-500 text-white px-3 py-1 rounded-full text-sm">${author.read_percentage.toFixed(1)}% read</span>
                                    <span class="bg-yellow-500 text-white px-3 py-1 rounded-full text-sm">${author.main_works_count} main works</span>
                                    <span class="bg-purple-500 text-white px-3 py-1 rounded-full text-sm">${author.read_main_works_percentage.toFixed(1)}% main works read</span>
                                </div>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div class="bg-white shadow-md rounded-lg p-6">
                    <h2 class="text-2xl font-semibold mb-4">All Authors</h2>
                    <ul class="space-y-4">
                        ${data.all_authors.map(author => `
                            <li class="flex items-center justify-between bg-gray-100 p-4 rounded-md">
                                <a href="/author/${author.id}" class="text-blue-600 hover:underline">${author.name}</a>
                                <div class="flex space-x-4">
                                    <span class="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">${author.book_count} books</span>
                                    <span class="bg-yellow-500 text-white px-3 py-1 rounded-full text-sm">${author.main_works_count} main works</span>
                                </div>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        })
        .catch(error => {
            console.error('Error fetching author list:', error);
            const authorList = document.getElementById('author-list');
            if (authorList) {
                authorList.innerHTML = `<p class="text-red-500 p-4 bg-white shadow-md rounded-lg">Error loading author list: ${error.message}. Please try again.</p>`;
            } else {
                console.error('Author list element not found in the DOM');
            }
        });
}

function setupEventListenersAuthors() {
    const searchButton = document.getElementById('search-authors-btn');
    if (searchButton) {
        searchButton.addEventListener('click', searchAuthors);
    }

    const searchInput = document.getElementById('author-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                searchAuthors();
            }
        });
    }
}

function searchAuthors() {
    const searchQuery = document.getElementById('author-search').value;
    loadAuthorList(searchQuery);
}

document.addEventListener('DOMContentLoaded', function() {
    loadAuthorList();
    setupEventListenersAuthors();
});
function handleUnauthorized(response) {
    if (response.status === 401) {
        console.log('Unauthorized access, redirecting to login');
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        throw new Error('Unauthorized');
    }
    return response;
}

function loadListList(searchQuery = '') {
    console.log('Loading list list...');
    fetch(`/api/lists?search=${encodeURIComponent(searchQuery)}`, {
        method: 'GET',
        credentials: 'include'
    })
        .then(handleUnauthorized)
        .then(response => response.json())
        .then(lists => {
            console.log('Received lists:', lists);
            const listList = document.getElementById('list-list');
            const isAdminUser = isAdmin();
            const currentUserId = getUserId();
            console.log('Is Admin:', isAdminUser);
            console.log('Current User ID:', currentUserId);
            listList.innerHTML = `
                <div class="bg-white shadow-md rounded-lg p-6 mb-8">
                    <h2 class="text-2xl font-semibold mb-4">Your Reading Lists</h2>
                    <div id="private-lists">
                        <h3 class="text-xl font-semibold mb-2">Private Lists</h3>
                        <ul class="space-y-4">
                            ${lists.filter(list => !list.is_public).map(list => `
                                <li class="flex items-center justify-between bg-gray-100 p-4 rounded-md">
                                    <a href="/list/${list.id}" class="text-blue-600 hover:underline">${list.name}</a>
                                    <div class="flex space-x-2 items-center">
                                        <span class="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">${list.book_count} books</span>
                                        <span class="bg-green-500 text-white px-3 py-1 rounded-full text-sm">${list.read_percentage.toFixed(1)}% read</span>
                                        <button class="bg-yellow-500 text-white px-3 py-1 rounded-md hover:bg-yellow-600 transition duration-300 toggle-visibility" data-list-id="${list.id}" data-is-public="true">Make Public</button>
                                        ${(isAdminUser || list.user_id === currentUserId) ? `<button class="bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 transition duration-300 delete-list" data-list-id="${list.id}">Delete</button>` : ''}
                                    </div>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
                <div class="bg-white shadow-md rounded-lg p-6">
                    <h2 class="text-2xl font-semibold mb-4">Public Lists</h2>
                    <ul class="space-y-4">
                        ${lists.filter(list => list.is_public).map(list => `
                            <li class="flex items-center justify-between bg-gray-100 p-4 rounded-md">
                                <a href="/list/${list.id}" class="text-blue-600 hover:underline">${list.name}</a>
                                <div class="flex space-x-2 items-center">
                                    <span class="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">${list.book_count} books</span>
                                    <span class="bg-green-500 text-white px-3 py-1 rounded-full text-sm">${list.read_percentage.toFixed(1)}% read</span>
                                    ${list.user_id === null ? `
                                        <button class="bg-yellow-500 text-white px-3 py-1 rounded-md hover:bg-yellow-600 transition duration-300 toggle-visibility" data-list-id="${list.id}" data-is-public="false">Make Private</button>
                                    ` : ''}
                                    ${isAdminUser ? `<button class="bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 transition duration-300 delete-list" data-list-id="${list.id}">Delete</button>` : ''}
                                </div>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <button id="create-list-btn" class="mt-8 bg-green-500 text-white px-6 py-2 rounded-md hover:bg-green-600 transition duration-300">Create New List</button>
            `;
            setupEventListeners();
        })
        .catch(error => {
            console.error('Error fetching list list:', error);
            const listList = document.getElementById('list-list');
            listList.innerHTML = '<p class="text-red-500 p-4 bg-white shadow-md rounded-lg">Error loading list list. Please try again.</p>';
        });
}

function setupEventListeners() {
    const createListBtn = document.getElementById('create-list-btn');
    if (createListBtn) {
        createListBtn.addEventListener('click', showCreateListForm);
    }

    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('toggle-visibility')) {
            const listId = event.target.dataset.listId;
            const isPublic = event.target.dataset.isPublic === 'true';
            toggleListVisibility(listId, isPublic);
        } else if (event.target.classList.contains('delete-list')) {
            const listId = event.target.dataset.listId;
            deleteList(listId);
        }
    });

    const searchInput = document.getElementById('list-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                searchLists();
            }
        });
    }
}

function showCreateListForm() {
    const listList = document.getElementById('list-list');
    listList.innerHTML += `
        <div id="create-list-form" class="mt-8 bg-white shadow-md rounded-lg p-6">
            <h3 class="text-xl font-semibold mb-4">Create New List</h3>
            <input type="text" id="new-list-name" class="w-full px-4 py-2 mb-4 border rounded-md" placeholder="Enter list name">
            <div class="flex items-center mb-4">
                <input type="checkbox" id="new-list-public" class="mr-2">
                <label for="new-list-public">Make list public</label>
            </div>
            <button id="create-list-submit" class="bg-green-500 text-white px-6 py-2 rounded-md hover:bg-green-600 transition duration-300">Create List</button>
        </div>
    `;
    document.getElementById('create-list-submit').addEventListener('click', createList);
}

function createList() {
    const listName = document.getElementById('new-list-name').value;
    const isPublic = document.getElementById('new-list-public').checked;
    if (!listName) {
        alert('Please enter a list name');
        return;
    }

    console.log('Creating new list:', listName, 'Public:', isPublic);
    fetch('/api/lists', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: listName, is_public: isPublic }),
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => {
        console.log('Create list response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Create list response:', data);
        alert(data.message);
        loadListList();
    })
    .catch(error => {
        console.error('Error creating list:', error);
        alert('Failed to create list. Please try again.');
    });
}

function toggleListVisibility(listId, isPublic) {
    fetch(`/api/lists/${listId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_public: isPublic }),
        credentials: 'include'
    })
    .then(handleUnauthorized)
    .then(response => response.json())
    .then(() => {
        loadListList();
    })
    .catch(error => {
        console.error('Error updating list visibility:', error);
        alert('Failed to update list visibility. Please try again.');
    });
}

function deleteList(listId) {
    console.log(`Attempting to delete list with ID: ${listId}`);
    if (confirm('Are you sure you want to delete this list? This action cannot be undone.')) {
        fetch(`/api/lists/${listId}`, {
            method: 'DELETE',
            credentials: 'include'
        })
        .then(handleUnauthorized)
        .then(response => {
            console.log(`Delete response status: ${response.status}`);
            if (!response.ok) {
                throw new Error(`Failed to delete list: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Delete response:', data);
            alert(data.message);
            loadListList();
        })
        .catch(error => {
            console.error('Error deleting list:', error);
            alert(`Failed to delete list: ${error.message}. Please try again.`);
        });
    }
}

function searchLists() {
    const searchQuery = document.getElementById('list-search').value;
    loadListList(searchQuery);
}

function isAdmin() {
    return document.body.dataset.isAdmin === 'true';
}

function getUserId() {
    return parseInt(document.body.dataset.userId, 10);
}

function debounce(func, delay) {
    let debounceTimer;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(context, args), delay);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const listSearchInput = document.getElementById('list-search');
    if (listSearchInput) {
        listSearchInput.addEventListener('input', debounce(searchLists, 300));
    }

    loadListList();
});
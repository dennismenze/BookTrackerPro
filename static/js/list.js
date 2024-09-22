function loadListList() {
    fetch('/api/lists')
        .then(response => response.json())
        .then(lists => {
            const listList = document.getElementById('list-list');
            listList.innerHTML = `
                <ul class="list-group">
                    ${lists.map(list => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="/list/${list.id}">${list.name}</a>
                            <span class="badge bg-primary rounded-pill">${list.book_count} books</span>
                            <span class="badge bg-success rounded-pill">${list.read_percentage.toFixed(1)}% read</span>
                        </li>
                    `).join('')}
                </ul>
            `;
        });
}

let currentListId;

function loadListDetails(listId) {
    currentListId = listId;
    console.log('Loading list details for id:', listId);
    fetch(`/api/lists/${listId}`)
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(list => {
            console.log('Received list details:', list);
            const listDetails = document.getElementById('list-details');
            listDetails.innerHTML = `
                <h2>${list.name}</h2>
                <p>Books: ${list.books.length}</p>
                <p>Read Percentage: ${list.read_percentage.toFixed(1)}%</p>
                <h3>Books:</h3>
                <ul class="list-group">
                    ${list.books.map(book => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="/book/${book.id}?id=${book.id}">${book.title}</a> by <a href="/author/${book.author_id}">${book.author}</a>
                            <button onclick="toggleReadStatus(${book.id}, ${!book.is_read})" class="btn btn-sm ${book.is_read ? 'btn-secondary' : 'btn-success'}">
                                Mark as ${book.is_read ? 'Unread' : 'Read'}
                            </button>
                        </li>
                    `).join('')}
                </ul>
            `;
        })
        .catch(error => {
            console.error('Error fetching list details:', error);
            const listDetails = document.getElementById('list-details');
            listDetails.innerHTML = `<p>Error loading list details: ${error.message}. Please try again.</p>`;
        });
}

function toggleReadStatus(bookId, isRead) {
    fetch(`/api/books/${bookId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_read: isRead }),
    })
    .then(response => response.json())
    .then(() => loadListDetails(currentListId))
    .catch(error => {
        console.error('Error updating book read status:', error);
        alert('Failed to update book status. Please try again.');
    });
}

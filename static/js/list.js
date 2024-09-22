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

function loadListDetails(listId) {
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
                            <a href="/book/${book.id}?id=${book.id}">${book.title}</a> by ${book.author}
                            <span class="badge ${book.is_read ? 'bg-success' : 'bg-secondary'} rounded-pill">
                                ${book.is_read ? 'Read' : 'Unread'}
                            </span>
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

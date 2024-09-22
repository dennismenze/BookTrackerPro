function loadAuthorList() {
    fetch('https://c3e4260a-6536-436d-a00a-a2ad1e9344db-00-1gx8hgbvt0nyh.picard.replit.dev/api/authors')
        .then(response => response.json())
        .then(authors => {
            const authorList = document.getElementById('author-list');
            authorList.innerHTML = `
                <ul class="list-group">
                    ${authors.map(author => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="/author/${author.id}">${author.name}</a>
                            <span class="badge bg-primary rounded-pill">${author.book_count} books</span>
                            <span class="badge bg-success rounded-pill">${author.read_percentage.toFixed(1)}% read</span>
                        </li>
                    `).join('')}
                </ul>
            `;
        })
        .catch(error => {
            console.error('Error fetching author list:', error);
            const authorList = document.getElementById('author-list');
            authorList.innerHTML = '<p>Error loading author list. Please try again.</p>';
        });
}

function loadAuthorDetails(authorId) {
    console.log('Loading author details for id:', authorId);
    fetch(`https://c3e4260a-6536-436d-a00a-a2ad1e9344db-00-1gx8hgbvt0nyh.picard.replit.dev/api/authors/${authorId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(author => {
            console.log('Received author details:', author);
            const authorDetails = document.getElementById('author-details');
            authorDetails.innerHTML = `
                <h2>${author.name}</h2>
                <p>Books: ${author.books.length}</p>
                <p>Read Percentage: ${author.read_percentage.toFixed(1)}%</p>
                <h3>Books:</h3>
                <ul class="list-group">
                    ${author.books.map(book => `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="/book/${book.id}">${book.title}</a>
                            <span class="badge ${book.is_read ? 'bg-success' : 'bg-secondary'} rounded-pill">
                                ${book.is_read ? 'Read' : 'Unread'}
                            </span>
                        </li>
                    `).join('')}
                </ul>
            `;
        })
        .catch(error => {
            console.error('Error fetching author details:', error);
            const authorDetails = document.getElementById('author-details');
            authorDetails.innerHTML = `<p>Error loading author details: ${error.message}. Please try again.</p>`;
        });
}

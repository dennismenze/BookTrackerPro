document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const authorId = urlParams.get('id') || document.getElementById('author-details').dataset.authorId;
    if (authorId) {
        loadAuthorDetails(authorId);
    } else {
        console.error('Author ID not found');
        document.getElementById('author-details').innerHTML = '<p class="text-red-500">Error: Author ID not provided. Please go back and try again.</p>';
    }
});

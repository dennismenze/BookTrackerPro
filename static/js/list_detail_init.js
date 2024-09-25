document.addEventListener('DOMContentLoaded', () => {
    const listId = document.getElementById('list-details').dataset.listId;
    if (listId) {
        loadListDetails(listId);
    } else {
        console.error('List ID not found');
        document.getElementById('list-details').innerHTML = '<p>Error: List ID not provided. Please go back and try again.</p>';
    }
});

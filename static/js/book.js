document.addEventListener('DOMContentLoaded', function() {
    const toggleReadStatusButton = document.getElementById('toggle-read-status');
    
    if (toggleReadStatusButton) {
        toggleReadStatusButton.addEventListener('click', function() {
            const bookId = this.dataset.bookId;
            const isRead = this.dataset.isRead === 'true';
            
            fetch('/book/toggle_read_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId, is_read: !isRead }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.dataset.isRead = (!isRead).toString();
                    this.textContent = isRead ? 'Mark as Read' : 'Mark as Unread';
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }
});

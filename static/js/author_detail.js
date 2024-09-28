function toggleReadStatus(bookId) {
    fetch(`/toggle_read_status/${bookId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            const icon = document.getElementById(`read-icon-${bookId}`);
            if (data.is_read) {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            } else {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            }
            // Update debug information
            const debugInfo = icon.closest('.relative').querySelector('.text-xs');
            debugInfo.textContent = `Read status: ${data.is_read}`;
        })
        .catch(error => console.error('Error:', error));
}

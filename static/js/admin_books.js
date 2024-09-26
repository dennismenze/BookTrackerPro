document.addEventListener('DOMContentLoaded', function() {
    const toggleButtons = document.querySelectorAll('.toggle-main-work');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.dataset.bookId;
            const isMainWork = this.dataset.isMainWork === 'true';
            fetch(`/api/books/${bookId}/toggle_main_work`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ is_main_work: !isMainWork }),
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_main_work) {
                    this.textContent = 'Main Work';
                    this.classList.remove('bg-gray-300');
                    this.classList.add('bg-green-500');
                } else {
                    this.textContent = 'Not Main Work';
                    this.classList.remove('bg-green-500');
                    this.classList.add('bg-gray-300');
                }
                this.dataset.isMainWork = data.is_main_work;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating the main work status.');
            });
        });
    });
});

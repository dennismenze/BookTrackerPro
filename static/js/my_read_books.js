document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('filter-form');
    const filterTitle = document.getElementById('filter_title');
    const filterAuthor = document.getElementById('filter_author');
    const sortBy = document.getElementById('sort_by');
    const sortOrder = document.getElementById('sort_order');

    filterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        applyFilters();
    });

    [filterTitle, filterAuthor, sortBy, sortOrder].forEach(element => {
        element.addEventListener('change', function() {
            applyFilters();
        });
    });

    function applyFilters() {
        const url = new URL(window.location);
        url.searchParams.set('title', filterTitle.value);
        url.searchParams.set('author', filterAuthor.value);
        url.searchParams.set('sort', sortBy.value);
        url.searchParams.set('order', sortOrder.value);
        url.searchParams.set('page', '1');  // Reset to first page when applying new filters
        window.location.href = url.toString();
    }
});

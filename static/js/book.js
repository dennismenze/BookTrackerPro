document.addEventListener("DOMContentLoaded", function () {
    const toggleReadStatusButton = document.getElementById("toggle-read-status");
    const userRatingButtons = document.querySelectorAll("#user-rating button");
    const userReviewTextarea = document.getElementById("user-review");
    const submitReviewButton = document.getElementById("submit-review");
    const listsTable = document.getElementById("lists-table").getElementsByTagName('tbody')[0];
    const prevPageButton = document.getElementById("prev-page");
    const nextPageButton = document.getElementById("next-page");
    const pageInfo = document.getElementById("page-info");
    const sortSelect = document.getElementById("sort-select");

    let currentPage = 1;
    let totalPages = 1;
    let currentSort = 'name';
    let currentOrder = 'asc';

    if (toggleReadStatusButton) {
        toggleReadStatusButton.addEventListener("click", function () {
            const bookId = this.dataset.bookId;
            const isRead = this.dataset.isRead === "true";

            fetch("/book/toggle_read_status", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ book_id: bookId, is_read: !isRead }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        this.dataset.isRead = (!isRead).toString();
                        this.textContent = isRead ? "Mark as Read" : "Mark as Unread";
                        
                        const readDateElement = document.getElementById("read-date");
                        if (data.read_date) {
                            if (readDateElement) {
                                readDateElement.textContent = new Date(data.read_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
                            } else {
                                const newReadDateElement = document.createElement("p");
                                newReadDateElement.id = "read-date";
                                newReadDateElement.className = "mt-2 text-sm text-gray-600";
                                newReadDateElement.textContent = `Read on: ${new Date(data.read_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}`;
                                this.insertAdjacentElement('afterend', newReadDateElement);
                            }
                        } else if (readDateElement) {
                            readDateElement.remove();
                        }
                    }
                })
                .catch((error) => console.error("Error:", error));
        });
    }

    userRatingButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const rating = this.dataset.rating;
            const bookId = toggleReadStatusButton.dataset.bookId;

            fetch("/book/rate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ book_id: bookId, rating: rating }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        userRatingButtons.forEach((btn) => {
                            btn.classList.remove("text-yellow-500");
                            btn.classList.add("text-gray-300");
                            if (btn.dataset.rating <= rating) {
                                btn.classList.remove("text-gray-300");
                                btn.classList.add("text-yellow-500");
                            }
                        });
                        document.getElementById("average-rating").textContent = data.average_rating.toFixed(1) + " / 5";
                        document.querySelector("#user-rating + p").textContent = `Your rating: ${rating} / 5`;
                    }
                })
                .catch((error) => console.error("Error:", error));
        });
    });

    submitReviewButton.addEventListener("click", function () {
        const bookId = toggleReadStatusButton.dataset.bookId;
        const review = userReviewTextarea.value;

        fetch("/book/review", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ book_id: bookId, review: review }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("Review submitted successfully!");
                    location.reload();
                }
            })
            .catch((error) => console.error("Error:", error));
    });

    function fetchLists(page = 1, sort = currentSort, order = currentOrder) {
        const bookId = toggleReadStatusButton.dataset.bookId;
        fetch(`/book/${bookId}/lists?page=${page}&sort=${sort}&order=${order}`)
            .then(response => response.json())
            .then(data => {
                listsTable.innerHTML = '';
                data.lists.forEach(list => {
                    const row = listsTable.insertRow();
                    row.innerHTML = `
                        <td class="py-2 px-4">
                            <a href="/list/${list.id}" class="text-blue-500 hover:underline">${list.name}</a>
                        </td>
                        <td class="py-2 px-4">${list.is_public ? 'Public' : 'Private'}</td>
                    `;
                });
                currentPage = data.current_page;
                totalPages = data.pages;
                updatePagination();
            })
            .catch(error => console.error('Error fetching lists:', error));
    }

    function updatePagination() {
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        prevPageButton.disabled = currentPage === 1;
        nextPageButton.disabled = currentPage === totalPages;
    }

    prevPageButton.addEventListener('click', () => {
        if (currentPage > 1) {
            fetchLists(currentPage - 1);
        }
    });

    nextPageButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            fetchLists(currentPage + 1);
        }
    });

    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const [newSort, newOrder] = this.value.split('-');
            currentSort = newSort;
            currentOrder = newOrder;
            fetchLists(1, currentSort, currentOrder);
        });
    }

    fetchLists();
});
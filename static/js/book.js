document.addEventListener("DOMContentLoaded", function () {
    const toggleReadStatusButton = document.getElementById("toggle-read-status");
    const userRatingContainer = document.getElementById("user-rating");
    const userReviewTextarea = document.getElementById("user-review");
    const submitReviewButton = document.getElementById("submit-review");
    const listsTable = document.getElementById("lists-table").getElementsByTagName('tbody')[0];
    const prevPageButton = document.getElementById("prev-page");
    const nextPageButton = document.getElementById("next-page");
    const pageInfo = document.getElementById("page-info");
    const sortSelect = document.getElementById("sort-select");
    const deleteRatingButton = document.getElementById("delete-rating");

    let currentPage = 1;
    let totalPages = 1;
    let currentSort = 'name';
    let currentOrder = 'asc';
    let currentUserRating = 0;

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
                        this.textContent = isRead ? window.translations["Mark as Read"] : window.translations["Mark as Unread"];
                        
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

    function createStarRating() {
        userRatingContainer.innerHTML = '';
        for (let i = 0; i < 5; i++) {
            const starContainer = document.createElement('div');
            starContainer.className = 'inline-block relative w-6 h-12 cursor-pointer';
            
            const fullStar = document.createElement('span');
            fullStar.className = 'absolute top-0 left-0 text-3xl text-gray-300 hover:text-yellow-500';
            fullStar.innerHTML = '★';
            fullStar.dataset.rating = (i + 1).toString();
            
            const halfStar = document.createElement('span');
            halfStar.className = 'absolute top-0 left-0 text-3xl text-gray-300 hover:text-yellow-500';
            halfStar.innerHTML = '★';
            halfStar.style.width = '50%';
            halfStar.style.overflow = 'hidden';
            halfStar.dataset.rating = (i + 0.5).toString();
            
            starContainer.appendChild(fullStar);
            starContainer.appendChild(halfStar);
            userRatingContainer.appendChild(starContainer);
            
            [halfStar, fullStar].forEach(star => {
                star.addEventListener('click', function() {
                    const rating = parseFloat(this.dataset.rating);
                    submitRating(rating);
                });
                
                star.addEventListener('mouseover', function() {
                    const rating = parseFloat(this.dataset.rating);
                    updateStarDisplay(rating);
                });
                
                star.addEventListener('mouseout', function() {
                    updateStarDisplay(currentUserRating);
                });
            });
        }
    }

    function submitRating(rating) {
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
                    currentUserRating = rating;
                    updateRatingDisplay(data.rating, data.average_rating);
                    if (toggleReadStatusButton.dataset.isRead.toLowerCase() === "false") {
                        toggleReadStatusButton.click();
                    }
                }
            })
            .catch((error) => console.error("Error:", error));
    }

    if (deleteRatingButton) {
        deleteRatingButton.addEventListener("click", function () {
            const bookId = toggleReadStatusButton.dataset.bookId;

            fetch("/book/delete_rating", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ book_id: bookId }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        currentUserRating = 0;
                        updateRatingDisplay(0, data.average_rating);
                        alert(data.message);
                    } else {
                        alert(data.error || "Failed to delete rating");
                    }
                })
                .catch((error) => console.error("Error:", error));
        });
    }

    function updateRatingDisplay(userRating, averageRating) {
        currentUserRating = userRating;
        updateStarDisplay(userRating);
        document.getElementById("average-rating").textContent = averageRating ? averageRating.toFixed(1) + " / 5" : "No ratings yet";
        const userRatingText = document.querySelector("#user-rating + p");
        userRatingText.textContent = userRating > 0 ? `Your rating: ${userRating.toFixed(1)} / 5` : "Your rating: Not rated";
        deleteRatingButton.style.display = userRating > 0 ? "inline-block" : "none";
    }

    function updateStarDisplay(rating) {
        const stars = userRatingContainer.querySelectorAll('span');
        stars.forEach((star, index) => {
            const starValue = parseFloat(star.dataset.rating);
            if (starValue <= rating) {
                star.classList.remove("text-gray-300");
                star.classList.add("text-yellow-500");
            } else {
                star.classList.remove("text-yellow-500");
                star.classList.add("text-gray-300");
            }
        });
    }

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
                    alert(window.translations["Review submitted successfully!"]);
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
                        <td class="py-2 px-4">${list.is_public ? window.translations["Public"] : window.translations["Private"]}</td>
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

    // Initialize the star rating system
    createStarRating();

    // Initialize the star display
    const initialRatingText = document.querySelector("#user-rating + p").textContent;
    const initialRating = initialRatingText.includes("Not rated") ? 0 : parseFloat(initialRatingText.split(':')[1]);
    const averageRating = document.getElementById("average-rating").textContent;
    updateRatingDisplay(initialRating, parseFloat(averageRating));

    fetchLists();
});

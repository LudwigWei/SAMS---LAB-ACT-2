document.addEventListener("DOMContentLoaded", function () {
    // Get elements
    const generateBtn = document.querySelector(".generate-btn");
    const qrPlaceholder = document.querySelector(".qr-placeholder");
    const classCodeInput = document.querySelector("#class-code"); // Class code input field

    const modal = document.querySelector(".modal");
    const modalOverlay = document.querySelector(".modal-overlay");
    const courseCard = document.querySelector(".course-card");
    const courseMenu = document.querySelector(".course-menu");
    const profileWrapper = document.querySelector(".profile-wrapper");
    const confirmationModal = document.querySelector(".confirmation-modal");
    const cancelButton = document.querySelector(".btn-cancel");
    const logoutButton = document.querySelector(".btn-logout");
    const addButton = document.querySelector(".add-button");
    const addClassModal = document.querySelector(".add-class-modal");
    const attendanceTableBody = document.getElementById("attendanceTableBody");

    // Generate QR Code Click Handler
    generateBtn.addEventListener("click", function () {
        const classCode = classCodeInput.value.trim();

        if (!classCode) {
            alert("Please enter a class code before generating a QR code.");
            return;
        }

        fetch(`/professor/generate-qr/${classCode}`)
            .then(response => response.json())
            .then(data => {
                if (data.qr_code) {
                    qrPlaceholder.innerHTML = `<img src="${data.qr_code}" alt="QR Code" width="200" height="200">`;
                } else {
                    alert("Error generating QR code.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Failed to generate QR code.");
            });
    });

    // Fetch and display attendance
    function fetchAttendance() {
        const classCode = "CS 3201"; // Modify dynamically if needed

        fetch(`/professor/attendance/${classCode}`)
            .then(response => response.json())
            .then(data => {
                attendanceTableBody.innerHTML = ""; // Clear previous data

                if (data.error) {
                    attendanceTableBody.innerHTML = `<tr><td colspan="2">${data.error}</td></tr>`;
                    return;
                }

                data.forEach(student => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${student.name}</td>
                        <td>
                            <input type="checkbox" class="attendance-checkbox" ${
                                student.checked ? "checked" : ""
                            } disabled>
                        </td>
                    `;
                    attendanceTableBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error("Error fetching attendance:", error);
            });
    }

    // Show modal and fetch attendance when course is clicked
    courseCard.addEventListener("click", function (e) {
        if (!e.target.classList.contains("course-menu")) {
            modal.style.display = "block";
            modalOverlay.style.display = "block";
            fetchAttendance();
        }
    });

    // Profile (logout) click handler
    profileWrapper.addEventListener("click", function (e) {
        e.stopPropagation();
        confirmationModal.style.display = "block";
        modalOverlay.style.display = "block";
    });

    // Cancel button click handler
    cancelButton.addEventListener("click", function () {
        confirmationModal.style.display = "none";
        modalOverlay.style.display = "none";
        addClassModal.style.display = "none";
    });

    // Logout button click handler
    logoutButton.addEventListener("click", function () {
        fetch("/logout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                window.location.href = "/";
            })
            .catch(error => {
                console.error("Logout error:", error);
            });

        confirmationModal.style.display = "none";
        modalOverlay.style.display = "none";
    });

    // Close modals when clicking overlay
    modalOverlay.addEventListener("click", function () {
        modal.style.display = "none";
        confirmationModal.style.display = "none";
        modalOverlay.style.display = "none";
        addClassModal.style.display = "none";
    });

    // Course menu click handler
    courseMenu.addEventListener("click", function (e) {
        e.stopPropagation();
        alert("Course menu clicked");
    });

    // Add button click handler with feedback
    addButton.addEventListener("click", function () {
        this.style.transform = "scale(0.9)";
        setTimeout(() => {
            this.style.transform = "scale(1)";
        }, 100);
        addClassModal.style.display = "block";
        modalOverlay.style.display = "block";
    });
});

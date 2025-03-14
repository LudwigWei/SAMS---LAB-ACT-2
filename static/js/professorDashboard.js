document.addEventListener("DOMContentLoaded", function () {
    // Get elements
    const classNameInput = document.querySelector("#class-name");
    const sectionInput = document.querySelector("#section");
    const classCodeInput = document.querySelector("#class-code"); // Class code input field
    const qrPlaceholder = document.querySelector(".qr-placeholder");
    const generateBtn = document.querySelector(".generate-btn");

    const modal = document.querySelector(".modal");
    const modalOverlay = document.querySelector(".modal-overlay");
    const courseCard = document.querySelector(".course-card");
    const courseMenu = document.querySelector(".course-menu");
    const profileWrapper = document.querySelector(".profile-wrapper");
    const confirmationModal = document.querySelector(".confirmation-modal");
    const cancelButton = document.querySelector(".cancel-btn");
    const logoutButton = document.querySelector(".btn-logout");
    const addButton = document.querySelector(".add-button");
    const createClassButton = document.querySelector(".create-btn");
    const addClassModal = document.querySelector(".add-class-modal");

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

    // Course card click handler
    courseCard.addEventListener("click", function (e) {
        if (!e.target.classList.contains("course-menu")) {
            modal.style.display = "block";
            modalOverlay.style.display = "block";
        }
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

    createClassButton.addEventListener("click", function () {
        const className = classNameInput.value.trim();
        const section = sectionInput.value.trim();
        const classCode = classCodeInput.value.trim();
    
        if (!className || !section || !classCode) {
            alert("Please fill in all fields before creating the class.");
            return;
        }
    
        fetch("/professor/create-class", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ class_name: className, section: section, class_code: classCode }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Class created successfully!");
    
                // create new course card dynamically
                const newCourseCard = document.createElement("div");
                newCourseCard.classList.add("course-card");
                newCourseCard.innerHTML = `
                    <div class="course-title">${className}</div>
                    <div class="course-code">${classCode}</div>
                    <div class="course-menu">...</div>
                `;
    
                // append new card to the container
                document.querySelector(".dashboard-card").appendChild(newCourseCard);
    
                
                classNameInput.value = "";
                sectionInput.value = "";
                classCodeInput.value = "";
    
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Failed to create class.");
        });
    });
    

});

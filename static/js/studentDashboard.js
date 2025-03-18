document.addEventListener("DOMContentLoaded", function () {
    const addButton = document.querySelector(".add-button");
    const modalOverlay = document.querySelector(".modal-overlay");
    const joinClassModal = document.querySelector(".join-class-modal");
    const btnCancel = document.querySelector(".btn-cancel");
    const btnJoin = document.querySelector(".btn-join");
    const classCodeInput = document.querySelector(".class-code-input");
    const courseCards = document.querySelectorAll(".course-card");
    const qrImage = document.getElementById("qr-image");
    const profileIcon = document.querySelector(".profile-icon");
    const qrModal = document.querySelector(".modal");
    const uploadBtn = document.querySelector(".upload-btn");
   
    courseCards.forEach(card => {
        card.addEventListener("click", function () {
            const classCode = card.querySelector(".course-code").textContent.trim();
            currentClassCode = classCode
            fetch(`/student/get-qr/${classCode}`)
                .then(response => response.json())
                .then(data => {
                    console.log(data.qr_code);
                    if (data.qr_code) {
                        qrImage.src = data.qr_code;
                        modalOverlay.style.display = "block";
                        qrModal.style.display = "block";
                    } else {
                        alert("Failed to load QR code.");
                    }
                })
                .catch(error => console.error("Error loading QR code:", error));
        });
    });
    
    // Open Join Class Modal
    addButton.addEventListener("click", function () {
        modalOverlay.style.display = "block";
        joinClassModal.style.display = "block";
    });

    // Close modal when cancel is clicked
    btnCancel.addEventListener("click", function () {
        modalOverlay.style.display = "none";
        joinClassModal.style.display = "none";
    });

    // Join class action
    btnJoin.addEventListener("click", function () {
        const classCode = classCodeInput.value.trim();
        if (!classCode) {
            alert("Please enter a class code.");
            return;
        }

        fetch("/student/join-class", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ class_code: classCode }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Successfully joined the class!");
                location.reload();
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    });
    
    profileIcon.addEventListener("click", function () {
        modalOverlay.style.display = "block";
        qrModal.style.display = "block";
    });

    modalOverlay.addEventListener("click", function () {
        modalOverlay.style.display = "none";
        qrModal.style.display = "none";
        joinClassModal.style.display = "none";
    });


    uploadBtn.addEventListener("click", function () {
        if (!currentClassCode) {
            alert("No class selected.");
            return;
        }

        fetch("/student/mark-attendance", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ class_code: currentClassCode }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Attendance marked successfully!");
                location.reload();
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    modalOverlay.addEventListener("click", function () {
        modalOverlay.style.display = "none";
        qrModal.style.display = "none";
    });

    // Logout Confirmation Modal
    const logoutButton = document.querySelector(".btn-logout");
    const confirmationModal = document.querySelector(".confirmation-modal");
    const confirmCancel = document.querySelector(".confirmation-buttons .btn-cancel");
    
    logoutButton.addEventListener("click", function () {
        modalOverlay.style.display = "block";
        confirmationModal.style.display = "block";
    });

    confirmCancel.addEventListener("click", function () {
        modalOverlay.style.display = "none";
        confirmationModal.style.display = "none";
    });
});

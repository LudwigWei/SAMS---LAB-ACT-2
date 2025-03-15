document.addEventListener("DOMContentLoaded", function () {
    // Get elements
    const classNameInput = document.querySelector("#class-name");
    const sectionInput = document.querySelector("#section");
    const classCodeInput = document.querySelector("#class-code");
    const qrPlaceholder = document.querySelector(".qr-placeholder");
    const generateBtn = document.querySelector(".generate-btn");
    const createClassButton = document.querySelector(".create-btn");
    const addButton = document.querySelector(".add-button");
    const addClassModal = document.querySelector(".add-class-modal");
    const modalOverlay = document.querySelector(".modal-overlay");
    const cancelButton = document.querySelector(".cancel-btn");
    const courseContainer = document.querySelector(".course-container");
    const attendanceModal = document.querySelector(".attendance-modal");
    const attendanceModalOverlay = document.querySelector(".attendance-modal-overlay");
    const closeAttendanceModal = document.querySelector(".close-attendance-modal");
    const attendanceTableBody = document.getElementById("attendanceTableBody");
    const modalTitle = document.getElementById("modal-course-title");
    const modalCourseCode = document.getElementById("modal-course-code");

    let qrGenerated = false;
    createClassButton.disabled = true;

    // Load classes when the dashboard is opened
    function loadClasses() {
        fetch("/professor/classes")
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Error fetching classes:", data.error);
                    return;
                }

                courseContainer.innerHTML = ""; // Clear previous content

                data.classes.forEach(course => {
                    const courseButton = document.createElement("button");
                    courseButton.classList.add("course-button");
                    courseButton.setAttribute("data-class-code", course.class_code);
                    courseButton.innerHTML = `<b>${course.class_name}</b> (${course.class_code})`;

                    // Clicking the class opens the attendance modal
                    courseButton.addEventListener("click", () => {
                        openAttendanceModal(course.class_code, course.class_name);
                    });

                    courseContainer.appendChild(courseButton);
                });
            })
            .catch(error => console.error("Error loading classes:", error));
    }

    // Open "Add Class" Modal
    addButton.addEventListener("click", function () {
        addClassModal.style.display = "block";
        modalOverlay.style.display = "block";
        qrGenerated = false;
        createClassButton.disabled = true;
        qrPlaceholder.innerHTML = "";
    });

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
                qrPlaceholder.innerHTML = `<img src="${data.qr_code}" alt="QR Code" width="200" height="200">`;
                qrGenerated = true;
                createClassButton.disabled = false;
            })
            .catch(error => {
                console.error("QR Error:", error);
                alert("Failed to generate QR code.");
            });
    });

    // Create Class Button Click Handler
    createClassButton.addEventListener("click", function () {
        if (!qrGenerated) {
            alert("You must generate the QR code before creating the class.");
            return;
        }

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

                // Refresh the list of classes dynamically
                loadClasses();

                // Close the modal
                addClassModal.style.display = "none";
                modalOverlay.style.display = "none";
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Failed to create class.");
        });
    });

    // Function to load attendance data when a course is clicked
    function openAttendanceModal(classCode, className) {
        modalTitle.textContent = className; // Update modal title dynamically
        modalCourseCode.textContent = classCode; // Update course code

        fetch(`/professor/attendance-data/${classCode}`)
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
                        <td><input type="checkbox" ${student.checked ? "checked" : ""} disabled></td>
                    `;
                    attendanceTableBody.appendChild(row);
                });

                // Show attendance modal
                attendanceModal.style.display = "block";
                attendanceModalOverlay.style.display = "block";
            })
            .catch(error => console.error("Error fetching attendance:", error));
    }

    // Close attendance modal
    closeAttendanceModal.addEventListener("click", function () {
        attendanceModal.style.display = "none";
        attendanceModalOverlay.style.display = "none";
    });

    attendanceModalOverlay.addEventListener("click", function () {
        attendanceModal.style.display = "none";
        attendanceModalOverlay.style.display = "none";
    });

    // Load existing classes when page loads
    loadClasses();
});

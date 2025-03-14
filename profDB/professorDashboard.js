document.addEventListener("DOMContentLoaded", function () {
    const modal = document.querySelector(".modal");
    const modalOverlay = document.querySelector(".modal-overlay");
    const attendanceTableBody = document.getElementById("attendanceTableBody");
    const courseCard = document.querySelector(".course-card");

    function fetchAttendance() {
        const classCode = "CS 3201";  // Modify dynamically if needed

        fetch(`/professor/attendance/${classCode}`)
            .then(response => response.json())
            .then(data => {
                attendanceTableBody.innerHTML = "";

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

    courseCard.addEventListener("click", function () {
        modal.style.display = "block";
        modalOverlay.style.display = "block";
        fetchAttendance();
    });
});

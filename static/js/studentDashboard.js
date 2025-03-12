document.addEventListener('DOMContentLoaded', function () {
    const qrScannerPlaceholder = document.querySelector('.qr-placeholder');
    const scanQRButton = document.querySelector('.scan-qr-btn');
    
    scanQRButton.addEventListener('click', function () {
        alert("Scanning QR Code... (Feature to be implemented)");
        // Future implementation: Use a QR scanner library to scan codes
    });
    
    async function fetchCourseQR(courseCode) {
        try {
            const response = await fetch(`/course/qr/${courseCode}`);  // Added backticks for string interpolation
            if (response.ok) {
                qrScannerPlaceholder.innerHTML = `<img src="/course/qr/${courseCode}" alt="QR Code" width="200" height="200">`;  // Corrected HTML string with backticks
            } else {
                alert("Failed to fetch QR code.");
            }
        } catch (error) {
            console.error("Error fetching QR code:", error);
        }
    }
    
    // Automatically fetch QR code for courses assigned to the student
    async function fetchStudentCourses(studentId) {
        try {
            const response = await fetch(`/student/courses/${studentId}`);  // Added backticks for string interpolation
            const courses = await response.json();
            if (response.ok) {
                courses.forEach(course => {
                    fetchCourseQR(course.code);
                });
            } else {
                console.error("Failed to fetch student courses.");
            }
        } catch (error) {
            console.error("Error fetching student courses:", error);
        }
    }
    
    // Example: Replace with actual student ID from session storage or login response
    const studentId = 1; // This should be dynamically retrieved
    fetchStudentCourses(studentId);
});

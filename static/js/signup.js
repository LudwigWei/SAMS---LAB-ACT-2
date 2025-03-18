document.addEventListener('DOMContentLoaded', function() {
    // Close button functionality
    document.querySelector('.close-button').addEventListener('click', function() {
        alert("Close button clicked");
        window.location.href = '/';
    });
});
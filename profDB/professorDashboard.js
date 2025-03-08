document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const modal = document.querySelector('.modal');
    const modalOverlay = document.querySelector('.modal-overlay');
    const courseCard = document.querySelector('.course-card');
    const courseMenu = document.querySelector('.course-menu');
    const profileWrapper = document.querySelector('.profile-wrapper');
    const confirmationModal = document.querySelector('.confirmation-modal');
    const cancelButton = document.querySelector('.btn-cancel');
    const logoutButton = document.querySelector('.btn-logout');
    const addButton = document.querySelector('.add-button');
    const addClassModal = document.querySelector('.add-class-modal');

    // Profile (now logout) click handler
    profileWrapper.addEventListener('click', function(e) {
        e.stopPropagation();
        confirmationModal.style.display = 'block';
        modalOverlay.style.display = 'block';
    });

    // Cancel button click handler
    cancelButton.addEventListener('click', function() {
        confirmationModal.style.display = 'none';
        modalOverlay.style.display = 'none';
        addClassModal.style.display = 'none';
    });

    // Logout button click handler
    logoutButton.addEventListener('click', function() {
        alert('Logging out...');
        confirmationModal.style.display = 'none';
        modalOverlay.style.display = 'none';
    });

    // Close modals when clicking overlay
    modalOverlay.addEventListener('click', function() {
        modal.style.display = 'none';
        confirmationModal.style.display = 'none';
        modalOverlay.style.display = 'none';
        addClassModal.style.display = 'none';
    });

    // Course card click handler
    courseCard.addEventListener('click', function(e) {
        if (!e.target.classList.contains('course-menu')) {
            modal.style.display = 'block';
            modalOverlay.style.display = 'block';
        }
    });

    // Course menu click handler
    courseMenu.addEventListener('click', function(e) {
        e.stopPropagation();
        alert('Course menu clicked');
    });

    // Add button click handler with feedback
    addButton.addEventListener('click', function() {
        // Show feedback animation
        this.style.transform = 'scale(0.9)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 100);
        addClassModal.style.display = 'block';
        modalOverlay.style.display = 'block';
    });


});
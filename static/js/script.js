// Add any necessary JavaScript functionality here
document.addEventListener('DOMContentLoaded', function() {
    // Handle login functionality
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(loginForm);
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.redirected) {
                    window.location.href = response.url;
                }
            } catch (error) {
                console.error('Login error:', error);
            }
        });
    }

    // Handle sign up functionality
    const signupLink = document.querySelector('.signup-link');
    if (signupLink) {
        signupLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/signup';
        });
    }

    // Handle forgot password functionality
    const forgotPassword = document.querySelector('.forgot-password');
    if (forgotPassword) {
        forgotPassword.addEventListener('click', function() {
            alert("Forgot password clicked");
        });
    }

    // Added event listeners for About, Contact Us
    document.querySelectorAll(".nav-item").forEach(function(item) {
        item.addEventListener("click", function() {
            alert(item.textContent + " clicked");
        });
    });

    // Get started button
    document.querySelectorAll(".get-started-button").forEach(function(item) {
        item.addEventListener("click", function() {
            alert(item.textContent + " clicked");
        });
    });

    // Remember me checkbox
    const rememberMe = document.querySelector(".remember-me");
    if (rememberMe) {
        rememberMe.addEventListener("change", function() {
            alert("Remember me " + (this.checked ? "checked" : "unchecked"));
        });
    }
});

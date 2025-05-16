// DOM Elements
const cartCount = document.querySelector('.cart-count');
const addToCartButtons = document.querySelectorAll('.add-to-cart');
const newsletterForm = document.getElementById('newsletter-form');
const cartIcon = document.querySelector('.cart');

// Cart Functionality
let cartItems = 0;

addToCartButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Get product details
        const item = button.closest('.item');
        const title = item.querySelector('h3').textContent;
        const price = item.querySelector('.price').textContent;
        const image = item.querySelector('img').src;
        
        // Add to cart
        addToCart(title, price, image);
        
        // Show notification
        showNotification(`${title} ajouté au panier`, 'success');
        
        // Button animation
        button.textContent = 'Ajouté!';
        button.style.backgroundColor = 'var(--success-color)';
        
        setTimeout(() => {
            button.textContent = 'Ajouter au panier';
            button.style.backgroundColor = 'var(--primary-color)';
        }, 2000);
    });
});

// Newsletter Form Submission
newsletterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = newsletterForm.querySelector('input').value;
    
    // Simple email validation
    if (validateEmail(email)) {
        showNotification('Merci pour votre inscription!', 'success');
        newsletterForm.reset();
    } else {
        showNotification('Veuillez saisir une adresse email valide', 'error');
    }
});

function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// Notifications
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animation for notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            window.scrollTo({
                top: target.offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Add the notification styles dynamically
const style = document.createElement('style');
style.textContent = `
  .notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 15px 25px;
    background-color: white;
    color: #333;
    border-radius: 5px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.5s ease;
    z-index: 1000;
  }
  
  .notification.show {
    transform: translateY(0);
    opacity: 1;
  }
  
  .notification.success {
    border-left: 4px solid var(--success-color);
  }
  
  .notification.error {
    border-left: 4px solid var(--danger-color);
  }
`;
document.head.appendChild(style);

// Animation on scroll
window.addEventListener('scroll', () => {
    const elements = document.querySelectorAll('.item, .post');
    
    elements.forEach(element => {
        const position = element.getBoundingClientRect();
        
        if (position.top < window.innerHeight - 100) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
});

// Initialize animations
document.querySelectorAll('.item, .post').forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'all 0.5s ease';
});

// Load animation for hero section
window.addEventListener('load', () => {
    const heroContent = document.querySelector('.hero-content');
    heroContent.style.opacity = '0';
    heroContent.style.transform = 'translateY(30px)';
    heroContent.style.transition = 'all 1s ease';
    
    setTimeout(() => {
        heroContent.style.opacity = '1';
        heroContent.style.transform = 'translateY(0)';
    }, 300);
});

// Add event listener to cart icon
cartIcon.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleCart();
});

// Initialize cart functionality
document.addEventListener('DOMContentLoaded', initCart);
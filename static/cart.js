// Cart functionality
let cart = [];
let isCartOpen = false;

// Add item to cart
function addToCart(title, price, image) {
    // Check if item already exists in cart
    const existingItem = cart.find(item => item.title === title);
    
    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({
            title,
            price,
            image,
            quantity: 1
        });
    }
    
    updateCartCount();
    updateCartItems();
    saveCartToLocalStorage();
}

// Update cart count
function updateCartCount() {
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    const cartCount = document.querySelector('.cart-count');
    cartCount.textContent = totalItems;
    
    // Animation for cart count update
    cartCount.style.transform = 'scale(1.3)';
    setTimeout(() => {
        cartCount.style.transform = 'scale(1)';
    }, 300);
}

// Update cart items in the cart panel
function updateCartItems() {
    const cartItemsContainer = document.querySelector('.cart-items');
    cartItemsContainer.innerHTML = '';
    
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p class="empty-cart">Votre panier est vide</p>';
        return;
    }
    
    let total = 0;
    
    cart.forEach((item, index) => {
        const itemPrice = parseFloat(item.price.replace('€', '').replace(',', '.').trim());
        const itemTotal = itemPrice * item.quantity;
        total += itemTotal;
        
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <div class="cart-item-image">
                <img src="${item.image}" alt="${item.title}">
            </div>
            <div class="cart-item-details">
                <h4>${item.title}</h4>
                <p class="cart-item-price">${item.price}</p>
                <div class="cart-item-quantity">
                    <button class="quantity-btn minus" data-index="${index}">-</button>
                    <span>${item.quantity}</span>
                    <button class="quantity-btn plus" data-index="${index}">+</button>
                </div>
            </div>
            <button class="remove-item" data-index="${index}">
                <i class="fas fa-trash"></i>
            </button>
        `;
        
        cartItemsContainer.appendChild(cartItem);
    });
    
    // Add total
    const totalElement = document.createElement('div');
    totalElement.className = 'cart-total';
    totalElement.innerHTML = `
        <span>Total:</span>
        <span>${total.toFixed(2)} €</span>
    `;
    
    cartItemsContainer.appendChild(totalElement);
    
    // Add event listeners to buttons
    document.querySelectorAll('.quantity-btn').forEach(btn => {
        btn.addEventListener('click', handleQuantityChange);
    });
    
    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', handleRemoveItem);
    });
}

// Handle quantity change
function handleQuantityChange(e) {
    const index = parseInt(e.target.getAttribute('data-index'));
    
    if (e.target.classList.contains('plus')) {
        cart[index].quantity++;
    } else if (e.target.classList.contains('minus')) {
        if (cart[index].quantity > 1) {
            cart[index].quantity--;
        } else {
            cart.splice(index, 1);
        }
    }
    
    updateCartCount();
    updateCartItems();
    saveCartToLocalStorage();
}

// Handle remove item
function handleRemoveItem(e) {
    const index = parseInt(e.target.closest('.remove-item').getAttribute('data-index'));
    cart.splice(index, 1);
    
    updateCartCount();
    updateCartItems();
    saveCartToLocalStorage();
}

// Toggle cart panel
function toggleCart() {
    const cartPanel = document.querySelector('.cart-panel');
    isCartOpen = !isCartOpen;
    
    if (isCartOpen) {
        cartPanel.classList.add('open');
        updateCartItems();
    } else {
        cartPanel.classList.remove('open');
    }
}

// Save cart to localStorage
function saveCartToLocalStorage() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

// Load cart from localStorage
function loadCartFromLocalStorage() {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
        cart = JSON.parse(savedCart);
        updateCartCount();
    }
}

// Initialize cart
function initCart() {
    loadCartFromLocalStorage();
    
    // Close cart when clicking outside
    document.addEventListener('click', (e) => {
        const cartPanel = document.querySelector('.cart-panel');
        const cartIcon = document.querySelector('.cart');
        
        if (isCartOpen && !cartPanel.contains(e.target) && !cartIcon.contains(e.target)) {
            toggleCart();
        }
    });

    // Cart action buttons
    document.querySelector('.close-cart').addEventListener('click', toggleCart);
    document.querySelector('.continue-shopping').addEventListener('click', toggleCart);
    document.querySelector('.checkout-btn').addEventListener('click', () => {
        if (cart.length > 0) {
            showNotification('Redirection vers le paiement...', 'success');
            // Here you would typically redirect to a checkout page
            setTimeout(() => {
                alert('Cette fonctionnalité serait connectée à une page de paiement dans un site réel.');
            }, 1000);
        } else {
            showNotification('Votre panier est vide', 'error');
        }
    });
}

// Call the initCart function
initCart();

// Add event listener to add to cart buttons
document.querySelectorAll('.add-to-cart').forEach(button => {
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
})

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
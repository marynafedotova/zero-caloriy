// Для мобільних пристроїв
document.addEventListener('DOMContentLoaded', function() {
  const dropdowns = document.querySelectorAll('.dropdown');
  
  dropdowns.forEach(dropdown => {
    dropdown.addEventListener('click', function(e) {
      if (window.innerWidth <= 768) {
        e.preventDefault();
        this.classList.toggle('active');
      }
    });
  });
});

document.addEventListener('DOMContentLoaded', function() {
  const hash = window.location.hash;
  
  if (hash) {
    // Використовуємо MutationObserver для відстеження змін DOM
    const observer = new MutationObserver(function(mutations) {
      const element = document.querySelector(hash);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
        observer.disconnect(); // Зупинити спостереження після знаходження
      }
    });
    
    // Спостереження за змінами в DOM
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
    
    // Автоматично зупинити спостереження через 5 секунд
    setTimeout(() => observer.disconnect(), 5000);
  }
});
function getCart() {
    let cart = sessionStorage.getItem('cart');
    return cart ? JSON.parse(cart) : [];
}


function addToCart(productId) {

    let cart = sessionStorage.getItem('cart');
    cart = cart ? JSON.parse(cart) : [];

    const existingItem = cart.find(item => item.id === productId);

    if (existingItem) {
        existingItem.qty += 1;
    } else {
        cart.push({ id: productId, qty: 1 });
    }

    sessionStorage.setItem('cart', JSON.stringify(cart));

    openModal(); // ← ВАЖНО: вызываем модалку
}

// --- Модальное окно ---
const modalOverlay = document.getElementById('modalOverlay');
const closeModal = document.getElementById('closeModal');
const continueShopping = document.getElementById('continueShopping');
const goToCart = document.getElementById('goToCart');

function openModal() {
  modalOverlay.classList.add('active');
}

function hideModal() {
  modalOverlay.classList.remove('active');
}

closeModal.addEventListener('click', hideModal);
continueShopping.addEventListener('click', hideModal);

goToCart.addEventListener('click', () => {
window.location.href = 'assets/pages/cart.html';
});

modalOverlay.addEventListener('click', (e) => {
  if (e.target === modalOverlay) hideModal();
});

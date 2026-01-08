//hamburger-menu
document.getElementById('hamb-btn').addEventListener('click', function () {
  document.body.classList.toggle('open-mobile-menu')
})

document.getElementById('hamb-btn-mobile').addEventListener('click', function () {
  document.body.classList.toggle('open-mobile-menu')
})

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
        observer.disconnect();
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

// --- Модальное окно ---

const modalOverlay = document.getElementById('modalOverlay');

function showAddedMessage() {
  modalOverlay.classList.add('active');

  setTimeout(() => {
    modalOverlay.classList.remove('active');
  }, 1500); // 1.5 секунды — оптимально
}


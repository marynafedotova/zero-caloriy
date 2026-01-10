//hamburger-menu
document.getElementById('hamb-btn').addEventListener('click', function () {
  document.body.classList.toggle('open-mobile-menu')
})

document.getElementById('hamb-btn-mobile').addEventListener('click', function () {
  document.body.classList.toggle('open-mobile-menu')
})
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.mobile-menu a').forEach(link => {
    link.addEventListener('click', () => {
      document.body.classList.remove('open-mobile-menu');
    });
  });
});

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

document.addEventListener('DOMContentLoaded', () => {
  const search = document.querySelector('.search');
  const form = search.querySelector('form');
  const button = search.querySelector('.search-btn');
  const input = search.querySelector('input[type="search"]');

  button.addEventListener('click', (e) => {
    const isActive = search.classList.contains('active');
    const hasValue = input.value.trim().length > 0;

    if (!isActive) {
      e.preventDefault();
      search.classList.add('active');
      input.focus();
      return;
    }

    if (!hasValue) {
      e.preventDefault();
      input.focus();
      return;
    }

  });
});

document.addEventListener('DOMContentLoaded', () => {
  if (window.location.hash) {
    const target = document.querySelector(window.location.hash);
    if (target) {
      setTimeout(() => {
        target.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }
});



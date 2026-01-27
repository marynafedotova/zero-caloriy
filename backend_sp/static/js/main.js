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

document.querySelectorAll('.index-product-nutrition').forEach(element => {
    const original = element.textContent
        .replace(/\n/g, ' ')          
        .replace(/\s+/g, ' ')         
        .trim();                    
    
    // console.log('Очищенный текст:', original);
    // console.log('Длина:', original.length);
    
    if (original.length > 33) {
        element.textContent = original.substring(0, 45) + '...';
        // console.log('Обрезано до:', element.textContent);
    } else {
        element.textContent = original;
    }
});


document.addEventListener('DOMContentLoaded', function() {
  const hash = window.location.hash;
  
  if (hash) {
    const observer = new MutationObserver(function(mutations) {
      const element = document.querySelector(hash);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
        observer.disconnect();
      }
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
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
  const searchContainer = document.querySelector('.search');
  const searchForm = searchContainer.querySelector('form');
  const input = searchForm.querySelector('input[type="search"]');
  const searchBtn = document.getElementById('btn-search-mobile');
  
  if (!searchBtn || !searchContainer) return;
  
  // Удаляем inline-стиль при загрузке
  searchContainer.style.display = '';
  
  const isMobile = () => window.innerWidth <= 855;
  
  // Функция для обновления видимости
  const updateVisibility = () => {
    if (isMobile()) {
      searchBtn.style.display = 'block';
      if (searchContainer.classList.contains('active')) {
        searchContainer.style.display = 'block';
      } else {
        searchContainer.style.display = 'none';
      }
    } else {
      searchBtn.style.display = 'none';
      searchContainer.style.display = 'block';
      searchContainer.classList.remove('active');
    }
  };
  
  // Переключение формы
  searchBtn.addEventListener('click', (e) => {
    if (!isMobile()) return;
    
    e.preventDefault();
    
    if (!searchContainer.classList.contains('active')) {
      // Показываем форму
      searchContainer.classList.add('active');
      searchContainer.style.display = 'block';
      input.focus();
    } else {
      // Скрываем форму или отправляем
      if (input.value.trim() === '') {
        searchContainer.classList.remove('active');
        searchContainer.style.display = 'none';
      } else {
        searchForm.submit();
      }
    }
  });
  
  // Скрываем форму при клике вне ее
  document.addEventListener('click', (e) => {
    if (isMobile() && 
        searchContainer.classList.contains('active') &&
        !searchContainer.contains(e.target) && 
        !searchBtn.contains(e.target)) {
      searchContainer.classList.remove('active');
      searchContainer.style.display = 'none';
    }
  });
  
  // Инициализация
  updateVisibility();
  
  // При изменении размера окна
  window.addEventListener('resize', updateVisibility);
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


document.addEventListener('DOMContentLoaded', () => {

  async function updateCartCounter() {
    const counter = document.getElementById('cart-counter');
    if (!counter) return;

    try {
      const response = await fetch('/carts/count/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });

      if (!response.ok) return;

      const data = await response.json();

      counter.textContent = data.count;
      counter.style.display = data.count > 0 ? 'flex' : 'none';

    } catch (e) {
      console.warn('Cart counter unavailable');
    }
  }

  document.querySelectorAll('form.add-to-cart-form').forEach(form => {

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: {
            'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        if (response.ok) {
          await updateCartCounter();
        }

      } catch (e) {
        console.warn('Add to cart failed');
      }
    });

  });

  updateCartCounter();

});


document.addEventListener('DOMContentLoaded', () => {
  const picker = document.querySelector('.language-picker');
  const toggle = picker.querySelector('.icon-language');

  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    picker.classList.toggle('active');
  });

  document.addEventListener('click', () => {
    picker.classList.remove('active');
  });

  // Добавляем подсветку текущего языка через JS
  const currentLang = "{{ LANGUAGE_CODE }}"; // Django подставляет текущий язык
  picker.querySelectorAll('.lang-buttons button').forEach(btn => {
    if (btn.value === currentLang) {
      btn.classList.add('active');
    }
  });
});


document.addEventListener('DOMContentLoaded', () => {
  const cartLink = document.querySelector('.cart-account a');
  if (window.location.pathname.endsWith('/goods/cart/')) {
    cartLink.classList.add('active');
  }
});


  document.addEventListener('DOMContentLoaded', () => {
    const toggles = document.querySelectorAll('.catalog-toggle');

    toggles.forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        e.preventDefault();

        const item = toggle.closest('.catalog-item');
        item.classList.toggle('is-open');
      });
    });
  });


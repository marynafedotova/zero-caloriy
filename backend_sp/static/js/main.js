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

document.addEventListener('DOMContentLoaded', () => {
  const titles = document.querySelectorAll('.product-title');

  titles.forEach(title => {
    const text = title.textContent.trim();

    const match = text.match(/(\s[MXL])$/);
    if (match) {
      const size = match[1]; 
      const name = text.slice(0, -size.length); 

      title.innerHTML = `${name} <span class="product-size-item">${size.trim()}</span>`;
    }
  });
});

function markCartItems(cartItems) {
    if (!Array.isArray(cartItems)) return;

    cartItems.forEach(slug => {
        // Находим все карточки товара с этим slug на странице
        const cards = document.querySelectorAll(`.product-card[data-slug="${slug}"]`);
        cards.forEach(card => {
            // 1. Скрываем кнопки "Добавить в корзину"
            card.querySelectorAll('.add-to-cart-btn, .add-to-cart-btn-m')
                .forEach(btn => {
                    btn.style.display = 'none';
                    btn.onclick = null;
                });

            // 2. Показываем галочку
            const check = card.querySelector('.product-to-cart');
            if (check) {
                check.hidden = false;
                check.style.display = 'flex';
            }

            // 3. Класс для отметки "в корзине"
            card.classList.add('in-cart');
        });
    });
}
// /* ---------- Автопроверка товаров в корзине при загрузке страницы ---------- */
// function markCartItemsOnPage() {
//     if (!Array.isArray(window.cartItemsOnLoad)) return;

//     window.cartItemsOnLoad.forEach(slug => {
//         const cards = document.querySelectorAll(`.product-card[data-slug="${slug}"]`);
//         cards.forEach(card => {
//             // Скрываем кнопки "Добавить в корзину"
//             card.querySelectorAll('.add-to-cart-btn, .add-to-cart-btn-m')
//                 .forEach(btn => {
//                     btn.style.display = 'none';
//                     btn.onclick = null;
//                 });

//             // Показываем галочку
//             const check = card.querySelector('.product-to-cart');
//             if (check) {
//                 check.hidden = false;
//                 check.style.display = 'flex';
//             }

//             // Класс "в корзине"
//             card.classList.add('in-cart');
//         });
//     });
// }

// /* Автоматический вызов при загрузке страницы */
// document.addEventListener('DOMContentLoaded', markCartItemsOnPage);



// ====== При загрузке страницы получаем товары из корзины и помечаем ======
// document.addEventListener('DOMContentLoaded', function () {
//     fetch('/carts/count/')  
//         .then(res => res.json())
//         .then(data => {
//             if (data.items && data.items.length) {
//                 markCartItems(data.items);
//             }
//         })
//         .catch(err => console.error('Ошибка при получении товаров корзины:', err));
// });



fetch('/carts/count/')
    .then(res => {
        // console.log('Status:', res.status);
        return res.json();
    })
    .then(data => {
        // console.log('Cart count response:', data);

        // ✅ ВОТ ЭТА ВСТАВКА
        if (data.items && typeof applyCartItems === 'function') {
            // console.log('[Cart] Applying items from AJAX:', data.items);
            applyCartItems(data.items);
        }

        const counter = document.querySelector('.cart-counter');
        if (counter) {
            // console.log('Updating counter with:', data.count);
            counter.textContent = data.count;
        }
    })
    .catch(err => console.error('Ошибка:', err));

// обмеження тексту в карточках товару
function limitTextAdaptive() {
    // console.log('=== limitTextAdaptive RUN ===');

    const elements = document.querySelectorAll('.index-product-nutrition');
    const maxLength = 30;

    // console.log('Elements found:', elements.length);
    // console.log('Max length:', maxLength);

    elements.forEach((el, index) => {
        // console.log(`--- Element #${index + 1} ---`);

        let fullText = el.getAttribute('data-full-text');

        // якщо ще не обробляли — беремо сирий текст і нормалізуємо
        if (!fullText) {
            fullText = el.textContent;

            // console.log('Raw text:', fullText);

            // нормалізація: перенос → масив → trim → прибрати пусті / None → join через ', '
            fullText = fullText
                .split('\n')
                .map(item => item.trim())
                .filter(item => item && item !== 'None')
                .join(', ')
                .trim();

            // прибрати кому на початку, якщо є
            fullText = fullText.replace(/^,\s*/, '');

            // прибрати кому в кінці
            fullText = fullText.replace(/,\s*$/, '');

            el.setAttribute('data-full-text', fullText);

            // console.log('Normalized text:', fullText);
        }

        // console.log('Length:', fullText.length);

        if (fullText.length > maxLength) {
            let truncated = fullText.substring(0, maxLength);

            // не рвемо слово
            const lastSpace = truncated.lastIndexOf(' ');
            if (lastSpace > 0) {
                truncated = truncated.substring(0, lastSpace);
            }

            el.textContent = truncated + '...';

            // console.log('Truncated:', el.textContent);
        } else {
            el.textContent = fullText;
            // console.log('No truncation needed');
        }
    });

    // console.log('=== END ===');
}
// запуск
limitTextAdaptive();

// resize
window.addEventListener('resize', limitTextAdaptive);






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
// пошук
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
  
  document.addEventListener('click', (e) => {
    if (isMobile() && 
        searchContainer.classList.contains('active') &&
        !searchContainer.contains(e.target) && 
        !searchBtn.contains(e.target)) {
      searchContainer.classList.remove('active');
      searchContainer.style.display = 'none';
    }
  });
  updateVisibility();
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

// мови
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

  const currentLang = "{{ LANGUAGE_CODE }}"; 
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


document.addEventListener('DOMContentLoaded', () => {
    fetch('../data/data.json')
        .then(response => response.json())
        .then(products => {
            const desserts = products.filter(item => item['Категория'] === 'Дессерт');
            const drinks = products.filter(item => item['Категория'] === 'Напої');

            // Рендер десертів
            if (desserts.length > 0) {
                renderProducts(desserts, 'catalog-list-dessert');
            } else {
                document.getElementById('catalog-list-dessert').innerHTML =
                    '<p class="no-products">Десерти відсутні</p>';
            }

            // Рендер напоїв (без пагінації)
            if (drinks.length > 0) {
                renderProducts(drinks, 'catalog-list-drinks');
            } else {
                document.getElementById('catalog-list-drinks').innerHTML =
                    '<p class="no-products">Напої відсутні</p>';
            }
        })
        .catch(error => console.error('Ошибка загрузки товаров:', error));
});

function renderProducts(list, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    const perPage = 8; // Всегда 8
    let currentPage = 1;
    const totalPages = Math.ceil(list.length / perPage);

    function renderPage(page) {
        container.innerHTML = '';
        const start = (page - 1) * perPage;
        const end = start + perPage;
        const pageItems = list.slice(start, end);

        pageItems.forEach(item => {
            const productCard = createProductCard(item);
            container.appendChild(productCard);
        });
    }

    renderPage(currentPage);

    // Создаём пагинацию всегда, если больше одной страницы
    if (totalPages > 1) {
        let paginationContainer = container.nextElementSibling;
        if (!paginationContainer || !paginationContainer.classList.contains('pagination')) {
            paginationContainer = document.createElement('div');
            paginationContainer.className = 'pagination';
            container.parentNode.insertBefore(paginationContainer, container.nextSibling);
        }
        paginationContainer.innerHTML = '';

        const prevBtn = document.createElement('button');
        prevBtn.textContent = '←';
        prevBtn.disabled = true;

        const nextBtn = document.createElement('button');
        nextBtn.textContent = '→';

        paginationContainer.appendChild(prevBtn);
        paginationContainer.appendChild(nextBtn);

        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderPage(currentPage);
                prevBtn.disabled = currentPage === 1;
                nextBtn.disabled = currentPage === totalPages;
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderPage(currentPage);
                prevBtn.disabled = currentPage === 1;
                nextBtn.disabled = currentPage === totalPages;
            }
        });
    }
}

// Функція для створення картки товару
function createProductCard(item) {
    const productCard = document.createElement('div');
    productCard.className = 'product-card';

    productCard.innerHTML = `
        <a href="../pages/product.html?id=${item['ID']}" class="product-link">
            <div class="product-img">
                <img src="/zero-caloriy/${item['Зображення']}" alt="${item['Назва']}" class="product-image">
            </div>
            <div class="product-info">
                <h3 class="product-title">${item['Назва']}</h3>
                <p class="product-weight">${item["Вага"]}</p>
            </div>
        </a>
        <div class="product-catalog-btn">
            <div class="product-price">
                ${item['Ціна']}
                <div class="product-price-uah">грн</div>
            </div>
            <button class="add-to-cart" data-id="${item['ID']}">
                <img src="../img/+.svg" alt="add to cart">
            </button>
        </div>
    `;

    // Підключаємо обробник кнопки прямо тут
    const addBtn = productCard.querySelector('.add-to-cart');
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            const productId = addBtn.getAttribute('data-id');
            addToCart(productId); // твоя функція для кошика
        });
    }

    return productCard;
}


    
// Обработчики для кнопок корзины
container.querySelectorAll('.add-to-cart').forEach(btn => {
    btn.addEventListener('click', function () {
        const productId = this.getAttribute('data-id');
        addToCart(productId);  // ← Добавление в корзину
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
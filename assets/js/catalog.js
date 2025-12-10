document.addEventListener('DOMContentLoaded', () => {
    fetch('../data/data.json')
        .then(response => response.json())
        .then(products => {
            // Фильтруем продукты по категориям
            const desserts = products.filter(item => item['Категория'] === 'Дессерт');
            const drinks = products.filter(item => item['Категория'] === 'Напої');
            
            // Рендерим десерты
            if (desserts.length > 0) {
                renderProducts(desserts, 'catalog-list-dessert');
            } else {
                document.getElementById('catalog-list-dessert').innerHTML = 
                    '<p class="no-products">Десерти відсутні</p>';
            }
            
            // Рендерим напитки
            if (drinks.length > 0) {
                renderProducts(drinks, 'catalog-list-drinks');
            } else {
                document.getElementById('catalog-list-drinks').innerHTML = 
                    '<p class="no-products">Напої відсутні</p>';
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки товаров:', error);
        });
});

function renderProducts(list, containerId) {
    const container = document.getElementById(containerId);
    
    if (!container) return;
    
    container.innerHTML = '';
    
list.forEach(item => {
    const productCard = document.createElement('div');
    productCard.className = 'product-card';

    productCard.innerHTML = `
        <a href="../pages/product.html?id=${item['ID']}" class="product-link">
            <div class="product-img">
                <img src="/${item['Зображення']}" alt="${item['Назва']}" class="product-image">
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

    container.appendChild(productCard);
});
    
// Обработчики для кнопок корзины
container.querySelectorAll('.add-to-cart').forEach(btn => {
    btn.addEventListener('click', function () {
        const productId = this.getAttribute('data-id');
        addToCart(productId);  // ← Добавление в корзину
    });
});
}
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
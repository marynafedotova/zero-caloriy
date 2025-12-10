document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const productId = parseInt(params.get('id'), 10);

    fetch('../data/data.json')
        .then(res => res.json())
        .then(products => {
            const product = products.find(p => p.ID === productId);
            if (!product) return;

            // Елементи
            const imgEl = document.querySelector('.product-image');
            const titleEl = document.querySelector('.product-title');
            const priceEl = document.querySelector('.product-price');
            const descEl = document.querySelector('.product-desc');
            const ingredientsEl = document.querySelector('.product-ingredients');
            const nutritionEl = document.querySelector('.nutrition-list');
            const addToCartBtn = document.querySelector('.add-to-cart');

            // Підставляємо
            imgEl.src = '/zero-caloriy/'+  product['Зображення'];
            titleEl.textContent = product['Назва'];
            priceEl.textContent = product['Ціна'] + ' грн';
            descEl.textContent = product['Опис'];
            ingredientsEl.textContent = product['Склад'];

            // додаємо ID у кнопку
            addToCartBtn.dataset.id = product.ID;

            // КБЖУ
            nutritionEl.innerHTML = '';
            const kbju = product['КБЖУ'];
            for (const key in kbju) {
                const li = document.createElement('li');
                li.textContent = `${key}: ${kbju[key]}`;
                nutritionEl.appendChild(li);
            }
        });
});
document.addEventListener("click", (e) => {
    if (e.target.classList.contains("add-to-cart")) {
        const id = e.target.dataset.id;
        addToCart(id);
    }
});


document.addEventListener('DOMContentLoaded', () => {
    const favContainer = document.getElementById('favlist-products');
    const favShowAllBtn = document.getElementById('favlist-show-all');

    let favProducts = [];

    fetch('../data/data.json')
        .then(response => response.json())
        .then(products => {
            favProducts = products;
            renderFavProducts(products.slice(0, 4));

            favShowAllBtn.addEventListener('click', () => {
                favContainer.innerHTML = "";
                renderFavProducts(favProducts);
                favShowAllBtn.style.display = "none";
            });
        });
});

function renderFavProducts(list) {
    const favContainer = document.getElementById('favlist-products');

    list.forEach(item => {
        const li = document.createElement('li');
        li.className = 'product-card';
        const productLink = `../pages/product.html?id=${item['ID']}`;
        li.innerHTML = `
            <a href="${productLink}" class="product-link">
                <div class="product-img">
                    <img src="/zero-caloriy/${item['Зображення']}" alt="${item['Назва']}" class="product-image">
                </div>

                <div class="product-info">
                    <h3 class="product-title">${item['Назва']}</h3>
                    <p class="product-weight">${item["Вага"]}</p>


            </a>
                                <div class="product-cart">
                        <div class="product-price">
                            ${item['Ціна']}
                            <div class="product-price-uah">грн</div>
                        </div>
                <button class="add-to-cart" data-id="${item['ID']}">
                <img src="../img/+.svg" alt="add to cart">
            </button>

                    </div>
                </div>

        `;

        favContainer.appendChild(li);
    });

    // фиксируем обработчики
    favContainer.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation(); // если внутри ссылки
            const productId = this.getAttribute('data-id');
            addToCart(productId);
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
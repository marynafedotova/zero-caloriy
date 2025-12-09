document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('news-product');
    const btnShowAll = document.getElementById('show-all-btn');

    let allProducts = []; // сюди збережемо всі товари

    fetch('assets/data/data.json')
      .then(response => response.json())
      .then(products => {
          allProducts = products;

          renderProducts(products.slice(0, 4)); 

          btnShowAll.addEventListener('click', () => {
              container.innerHTML = ""; 
              renderProducts(allProducts); 
              btnShowAll.style.display = "none"; 
          });
      })
      .catch(error => console.error('Помилка завантаження файлу:', error));


    function renderProducts(list) {
        list.forEach(item => {
            const li = document.createElement('li');
            li.className = 'product-card';

        li.innerHTML = `
             <a href="assets/pages/product.html?id=${item['ID']}" class="product-link">
                <div class="product-img">
                    <img src="${item['Зображення']}" alt="${item['Назва']}" class="product-image">
                </div>

                <div class="product-info">
                    <h3 class="product-title">${item['Назва']}</h3>
                    <p class="product-weight">${item["Вага/об'єм (г/л)"]}</p>

                    <div class="product-cart">
                        <div class="product-price">
                            ${item['Ціна']}
                            <div class="product-price-uah">грн</div>
                        </div>

                        <button class="add-to-cart" data-id="${item['ID']}">
                            <img src="assets/img/+.svg" alt="add to cart">
                        </button>
                    </div>
                </div>
            </a>
        `;

            container.appendChild(li);
        });

        // навішуємо обробники після рендера
        document.querySelectorAll('.add-to-cart').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                console.log("Додано в корзину товар ID:", id);
            });
        });
    }
});


document.addEventListener('DOMContentLoaded', () => {
    const favContainer = document.getElementById('favlist-products');
    const favShowAllBtn = document.getElementById('favlist-show-all');

    let favProducts = [];

    fetch('assets/data/data.json')
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
        
        // Создаем ссылку на страницу товара
        const productLink = `http://127.0.0.1:5500/assets/pages/product.html?id=${item['ID'] || ''}`;
        
        li.innerHTML = `
        <a href="${productLink}" class="product-link">
            <div class="product-img">
                <img src="${item['Зображення']}" alt="${item['Назва']}" class="product-image">
            </div>

            <div class="product-info">
                <h3 class="product-title">${item['Назва']}</h3>
                <p class="product-weight">${item["Вага"]}</p>

                <div class="product-cart">
                    <div class="product-price">
                        ${item['Ціна']}
                        <div class="product-price-uah">грн</div>
                    </div>

                    <button class="add-to-cart" data-id="${item['ID'] || ''}">
                        <img src="assets/img/+.svg" alt="add to cart">
                    </button>
                </div>
            </div>
        </a>
        `;

        favContainer.appendChild(li);
    });

    // Используем делегирование событий для обработки кликов на кнопки
    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault(); // Предотвращаем переход по ссылке
            e.stopPropagation(); // Останавливаем всплытие события
            
            const id = btn.getAttribute('data-id');
            console.log("Додано в корзину товар ID:", id);
            // Здесь можно добавить логику добавления в корзину
        });
    });
}
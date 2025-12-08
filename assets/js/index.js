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

    let favProducts = []; // збережемо всі товари

    fetch('assets/data/data.json')
        .then(response => response.json())
        .then(products => {
            favProducts = products;

            // показуємо перші 4
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

        li.innerHTML = `
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

                <button class="add-to-cart" data-id="${item['ID'] || ''}">
                    <img src="assets/img/+.svg" alt="add to cart">
                </button>
            </div>
        </div>
        `;

        favContainer.appendChild(li);
    });

    // обробники додавання до кошика
    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            console.log("Додано в корзину товар ID:", id);
        });
    });
}

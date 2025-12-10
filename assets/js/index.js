document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('news-product');
    const btnShowAll = document.getElementById('show-all-btn');

    let allProducts = [];

fetch('assets/data/data.json')
  .then(response => response.json())
  .then(products => {
      let desserts = products.filter(item => item["Категория"] === "Дессерт");

      desserts.sort((a, b) => b.ID - a.ID);

      allProducts = desserts;
      renderProducts(desserts.slice(0, 4));

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
                        <p class="product-weight">${item["Вага"]}</p>

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
    }
});


// ---------------------------
// FAVORITES SECTION
// ---------------------------

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

        const productLink = `assets/pages/product.html?id=${item['ID']}`;

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
                <button class="add-to-cart" data-id="${item['ID']}">
                <img src="assets/img/+.svg" alt="add to cart">
            </button>

                    </div>
                </div>
            </a>

        `;

        favContainer.appendChild(li);
    });
}



// ---------------------------
// GLOBAL ADD-TO-CART HANDLER
// ---------------------------

document.addEventListener('click', (e) => {
    const btn = e.target.closest('.add-to-cart');
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();

    const id = btn.dataset.id;
    addToCart(id);
});


// ---------------------------
// CART STORAGE LOGIC
// ---------------------------

// function addToCart(productId) {
//     let cart = sessionStorage.getItem('cart');
//     cart = cart ? JSON.parse(cart) : [];

//     const existingItem = cart.find(item => item.id === productId);

//     if (existingItem) {
//         existingItem.qty += 1;
//     } else {
//         cart.push({ id: productId, qty: 1 });
//     }

//     sessionStorage.setItem('cart', JSON.stringify(cart));

//     openModal();
// }

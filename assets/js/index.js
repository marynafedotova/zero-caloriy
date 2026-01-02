document.addEventListener('DOMContentLoaded', () => {
    const track = document.getElementById('news-product');

    let products = [];

    fetch('assets/data/data.json')
        .then(res => res.json())
        .then(data => {
            products = data
                .filter(item => item['Категория'] === 'Дессерт')
                .sort((a, b) => b.ID - a.ID);

            renderProducts(products);
        })
        .catch(err => console.error('JSON error:', err));

    function renderProducts(list) {
        track.innerHTML = '';

        list.forEach(item => {
            const kbju = item['КБЖУ'];

            const li = document.createElement('li');
            li.className = 'product-card';

            li.innerHTML = `
                <a href="assets/pages/product.html?id=${item.ID}" class="product-link">
                    <div class="product-img">
                        <img src="${item['Зображення']}" alt="${item['Назва']}">
                    </div>

                    <div class="product-info">
                                    <div class="product-info">
                                <h3 class="product-title">${item['Назва']}</h3>
                                <p class="product-weight">${item["Вага"]}</p>
                            </div>
                            <div class="product-price">
                                ${item['Ціна']} <span class="product-price-uah">грн</span>

                             <button class="add-to-cart" data-id="${item.ID}">
                                <img src="assets/img/+.svg" alt="add to cart">
                            </button>    </div>

                       
                    </div>
                </a>
            `;

            track.appendChild(li);
        });
    }
});



// ---------------------------
// FAVORITES SECTION
// ---------------------------

document.addEventListener('DOMContentLoaded', () => {
    const favContainer = document.getElementById('favlist-products');

    if (!favContainer) {
        console.error('favlist-products not found');
        return;
    }

    // Завантажуємо всі товари
    fetch('assets/data/data.json')
        .then(res => res.json())
        .then(data => {
            renderFavProducts(data); // відображаємо всі товари
        })
        .catch(err => console.error('JSON error:', err));

    function renderFavProducts(list) {
        favContainer.innerHTML = '';

        list.forEach(item => {
            const li = document.createElement('li');
            li.className = 'product-card';

            const productLink = `assets/pages/product.html?id=${item.ID}`;

            li.innerHTML = `
                <a href="${productLink}" class="product-link">
                    <div class="product-img">
                        <img src="${item['Зображення']}" alt="${item['Назва']}" class="product-image">
                    </div>

                    <div class="product-info">
                        <h3 class="product-title">${item['Назва']}</h3>
                        <p class="product-weight">${item['Вага']}</p>

                        <div class="product-cart">
                            <div class="product-price">
                                ${item['Ціна']}
                                <span class="product-price-uah">грн</span>
                            </div>

                            <button class="add-to-cart" data-id="${item.ID}">
                                <img src="assets/img/+.svg" alt="add to cart">
                            </button>
                        </div>
                    </div>
                </a>
            `;

            favContainer.appendChild(li);
        });
    }
});



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

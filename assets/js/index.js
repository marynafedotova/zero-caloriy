document.addEventListener('DOMContentLoaded', () => {
    const track = document.getElementById('news-product');
    const prevBtn = document.getElementById('prevSlide');
    const nextBtn = document.getElementById('nextSlide');

    let products = [];
    let currentIndex = 0;

    fetch('assets/data/data.json')
        .then(res => res.json())
        .then(data => {
            products = data
                .filter(item => item['Категория'] === 'Дессерт')
                .sort((a, b) => b.ID - a.ID);

            renderProducts(products);
            updateSlider();
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

                    <div class="slide-img">
                        <img src="${item['Зображення']}" alt="${item['Назва']}">
                    </div>

                    <div class="product-info">
                        <h3 class="product-title">${item['Назва']}</h3>
                        

                        <p class="product-description">${item['Опис']}</p>
                        <div class="product-ingred-block">
                            <div class="product-ingred-title">Склад:</div> 
                            <div class="product-ingred">${item['Склад']}</div>
                         </div>
                        
                        <div class="news-block-kbju">
                        <h4 class="news-title-kbju">КБЖУ (100г):</h4>
                        <ul class="product-kbju">
                            <li>Калорії: ${kbju.Калорії} ккал</li>
                            <li>Білки: ${kbju.Білки} г</li>
                            <li>Жири: ${kbju.Жири} г</li>
                            <li>Вуглеводи: ${kbju.Вуглеводи} г</li>
                            <li>Хлібні одиниці: : ${kbju['Хлібні одиниці']}</li>
                        </ul>
                        </div>
                        <div class="product-cart-slider">
                        <div class="product-weight-slider">${item['Вага']}</div>
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

            track.appendChild(li);
        });
    }

    function updateSlider() {
        track.style.transform = `translateX(-${currentIndex * 100}%)`;
    }

    nextBtn.addEventListener('click', () => {
        if (!products.length) return;
        currentIndex = (currentIndex + 1) % products.length;
        updateSlider();
    });

    prevBtn.addEventListener('click', () => {
        if (!products.length) return;
        currentIndex =
            (currentIndex - 1 + products.length) % products.length;
        updateSlider();
    });
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

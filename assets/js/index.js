const heroLb = document.querySelector('.hero-lb');
const letters = document.querySelectorAll('.hero-lb .letter');

// плавное появление исходного слова
letters.forEach((letter, i) => {
  setTimeout(() => {
    letter.style.opacity = '1';
    letter.style.transform = 'translateY(0) scale(1)';
    letter.style.transition = 'transform 1s cubic-bezier(0.68, -0.55, 0.27, 1.55), opacity 1s ease';
    letter.classList.add('pulse'); // добавляем пульсацию
  }, i * 300);
});

const extraOs = 4;

for (let i = 0; i < extraOs; i++) {
  setTimeout(() => {
    const oLetter = document.createElement('img');
    oLetter.src = 'assets/img/о.png';
    oLetter.classList.add('letter');

    oLetter.style.opacity = '0';
    oLetter.style.transform = 'translateY(30px) scale(0.8)';

    const lastLetter = heroLb.lastElementChild;
    heroLb.insertBefore(oLetter, lastLetter);

    // плавное появление буквы 'о'
    setTimeout(() => {
      oLetter.style.opacity = '1';
      oLetter.style.transform = 'translateY(0) scale(1)';
      oLetter.style.transition = 'transform 1s cubic-bezier(0.68, -0.55, 0.27, 1.55), opacity 1s ease';
      oLetter.classList.add('pulse'); // пульсация для новых букв
    }, 50);

    // смещаем последнюю букву 'т' постепенно
    const shiftAmount = 35; 
    const totalShift = (i + 1) * shiftAmount;
    lastLetter.style.transition = 'transform 1s cubic-bezier(0.68, -0.55, 0.27, 1.55)';
    lastLetter.style.transform = `translateX(${totalShift}px)`;
    
  }, (letters.length + i) * 400);
}





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

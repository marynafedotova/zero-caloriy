    async function loadProductsData() {
    try {
        const res = await fetch('../data/data.json'); 
        if (!res.ok) throw new Error('Помилка завантаження продуктів');
        const data = await res.json();
        return data;
    } catch (err) {
        console.error(err);
        return [];
    }
}


document.addEventListener('DOMContentLoaded', async () => {
    const cartContainer = document.getElementById('cart-list'); // UL або DIV
    const cart = getCart();

    if (cart.length === 0) {
        cartContainer.innerHTML = "<p>Кошик порожній</p>";
        return;
    }

    const products = await loadProductsData();

    cart.forEach(cartItem => {
        const product = products.find(p => p.ID == cartItem.id);
        if (!product) return;

        const li = document.createElement('li');
        li.className = 'cart-item';

        li.innerHTML = `
            <div class="cart-img">
                <img src="/${product['Зображення']}" alt="${product['Назва']}">
            </div>

            <div class="cart-info">
            <div class="cart-top-info">
                <h3 class="cart-title">${product['Назва']}</h3>
                <button class="remove-from-cart" data-id="${product.ID}"><img src="../img/delete.svg" alt=""></button>

            </div>
                <p class="cart-weight">${product["Вага"] || ""}</p>
                <div class="cart-bottom">
                  <div class="cart-price">
                    ${product['Ціна']} грн
                  </div>
                  <div class="cart-controls">
                    <button class="qty-minus" data-id="${product.ID}"><img src="../img/minus.svg" alt=""></button>
                    <span class="qty-value">${cartItem.qty}</span>
                    <button class="qty-plus" data-id="${product.ID}"><img src="../img/plus.svg" alt=""></button>
                </div>
                </div>
                

                

                
            </div>
        `;

        cartContainer.appendChild(li);
    });

    attachCartHandlers();
});
function attachCartHandlers() {
    document.querySelectorAll('.qty-plus').forEach(btn => {
        btn.addEventListener('click', () => {
            changeQty(btn.dataset.id, 1);
        });
    });

    document.querySelectorAll('.qty-minus').forEach(btn => {
        btn.addEventListener('click', () => {
            changeQty(btn.dataset.id, -1);
        });
    });

    document.querySelectorAll('.remove-from-cart').forEach(btn => {
        btn.addEventListener('click', () => {
            removeFromCart(btn.dataset.id);
        });
    });
}
function changeQty(id, delta) {
    let cart = getCart();
    const item = cart.find(i => i.id == id);

    if (!item) return;

    item.qty += delta;

    if (item.qty <= 0) {
        cart = cart.filter(i => i.id != id);
    }

    sessionStorage.setItem('cart', JSON.stringify(cart));
    location.reload(); // перерендер
}
function removeFromCart(id) {
    let cart = getCart();
    cart = cart.filter(item => item.id != id);
    sessionStorage.setItem('cart', JSON.stringify(cart));
    location.reload();
}



function getCart() {
    let cart = sessionStorage.getItem('cart');
    return cart ? JSON.parse(cart) : [];
}

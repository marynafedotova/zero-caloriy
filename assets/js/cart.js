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
                    <div class="cart-price" data-price="${product['Ціна']}">
                        ${product['Ціна'] * cartItem.qty} грн
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
updateCartTotal();

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
        sessionStorage.setItem('cart', JSON.stringify(cart));
        document.querySelector(`[data-id="${id}"]`).closest('.cart-item').remove();
        updateCartTotal();
        return;
    }

    sessionStorage.setItem('cart', JSON.stringify(cart));

    // обновляем количество на странице
    const cartItem = document.querySelector(`.qty-plus[data-id="${id}"]`).closest('.cart-item');
    cartItem.querySelector('.qty-value').textContent = item.qty;

    updateCartTotal();
}
function removeFromCart(id) {
    let cart = getCart().filter(item => item.id != id);
    sessionStorage.setItem('cart', JSON.stringify(cart));

    document.querySelector(`[data-id="${id}"]`).closest('.cart-item').remove();
    updateCartTotal();
}



function getCart() {
    let cart = sessionStorage.getItem('cart');
    return cart ? JSON.parse(cart) : [];
}
function updateCartTotal() {
    let total = 0;

    document.querySelectorAll('.cart-item').forEach(item => {
        const priceEl = item.querySelector('.cart-price');
        const qtyEl = item.querySelector('.qty-value');

        const price = Number(priceEl.dataset.price); // цена за 1 шт
        const qty = Number(qtyEl.textContent);       // количество

        total += price * qty;

        // обновляем цену за товар
        priceEl.textContent = (price * qty) + ' грн';
    });

    document.querySelector('.sum').textContent = total + ' грн';
}

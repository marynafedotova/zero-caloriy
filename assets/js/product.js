document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const productId = parseInt(params.get('id'), 10);

    fetch('../data/data.json')
        .then(res => res.json())
        .then(products => {
            const product = products.find(p => p.ID === productId);
            if (!product) return;

            // Елементи на сторінці
            const imgEl = document.querySelector('.product-image');
            const titleEl = document.querySelector('.product-title');
            const priceEl = document.querySelector('.product-price');
            const descEl = document.querySelector('.product-desc');      // для опису
            const ingredientsEl = document.querySelector('.product-ingredients'); // для складу
            const nutritionEl = document.querySelector('.nutrition-list');

            // Підставляємо дані
            imgEl.src = "/" + product['Зображення'];
            imgEl.alt = product['Назва'];
            titleEl.textContent = product['Назва'];
            priceEl.textContent = product['Ціна'] + ' грн';
            descEl.textContent = product['Опис']; // окремо опис
            ingredientsEl.textContent = product['Склад']; // окремо склад

            // КБЖУ
            nutritionEl.innerHTML = '';
            const kbju = product['КБЖУ'];
            for (const key in kbju) {
                const li = document.createElement('li');
                li.textContent = `${key}: ${kbju[key]}`;
                nutritionEl.appendChild(li);
            }
        })
        .catch(err => console.error(err));
});

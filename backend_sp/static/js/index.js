// const heroLb = document.querySelector('.hero-lb');
// const letters = document.querySelectorAll('.hero-lb .letter');
// const extraOs = 4;
// const shiftAmount = 35;

// const oLetter = document.createElement('img');
// oLetter.src = oSrc; 

// const oLetters = [];
// for (let i = 0; i < extraOs; i++) {
//   const oLetter = document.createElement('img');
//   oLetter.src = oSrc;
//   oLetter.classList.add('letter', 'extra-o');
  
//   Object.assign(oLetter.style, {
//     opacity: '0',
//     transform: 'translateY(40px) scale(0.7)',
//     transition: 'all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)',
//     position: 'relative',
//     display: 'inline-block'
//   });
  
//   const lastLetter = heroLb.lastElementChild;
//   heroLb.insertBefore(oLetter, lastLetter);
//   oLetters.push(oLetter);
// }

// const allLetters = document.querySelectorAll('.hero-lb .letter');
// const lastLetter = heroLb.lastElementChild; // буква "т"

// allLetters.forEach(letter => {
//   if (letter !== lastLetter) {
//     letter.style.opacity = '0';
//     letter.style.transform = 'translateY(40px) scale(0.7)';
//     letter.style.transition = 'all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)';
//   }
// });

// lastLetter.style.transition = 'transform 1.2s cubic-bezier(0.68, -0.55, 0.27, 1.55)';
// lastLetter.style.transform = `translateX(${extraOs * shiftAmount}px)`;

// function animateLetters() {
//   const baseDelay = 200;
//   const staggerDelay = 150;
  
//   allLetters.forEach((letter, index) => {
//     if (letter === lastLetter) {
//       setTimeout(() => {
//         letter.style.opacity = '1';
//         letter.classList.add('pulse');
//       }, (allLetters.length - 1) * baseDelay + 300);
//       return;
//     }
    
//     setTimeout(() => {
//       letter.style.opacity = '1';
//       letter.style.transform = 'translateY(0) scale(1)';
//       letter.classList.add('pulse');
      
//       setTimeout(() => {
//         letter.style.transform = 'translateY(-8px) scale(1.1)';
//         setTimeout(() => {
//           letter.style.transform = 'translateY(0) scale(1)';
//         }, 150);
//       }, 400);
//     }, index * baseDelay);
//   });
// }

// // Запускаем анимацию
// setTimeout(animateLetters, 300);


// document.addEventListener('DOMContentLoaded', () => {
//     const track = document.getElementById('news-product');

//     let products = [];

//     fetch('assets/data/data.json')
//         .then(res => res.json())
//         .then(data => {
//             products = data
//                 .filter(item => item['Категория'] === 'Дессерт')
//                 .sort((a, b) => b.ID - a.ID);

//             renderProducts(products);
//         })
//         .catch(err => console.error('JSON error:', err));

//     function renderProducts(list) {
//         track.innerHTML = '';

//         list.forEach(item => {
//             const kbju = item['КБЖУ'];

//             const li = document.createElement('li');
//             li.className = 'product-card';

//             li.innerHTML = `
//                 <a href="assets/pages/product.html?id=${item.ID}" class="product-link">
//                     <div class="product-img">
//                         <img src="${item['Зображення']}" alt="${item['Назва']}">
//                     </div>

//                     <div class="product-info">
//                                     <div class="product-info">
//                                 <h3 class="product-title">${item['Назва']}</h3>
//                                 <p class="product-weight">${item["Вага"]}</p>
//                             </div>
//                             <div class="product-price">
//                                 ${item['Ціна']} <span class="product-price-uah">грн</span>

//                              <button class="add-to-cart" data-id="${item.ID}">
//                                 <img src="assets/img/+.svg" alt="add to cart">
//                             </button>    </div>

                       
//                     </div>
//                 </a>
//             `;

//             track.appendChild(li);
//         });
//     }
// });



// ---------------------------
// FAVORITES SECTION
// ---------------------------

// document.addEventListener('DOMContentLoaded', () => {
//     const favContainer = document.getElementById('favlist-products');

//     if (!favContainer) {
//         console.error('favlist-products not found');
//         return;
//     }

//     // Завантажуємо всі товари
//     fetch('assets/data/data.json')
//         .then(res => res.json())
//         .then(data => {
//             renderFavProducts(data); // відображаємо всі товари
//         })
//         .catch(err => console.error('JSON error:', err));

//     function renderFavProducts(list) {
//         favContainer.innerHTML = '';

//         list.forEach(item => {
//             const li = document.createElement('li');
//             li.className = 'product-card';

//             const productLink = `assets/pages/product.html?id=${item.ID}`;

//             li.innerHTML = `
//                 <a href="${productLink}" class="product-link">
//                     <div class="product-img">
//                         <img src="${item['Зображення']}" alt="${item['Назва']}" class="product-image">
//                     </div>

//                     <div class="product-info">
//                         <h3 class="product-title">${item['Назва']}</h3>
//                         <p class="product-weight">${item['Вага']}</p>

//                         <div class="product-cart">
//                             <div class="product-price">
//                                 ${item['Ціна']}
//                                 <span class="product-price-uah">грн</span>
//                             </div>

//                             <button class="add-to-cart" data-id="${item.ID}">
//                                 <img src="assets/img/+.svg" alt="add to cart">
//                             </button>
//                         </div>
//                     </div>
//                 </a>
//             `;

//             favContainer.appendChild(li);
//         });
//     }
// });



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
document.addEventListener('click', (e) => {
  document.querySelectorAll('.catalog-item.is-open').forEach(item => {
    if (!item.contains(e.target)) {
      item.classList.remove('is-open');
    }
  });
});
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');

let currentIndex = 0;

// переключение по точкам
dots.forEach(dot => {
    dot.addEventListener('click', () => {
        const index = +dot.dataset.slide;

        currentIndex = index; // важно — чтобы автопрокрутка "знала" текущий слайд

        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        slides[index].classList.add('active');
        dots[index].classList.add('active');
    });
});

// автопрокрутка
setInterval(() => {
    currentIndex = (currentIndex + 1) % slides.length;

    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));

    slides[currentIndex].classList.add('active');
    dots[currentIndex].classList.add('active');
}, 3000);



document.addEventListener('DOMContentLoaded', () => {
    const mobileSlider = document.querySelector('.slider-hero-m');

    if (!mobileSlider) return;

    const slidesM = mobileSlider.querySelectorAll('.slide');
    const dotsM = mobileSlider.querySelectorAll('.dot');

    dotsM.forEach(dot => {
        dot.addEventListener('click', () => {
            const index = dot.dataset.slide;

            slidesM.forEach(s => s.classList.remove('active'));
            dotsM.forEach(d => d.classList.remove('active'));

            slidesM[index].classList.add('active');
            dotsM[index].classList.add('active');
        });
    });

    // 🔥 вот сюда добавляем автопрокрутку
    let currentIndex = 0;

    setInterval(() => {
        currentIndex = (currentIndex + 1) % slidesM.length;

        slidesM.forEach(s => s.classList.remove('active'));
        dotsM.forEach(d => d.classList.remove('active'));

        slidesM[currentIndex].classList.add('active');
        dotsM[currentIndex].classList.add('active');
    }, 3000);
});


// // Находим все слайды в обоих слайдерах
// const desktopSlides = document.querySelectorAll('.slider-hero .slide img');
// const mobileSlides = document.querySelectorAll('.slider-hero-m .slide img');

// function preloadImages(slideImages) {
//   return Promise.all([...slideImages].map(img => {
//     return new Promise(resolve => {
//       if (img.complete) return resolve(); // если уже загружено
//       img.onload = resolve;               // ждем загрузку
//       img.onerror = resolve;              // на случай ошибки
//     });
//   }));
// }

// // Предзагрузка всех изображений
// Promise.all([
//   preloadImages(desktopSlides),
//   preloadImages(mobileSlides)
// ]).then(() => {
//   // Все изображения загружены — запускаем слайдер
//   startSlider();
// });

// // Функция слайдера (можно использовать твой существующий код)
// function startSlider() {
//   const sliders = [
//     { slides: document.querySelectorAll('.slider-hero .slide'), dots: document.querySelectorAll('.slider-hero .dot'), currentIndex: 0 },
//     { slides: document.querySelectorAll('.slider-hero-m .slide'), dots: document.querySelectorAll('.slider-hero-m .dot'), currentIndex: 0 }
//   ];

//   sliders.forEach(slider => {
//     // показ первого слайда
//     slider.slides[0].classList.add('active');
//     slider.dots[0].classList.add('active');

//     // переключение по точкам
//     slider.dots.forEach((dot, i) => {
//       dot.addEventListener('click', () => {
//         slider.slides.forEach(s => s.classList.remove('active'));
//         slider.dots.forEach(d => d.classList.remove('active'));
//         slider.slides[i].classList.add('active');
//         slider.dots[i].classList.add('active');
//         slider.currentIndex = i;
//       });
//     });

//     // автопрокрутка
//     setInterval(() => {
//       slider.currentIndex = (slider.currentIndex + 1) % slider.slides.length;
//       slider.slides.forEach(s => s.classList.remove('active'));
//       slider.dots.forEach(d => d.classList.remove('active'));
//       slider.slides[slider.currentIndex].classList.add('active');
//       slider.dots[slider.currentIndex].classList.add('active');
//     }, 3000);
//   });
// }



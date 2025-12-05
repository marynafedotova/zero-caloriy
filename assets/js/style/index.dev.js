"use strict";

document.addEventListener('DOMContentLoaded', function () {
  var container = document.getElementById('news-product');
  var btnShowAll = document.getElementById('show-all-btn');
  var allProducts = []; // сюди збережемо всі товари

  fetch('assets/data/data.json').then(function (response) {
    return response.json();
  }).then(function (products) {
    allProducts = products;
    renderProducts(products.slice(0, 4)); // показуємо перші 4

    btnShowAll.addEventListener('click', function () {
      container.innerHTML = ""; // очищаємо список

      renderProducts(allProducts); // показуємо всі товари

      btnShowAll.style.display = "none"; // приховуємо кнопку
    });
  })["catch"](function (error) {
    return console.error('Помилка завантаження файлу:', error);
  });

  function renderProducts(list) {
    list.forEach(function (item) {
      var li = document.createElement('li');
      li.className = 'product-card';
      li.innerHTML = "\n              <div class=\"product-img\">\n                  <img src=\"".concat(item['Зображення'], "\" alt=\"").concat(item['Назва'], "\" class=\"product-image\">\n              </div>\n                  \n              <div class=\"product-info\">\n                  <h3 class=\"product-title\">").concat(item['Назва'], "</h3>\n                  <p class=\"product-weight\">").concat(item['Вага/об\'єм (г/л)'], "</p>\n\n                  <div class=\"product-cart\">\n                      <div class=\"product-price\">\n                          ").concat(item['Ціна'], "\n                          <div class=\"product-price-uah\">\u0433\u0440\u043D</div>\n                      </div>\n\n                      <button class=\"add-to-cart\" data-id=\"").concat(item['ID'] || '', "\">\n                          <img src=\"assets/img/+.svg\" alt=\"add to cart\">\n                      </button>\n                  </div>\n              </div>\n            ");
      container.appendChild(li);
    }); // навішуємо обробники після рендера

    document.querySelectorAll('.add-to-cart').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = btn.getAttribute('data-id');
        console.log("Додано в корзину товар ID:", id);
      });
    });
  }
});
document.addEventListener('DOMContentLoaded', function () {
  var favContainer = document.getElementById('favlist-products');
  var favShowAllBtn = document.getElementById('favlist-show-all');
  var favProducts = []; // збережемо всі товари

  fetch('assets/data/data.json').then(function (response) {
    return response.json();
  }).then(function (products) {
    favProducts = products; // показуємо перші 4

    renderFavProducts(products.slice(0, 4));
    favShowAllBtn.addEventListener('click', function () {
      favContainer.innerHTML = "";
      renderFavProducts(favProducts);
      favShowAllBtn.style.display = "none";
    });
  });
});

function renderFavProducts(list) {
  var favContainer = document.getElementById('favlist-products');
  list.forEach(function (item) {
    var li = document.createElement('li');
    li.className = 'product-card';
    li.innerHTML = "\n        <div class=\"product-img\">\n            <img src=\"".concat(item['Зображення'], "\" alt=\"").concat(item['Назва'], "\" class=\"product-image\">\n        </div>\n\n        <div class=\"product-info\">\n            <h3 class=\"product-title\">").concat(item['Назва'], "</h3>\n            <p class=\"product-weight\">").concat(item["Вага/об'єм (г/л)"], "</p>\n\n            <div class=\"product-cart\">\n                <div class=\"product-price\">\n                    ").concat(item['Ціна'], "\n                    <div class=\"product-price-uah\">\u0433\u0440\u043D</div>\n                </div>\n\n                <button class=\"add-to-cart\" data-id=\"").concat(item['ID'] || '', "\">\n                    <img src=\"assets/img/+.svg\" alt=\"add to cart\">\n                </button>\n            </div>\n        </div>\n        ");
    favContainer.appendChild(li);
  }); // обробники додавання до кошика

  document.querySelectorAll('.add-to-cart').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-id');
      console.log("Додано в корзину товар ID:", id);
    });
  });
}
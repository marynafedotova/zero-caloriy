"use strict";

document.addEventListener('DOMContentLoaded', function () {
  var params = new URLSearchParams(window.location.search);
  var productId = parseInt(params.get('id'), 10);
  fetch('../data/data.json') // путь относительно product.html
  .then(function (res) {
    return res.json();
  }).then(function (products) {
    var product = products.find(function (p) {
      return p.ID === productId;
    });
    if (!product) return; // Элементы на странице

    var imgEl = document.querySelector('.product-image');
    var titleEl = document.querySelector('.product-title');
    var priceEl = document.querySelector('.product-price');
    var descEl = document.querySelector('.product-desc');
    var nutritionEl = document.querySelector('.nutrition-list'); // Подставляем данные

    imgEl.src = "/" + product['Зображення']; // путь корректируем

    imgEl.alt = product['Назва'];
    titleEl.textContent = product['Назва'];
    priceEl.textContent = product['Ціна'];
    descEl.textContent = product['Склад']; // КБЖУ

    nutritionEl.innerHTML = '';
    product['КБЖУ'].trim().split('\n').forEach(function (item) {
      if (item.trim()) {
        var li = document.createElement('li');
        li.textContent = item.trim();
        nutritionEl.appendChild(li);
      }
    });
  })["catch"](function (err) {
    return console.error(err);
  });
});
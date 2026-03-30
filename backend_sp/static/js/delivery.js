
function openStore(app) {
    // Получаем информацию об устройстве пользователя
    var userAgent = navigator.userAgent || navigator.vendor || window.opera;
    
    var links = {
        loko: {
            ios: 'https://apps.apple.com/ua/app/loko-%D0%B4%D0%BE%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B0-%D1%97%D0%B6%D1%96-%D1%96-%D0%BF%D1%80%D0%BE%D0%B4%D1%83%D0%BA%D1%82%D1%96%D0%B2/id6448402849?l=uk&ppid=6c4e0833-5541-4842-9f74-e410c9092908',
            android: 'https://play.google.com/store/apps/details?id=ua.com.loko.app',
            web: 'https://loko.delivery/'
        },
        bolt: {
            ios: 'https://apps.apple.com/ua/app/bolt-fast-affordable-rides/id675033630',
            android: 'https://play.google.com/store/apps/details?id=ee.mtakso.client',
            web: 'https://bolt.eu/'
        },
        glovo: {
            ios: 'https://apps.apple.com/ua/app/glovo-food-delivery-and-more/id951812684',
            android: 'https://play.google.com/store/apps/details?id=com.glovo',
            web: 'https://glovoapp.com/'
        }
    };

    var appLinks = links[app];
    if (!appLinks) return;

    if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
        window.location.href = appLinks.ios;
    } 
    else if (/android/i.test(userAgent)) {
        window.location.href = appLinks.android;
    } 
    else {
        window.location.href = appLinks.web; 
    }
}

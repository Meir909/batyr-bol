// Service Worker для BATYR BOL PWA
const CACHE_NAME = 'batyrbol-v1';
const urlsToCache = [
  '/',
  '/game',
  '/intro.html',
  '/igra.html',
  '/logo.png',
  '/game_integration.js',
  '/game_engine.js',
  '/features.js',
  '/achievements.js',
  '/voice_recognition.js',
  '/manifest.json'
];

// Установка Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .catch(err => console.log('Cache error:', err))
  );
});

// Активация
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Перехват запросов
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Возвращаем кэш или делаем запрос
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});

// Push уведомления
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'Жаңа миссия күтіп тұр!',
    icon: '/logo.png',
    badge: '/logo.png',
    vibrate: [100, 50, 100],
    data: {
      url: '/game'
    },
    actions: [
      { action: 'open', title: 'Ойнау' },
      { action: 'close', title: 'Жабу' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('BATYR BOL', options)
  );
});

// Клик по уведомлению
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    event.waitUntil(
      clients.openWindow('/game')
    );
  }
});

const CACHE_VERSION = 'v2';
const STATIC_CACHE = `terra-roxa-static-${CACHE_VERSION}`;
const PAGE_CACHE = `terra-roxa-pages-${CACHE_VERSION}`;
const API_CACHE = `terra-roxa-api-${CACHE_VERSION}`;
const FONT_CACHE = `terra-roxa-fonts-${CACHE_VERSION}`;
const OFFLINE_URL = '/offline';

const STATIC_URLS = [
  '/static/manifest.json',
  '/offline',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Nunito+Sans:wght@400;600;700&display=swap',
];

const API_PATTERNS = ['/api/', '/health'];

function isApiRequest(url) {
  return API_PATTERNS.some(p => url.includes(p));
}

function isStaticAsset(url) {
  return url.includes('/static/') ||
         url.includes('cdn.jsdelivr.net') ||
         url.includes('fonts.googleapis.com') ||
         url.includes('fonts.gstatic.com');
}

function isNavigation(url) {
  try {
    const u = new URL(url);
    return u.origin === self.location.origin && !isStaticAsset(url) && !isApiRequest(url);
  } catch { return false; }
}

self.addEventListener('install', event => {
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then(cache => cache.addAll(STATIC_URLS)),
      caches.open(FONT_CACHE).then(cache => {
        return cache.addAll([
          'https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Nunito+Sans:wght@400;600;700&display=swap',
          'https://fonts.gstatic.com/s/nunito/v26/XRXI3I6Li01BKofiOc5wtlZ2di8HDLshdTQ3j6zbXWjgeg.woff2',
          'https://fonts.gstatic.com/s/nunitosans/v15/pe0qMImSLYBIv1o4X1M8ccewI9tScg.woff2',
        ]).catch(() => {});
      }),
    ])
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== STATIC_CACHE && name !== PAGE_CACHE && name !== API_CACHE && name !== FONT_CACHE)
          .map(name => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  const url = request.url;

  if (request.method !== 'GET') {
    return;
  }

  if (isStaticAsset(url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  if (isApiRequest(url)) {
    event.respondWith(networkFirst(request, API_CACHE));
    return;
  }

  if (isNavigation(url)) {
    event.respondWith(networkFirst(request, PAGE_CACHE));
    return;
  }

  event.respondWith(networkFirst(request, PAGE_CACHE));
});

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (event.data && event.data.type === 'CLEAR_CACHES') {
    caches.keys().then(names => Promise.all(names.map(n => caches.delete(n))));
  }
});

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) return cached;
    if (request.mode === 'navigate') {
      const offlinePage = await caches.match(OFFLINE_URL);
      if (offlinePage) return offlinePage;
      return new Response('Você está offline. Conecte-se à internet para acessar.',
        { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } });
    }
    if (isApiRequest(request.url)) {
      return new Response(JSON.stringify({ offline: true, error: 'Sem conexão' }),
        { status: 503, headers: { 'Content-Type': 'application/json' } });
    }
    return new Response('Offline', { status: 503 });
  }
}

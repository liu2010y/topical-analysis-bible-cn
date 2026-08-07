// 自动生成，勿手改（build.py）
const CACHE = 'topical-cn-32deb2dd88';
const ASSETS = [
  "./index.html",
  "./manifest.json",
  "./assets/style.css",
  "./assets/app.js",
  "./assets/grammar-registry.js",
  "./assets/dict/dict-a.js",
  "./assets/dict/dict-b.js",
  "./assets/dict/dict-c.js",
  "./assets/dict/dict-d.js",
  "./assets/dict/dict-e.js",
  "./assets/dict/dict-f.js",
  "./assets/dict/dict-g.js",
  "./assets/dict/dict-h.js",
  "./assets/dict/dict-i.js",
  "./assets/dict/dict-j.js",
  "./assets/dict/dict-k.js",
  "./assets/dict/dict-l.js",
  "./assets/dict/dict-m.js",
  "./assets/dict/dict-n.js",
  "./assets/dict/dict-o.js",
  "./assets/dict/dict-p.js",
  "./assets/dict/dict-q.js",
  "./assets/dict/dict-r.js",
  "./assets/dict/dict-s.js",
  "./assets/dict/dict-t.js",
  "./assets/dict/dict-u.js",
  "./assets/dict/dict-v.js",
  "./assets/dict/dict-w.js",
  "./assets/dict/dict-x.js",
  "./assets/dict/dict-y.js",
  "./assets/dict/dict-z.js",
  "./assets/icons/apple-touch-icon.png",
  "./assets/icons/icon-192.png",
  "./assets/icons/icon-512.png",
  "./001-Accountability-%E5%90%91%E7%A5%9E%E4%BA%A4%E8%B4%A6%E7%9A%84%E8%B4%A3%E4%BB%BB.html",
  "./002-Adoption-%E5%BE%97%E5%84%BF%E5%AD%90%E7%9A%84%E5%90%8D%E5%88%86.html",
  "./003-Affliction-%E8%8B%A6%E9%9A%BE.html",
  "./004-Agency-%E7%A5%9E%E4%BA%BA%E5%8D%8F%E4%BD%9C.html",
  "./005-Altar-%E7%A5%AD%E5%9D%9B.html",
  "./006-Angels-%E5%A4%A9%E4%BD%BF.html",
  "./007-Anger-%E4%BA%BA%E7%9A%84%E6%80%92%E6%B0%94.html",
  "./008-Anthropopathy-%E7%A5%9E%E6%A0%BC%E6%8B%9F%E4%BA%BA.html",
  "./009-Anxiety-%E5%BF%A7%E8%99%91.html",
  "./010-Apostleship-%E4%BD%BF%E5%BE%92%E8%81%8C%E5%88%86.html",
  "./011-Archeology-%E8%80%83%E5%8F%A4%E5%AD%A6.html",
  "./012-Atheism-%E6%97%A0%E7%A5%9E%E8%AE%BA.html",
  "./013-Atonement-%E8%B5%8E%E7%BD%AA.html",
  "./014-Backsliders-%E8%83%8C%E9%81%93.html",
  "./015-Beatitudes-%E5%85%AB%E7%A6%8F.html",
  "./016-Beauty-%E8%8D%A3%E7%BE%8E.html",
  "./017-Benedictions-%E7%A5%9D%E7%A6%8F.html",
  "./018-Bible-%E5%9C%A3%E7%BB%8F.html",
  "./019-Bible-Lands-%E5%9C%A3%E7%BB%8F%E5%9C%B0%E7%90%86.html",
  "./020-Bishop-%E7%9B%91%E7%9D%A3.html",
  "./021-Blasphemy-%E4%BA%B5%E6%B8%8E.html",
  "./022-Blessings-Curses-%E7%A5%9D%E7%A6%8F%E4%B8%8E%E5%92%92%E8%AF%85.html",
  "./023-Books-%E4%B9%A6%E7%B1%8D%E4%B8%8E%E9%98%85%E8%AF%BB.html",
  "./024-Call-of-God-%E7%A5%9E%E7%9A%84%E5%91%BC%E5%8F%AC.html",
  "./025-Calling-%E5%A4%A9%E8%81%8C.html",
  "./026-Captivity-%E8%A2%AB%E6%8E%B3.html",
  "./027-Character-%E5%93%81%E6%A0%BC.html",
  "./028-OT-Characters-%E6%97%A7%E7%BA%A6%E4%BA%BA%E7%89%A9.html",
  "./029-Cherubim-%E5%9F%BA%E8%B7%AF%E4%BC%AF.html",
  "./030-Childlikeness-%E8%B5%A4%E5%AD%90%E4%B9%8B%E5%BF%83.html",
  "./031-Choices-%E6%8A%89%E6%8B%A9.html",
  "./032-Christ-on-Earth-%E5%9F%BA%E7%9D%A3%E5%9C%A8%E4%B8%96.html",
  "./033-Christ-Believer-%E5%9F%BA%E7%9D%A3%E4%B8%8E%E4%BF%A1%E5%BE%92.html",
  "./034-Christian-Life-%E5%9F%BA%E7%9D%A3%E5%BE%92%E7%94%9F%E6%B4%BB.html"
];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request, {ignoreSearch: true}).then(hit => hit || fetch(e.request).then(resp => {
      if (resp.ok && new URL(e.request.url).origin === location.origin) {
        const copy = resp.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return resp;
    }))
  );
});

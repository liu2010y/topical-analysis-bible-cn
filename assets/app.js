/* 《圣经主题分析》中译工程 —— 页面交互
 * 1. 小节 EN 按钮 / 全局 EN 按钮：控制英文原文显示
 * 1b. 现代英译（BSB）开关（默认开）
 * 2. 语法说明全局开关（默认隐藏）
 * 3. 查词：悬停 1.5 秒（或点击）——先查本页精编词典，查不到再查 ECDICT 兜底词典；
 *    划选任意单词/短语 → 弹窗查询（支持短语条目）＋朗读＋网页查词外链
 * 4. 语法引用 chip 点击就地展开完整讲解（数据来自 grammar-registry.js）
 */
(function () {
  'use strict';

  /* ---------- 1. 英文显示开关 ---------- */
  var btnEn = document.getElementById('btn-en');
  var sections = Array.prototype.slice.call(document.querySelectorAll('.section'));

  function updateGlobalEnButton() {
    if (!btnEn) return;
    var anyVisible = sections.some(function (s) { return !s.classList.contains('en-hidden'); });
    btnEn.textContent = anyVisible ? '隐藏全部英文' : '显示全部英文';
    btnEn.classList.toggle('active', !anyVisible);
  }

  sections.forEach(function (sec) {
    var t = sec.querySelector('.en-toggle');
    if (!t) return;
    t.addEventListener('click', function () {
      var hidden = sec.classList.toggle('en-hidden');
      t.textContent = hidden ? '显示EN' : '隐藏EN';
      t.classList.toggle('active', hidden);
      updateGlobalEnButton();
    });
  });

  if (btnEn) {
    btnEn.addEventListener('click', function () {
      var anyVisible = sections.some(function (s) { return !s.classList.contains('en-hidden'); });
      sections.forEach(function (sec) {
        sec.classList.toggle('en-hidden', anyVisible);
        var t = sec.querySelector('.en-toggle');
        if (t) {
          t.textContent = anyVisible ? '显示EN' : '隐藏EN';
          t.classList.toggle('active', anyVisible);
        }
      });
      updateGlobalEnButton();
    });
    updateGlobalEnButton();
  }

  /* ---------- 1b. 现代英译（BSB）开关（默认开） ---------- */
  var btnBsb = document.getElementById('btn-bsb');
  if (btnBsb) {
    btnBsb.addEventListener('click', function () {
      var hidden = document.body.classList.toggle('hide-bsb');
      btnBsb.textContent = hidden ? '现代英译：关' : '现代英译：开';
      btnBsb.classList.toggle('active', !hidden);
    });
  }

  /* ---------- 2. 语法说明开关（默认关） ---------- */
  var btnGrammar = document.getElementById('btn-grammar');
  if (btnGrammar) {
    btnGrammar.addEventListener('click', function () {
      var on = document.body.classList.toggle('show-grammar');
      btnGrammar.textContent = on ? '语法说明：开' : '语法说明：关';
      btnGrammar.classList.toggle('active', on);
    });
  }

  /* ---------- 浏览器 TTS 朗读 ---------- */
  var ttsVoice = null;
  function pickVoice() {
    if (!window.speechSynthesis) return;
    var vs = window.speechSynthesis.getVoices();
    ttsVoice = vs.find(function (v) { return v.lang === 'en-GB'; }) ||
               vs.find(function (v) { return v.lang.indexOf('en') === 0; }) || null;
  }
  if (window.speechSynthesis) {
    pickVoice();
    window.speechSynthesis.onvoiceschanged = pickVoice;
  }

  function speak(text) {
    if (!window.speechSynthesis || !text) return;
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-GB'; // 音标为英式，读音保持一致
    if (ttsVoice) u.voice = ttsVoice;
    u.rate = 0.85;
    window.speechSynthesis.speak(u);
  }

  /* ---------- 3a. 词典数据 ---------- */
  // 本页精编词典（内嵌 JSON）
  var vocab = {};
  var vocabEl = document.getElementById('vocab-data');
  if (vocabEl) {
    try { vocab = JSON.parse(vocabEl.textContent); } catch (e) { vocab = {}; }
  }

  // ECDICT 兜底词典：26 个分片按需加载（<script> 方式，file:// 下也可用）
  var ecdict = {};
  var shardState = {};
  var shardWaiters = {};
  window.ECDICT_LOAD = function (key, data) {
    for (var k in data) ecdict[k] = data[k];
    shardState[key] = 'ready';
    (shardWaiters[key] || []).forEach(function (cb) { cb(); });
    shardWaiters[key] = [];
  };
  function shardOf(word) {
    var c = word.charAt(0);
    return (c >= 'a' && c <= 'z') ? c : 'misc';
  }
  function ensureShard(letter, cb) {
    if (shardState[letter] === 'ready') return cb();
    (shardWaiters[letter] = shardWaiters[letter] || []).push(cb);
    if (shardState[letter] === 'loading') return;
    shardState[letter] = 'loading';
    var s = document.createElement('script');
    s.src = 'assets/dict/dict-' + letter + '.js';
    s.onerror = function () { window.ECDICT_LOAD(letter, {}); };
    document.head.appendChild(s);
  }
  // 查 ECDICT：处理别名（变形→原型，可能跨分片）与所有格 's
  function ecdictLookup(key, cb, depth) {
    depth = depth || 0;
    if (!key || depth > 3) return cb(null);
    ensureShard(shardOf(key), function () {
      var v = ecdict[key];
      if (typeof v === 'string') return ecdictLookup(v, cb, depth + 1);
      if (v) {
        return cb({
          ipa: v[0] ? '/' + v[0] + '/' : '',
          def: (v[2] ? '【' + v[2] + '】' : '') + v[1],
          generic: true
        });
      }
      if (/'s$/.test(key)) return ecdictLookup(key.replace(/'s$/, ''), cb, depth + 1);
      cb(null);
    });
  }
  function normKey(text) {
    return text.toLowerCase().replace(/[’‘]/g, "'")
      .replace(/[^a-z'\- ]/g, ' ').replace(/\s+/g, ' ').trim();
  }

  /* ---------- 3b. 弹窗渲染 ---------- */
  var tip = document.createElement('div');
  tip.id = 'dict-tip';
  document.body.appendChild(tip);

  var hoverTimer = null;
  var hideTimer = null;
  var tipToken = 0;           // 防止过期的异步查询覆盖弹窗
  var HOVER_DELAY = 1500;     // 1.5 秒

  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function scheduleHide() {
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(hideTip, 350);
  }
  function cancelHide() {
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  }
  tip.addEventListener('mouseenter', cancelHide);
  tip.addEventListener('mouseleave', scheduleHide);

  function hideTip() {
    tip.style.display = 'none';
    tipToken++;
    if (hoverTimer) { clearTimeout(hoverTimer); hoverTimer = null; }
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  }

  function positionTip(rect) {
    tip.style.display = 'block';
    var tw = tip.offsetWidth, th = tip.offsetHeight;
    var x = rect.left + rect.width / 2 - tw / 2;
    x = Math.max(8, Math.min(x, window.innerWidth - tw - 8));
    var y = rect.top - th - 8;
    if (y < 8) y = rect.bottom + 8;
    tip.style.left = x + 'px';
    tip.style.top = y + 'px';
  }

  function renderTip(rect, word, entry) {
    cancelHide();
    var h = '<span class="tip-word">' + escapeHtml(word) + '</span>' +
      '<button class="tip-speak" data-word="' + escapeHtml(word) + '" title="朗读">🔊</button>';
    if (entry) {
      if (entry.ipa) h += '<span class="tip-ipa">' + escapeHtml(entry.ipa) + '</span>';
      if (entry.generic) h += '<span class="tip-src">通用词典</span>';
      h += '<div class="tip-def">' + escapeHtml(entry.def) + '</div>';
    } else {
      h += '<div class="tip-def">本地词典未收录</div>';
    }
    if (!entry || entry.generic) {
      h += '<a class="tip-link" href="https://dict.youdao.com/result?word=' +
        encodeURIComponent(word) + '&lang=en" target="_blank" rel="noopener">网页查词 →</a>';
    }
    tip.innerHTML = h;
    positionTip(rect);
  }

  function lookupAndShow(word, rect) {
    var key = normKey(word);
    var page = vocab[key];
    if (page) return renderTip(rect, word, {ipa: page.ipa, def: page.def});
    var token = ++tipToken;
    ecdictLookup(key, function (entry) {
      if (token !== tipToken) return; // 弹窗已被关闭/替换
      renderTip(rect, word, entry);
    });
  }

  /* ---------- 3c. 悬停 / 点击 / 划选 ---------- */
  function showTipForSpan(span) {
    lookupAndShow(span.textContent, span.getBoundingClientRect());
  }

  document.addEventListener('mouseover', function (ev) {
    var span = ev.target.closest ? ev.target.closest('.w, .w2') : null;
    if (!span) return;
    if (hoverTimer) clearTimeout(hoverTimer);
    hoverTimer = setTimeout(function () { showTipForSpan(span); }, HOVER_DELAY);
  });

  document.addEventListener('mouseout', function (ev) {
    var span = ev.target.closest ? ev.target.closest('.w, .w2') : null;
    if (!span) return;
    if (hoverTimer) { clearTimeout(hoverTimer); hoverTimer = null; }
    if (tip.style.display === 'block') scheduleHide(); // 留出移入弹窗点 🔊 的时间
  });

  // 划选单词/短语 → 查询（支持 according to 这类短语条目）
  document.addEventListener('mouseup', function () {
    setTimeout(function () {
      var sel = window.getSelection();
      var text = sel ? sel.toString().trim() : '';
      if (!text || text.length > 60 || !/[A-Za-z]/.test(text)) return;
      if (text.split(/\s+/).length > 5 || !sel.rangeCount) return;
      var rect = sel.getRangeAt(0).getBoundingClientRect();
      if (!rect || (rect.width === 0 && rect.height === 0)) return;
      lookupAndShow(text, rect);
    }, 10);
  });

  // 点击立即弹出（触摸板 / 手机友好）；点击 🔊 朗读
  document.addEventListener('click', function (ev) {
    var speakBtn = ev.target.closest ? ev.target.closest('.tip-speak, .speak') : null;
    if (speakBtn) {
      speak(speakBtn.getAttribute('data-word'));
      ev.stopPropagation();
      return;
    }
    if (ev.target.closest && ev.target.closest('#dict-tip')) return; // 弹窗内点击（如外链）
    var hasSelection = window.getSelection && window.getSelection().toString().trim();
    if (hasSelection) return; // 划选查询由 mouseup 处理
    var span = ev.target.closest ? ev.target.closest('.w, .w2') : null;
    if (span) {
      if (hoverTimer) clearTimeout(hoverTimer);
      if (tip.style.display === 'block') { hideTip(); } else { showTipForSpan(span); }
      ev.stopPropagation();
    } else if (tip.style.display === 'block') {
      hideTip();
    }
  });

  window.addEventListener('scroll', hideTip, { passive: true });

  /* ---------- 3d. 本页侧边导航：抽屉开关 + 滚动高亮 ---------- */
  var sideToc = document.getElementById('side-toc');
  var btnToc = document.getElementById('btn-toc');
  if (btnToc && sideToc) {
    btnToc.addEventListener('click', function (ev) {
      document.body.classList.toggle('toc-open');
      ev.stopPropagation();
    });
    sideToc.addEventListener('click', function (ev) {
      if (ev.target.closest('a')) document.body.classList.remove('toc-open');
    });
    document.addEventListener('click', function (ev) {
      if (document.body.classList.contains('toc-open') &&
          !ev.target.closest('#side-toc') && !ev.target.closest('#btn-toc')) {
        document.body.classList.remove('toc-open');
      }
    });
  }
  if (sideToc && 'IntersectionObserver' in window) {
    var tocLinks = {};
    sideToc.querySelectorAll('a[href^="#"]').forEach(function (a) {
      tocLinks[a.getAttribute('href').slice(1)] = a;
    });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        Object.keys(tocLinks).forEach(function (k) { tocLinks[k].classList.remove('active'); });
        var link = tocLinks[en.target.id];
        if (link) {
          link.classList.add('active');
          if (link.scrollIntoView) link.scrollIntoView({ block: 'nearest' });
        }
      });
    }, { rootMargin: '-12% 0px -78% 0px' });
    document.querySelectorAll('main .section[id]').forEach(function (s) { spy.observe(s); });
  }

  /* ---------- 4. 语法引用 chip 展开 ---------- */
  var registry = (typeof window.GRAMMAR_REGISTRY === 'object' && window.GRAMMAR_REGISTRY) || {};

  document.querySelectorAll('.gchip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      var item = chip.closest('.gitem');
      if (!item) return;
      var expand = item.querySelector('.gexpand');
      if (!expand) {
        expand = document.createElement('div');
        expand.className = 'gexpand';
        var gid = chip.getAttribute('data-gid');
        var g = registry[gid];
        expand.innerHTML = g
          ? '<span class="gtitle">' + escapeHtml(g.title) + '</span>（首见于词条 ' + escapeHtml(g.first) + '）<br>' + escapeHtml(g.body)
          : '（未在语法登记表中找到该条目）';
        item.appendChild(expand);
      }
      item.classList.toggle('expanded');
    });
  });
})();

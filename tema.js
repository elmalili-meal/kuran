// Koyu tema düğmesi: sağ üstteki düğme arka planı orijinal maviden koyuya
// çevirir; seçim tarayıcıda hatırlanır. Varsayılan görünüm orijinal mavidir.
// <head> içinde yüklenir, böylece koyu seçilmişse sayfa mavi yanıp sönmeden açılır.
(function () {
  var KEY = "tema";
  var root = document.documentElement;

  var style = document.createElement("style");
  style.textContent =
    "html.koyu body, html.koyu [bgcolor] { background-color: #121212 !important; }" +
    "html.koyu table, html.koyu td, html.koyu tr { border-color: #555 !important; }" +
    "#tema-dugme { position: fixed; top: 8px; right: 8px; z-index: 1000;" +
    " width: 36px; height: 36px; padding: 0; border: 1px solid #CCCCCC;" +
    " border-radius: 50%; background: rgba(0,0,0,0.25); color: #FFFFFF;" +
    " font-size: 18px; line-height: 34px; text-align: center; cursor: pointer; }" +
    "#tema-dugme:hover { color: red; }";
  document.head.appendChild(style);

  function oku() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function yaz(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
  }

  if (oku() === "koyu") root.classList.add("koyu");

  function dugmeKur() {
    var b = document.createElement("button");
    b.id = "tema-dugme";
    b.type = "button";
    function guncelle() {
      var koyu = root.classList.contains("koyu");
      b.textContent = koyu ? "☀" : "☾";  // ☀ / ☾
      b.title = koyu ? "Mavi arka plan" : "Koyu arka plan";
      b.setAttribute("aria-label", b.title);
    }
    b.addEventListener("click", function () {
      var koyu = root.classList.toggle("koyu");
      yaz(koyu ? "koyu" : "mavi");
      guncelle();
    });
    guncelle();
    document.body.appendChild(b);
  }

  if (document.body) dugmeKur();
  else document.addEventListener("DOMContentLoaded", dugmeKur);
})();

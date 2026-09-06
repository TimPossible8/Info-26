<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Fundgrube  Secondhand-App mit KI-Tags</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/fontsource/css/poppins@latest/latin-400-normal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/fontsource/css/poppins@latest/latin-500-normal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/fontsource/css/poppins@latest/latin-600-normal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/fontsource/css/poppins@latest/latin-700-normal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/fontsource/css/poppins@latest/latin-800-normal.css">
<style>
:root{
  --bg:#F8F5FE; --screen:#fef7ff; --primary:#6750a4; --primary-dark:#4f3d85;
  --secondary:#d0c3f1; --badge:#D4C4F7; --surface:#ece6f0; --ink:#100f0d;
  --text:#4A4A4A; --muted:#8a7fb0; --white:#ffffff; --danger:#e5484d;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0}
body{
  font-family:'Poppins',system-ui,sans-serif; background:var(--bg); color:var(--ink);
  min-height:100vh; display:flex; align-items:center; justify-content:center;
  background-image:linear-gradient(160deg,#efe9fb 0%,#F8F5FE 45%,#e9e0f8 100%);
  overflow:hidden;
}
body::before,body::after{content:"";position:fixed;border-radius:50%;filter:blur(90px);opacity:.55;z-index:0;pointer-events:none}
body::before{width:420px;height:420px;background:#d0c3f1;top:-120px;left:-120px;animation:blob 14s ease-in-out infinite alternate}
body::after{width:380px;height:380px;background:#f3d3ec;bottom:-140px;right:-120px;animation:blob 17s ease-in-out infinite alternate-reverse}
@keyframes blob{to{transform:translate(40px,30px) scale(1.12)}}

/* ---------- Phone Frame ---------- */
.phone{
  position:relative;z-index:1;width:392px;height:min(830px,96vh);
  background:var(--ink);border-radius:56px;padding:11px;
  box-shadow:0 40px 90px rgba(48,32,90,.35),0 8px 24px rgba(48,32,90,.22),inset 0 0 0 2px #2b2724;
}
.screen{position:relative;width:100%;height:100%;background:var(--screen);border-radius:46px;overflow:hidden;display:flex;flex-direction:column}
.notch{position:absolute;top:11px;left:50%;transform:translateX(-50%);width:116px;height:26px;background:var(--ink);border-radius:16px;z-index:55}
.statusbar{display:flex;justify-content:space-between;align-items:center;padding:15px 28px 4px;font-size:13px;font-weight:700;color:var(--ink);flex:0 0 auto}
.sb-icons{display:flex;gap:6px;align-items:center;color:var(--ink)}
.sb-icons svg{height:12px;width:auto;display:block}
.view{flex:1;overflow-y:auto;overflow-x:hidden;padding:6px 20px 18px;scrollbar-width:none}
.view::-webkit-scrollbar{width:0}
.view.anim>.page{animation:pageIn .38s cubic-bezier(.22,.8,.28,1)}
@keyframes pageIn{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}

/* ---------- Navigation ---------- */
.nav{flex:0 0 auto;display:flex;align-items:center;justify-content:space-around;padding:8px 14px 16px;background:rgba(255,255,255,.94);backdrop-filter:blur(14px);border-top:1px solid var(--surface);z-index:40}
.nbtn{position:relative;display:flex;flex-direction:column;align-items:center;gap:3px;border:none;background:none;color:#9a8fc0;font-size:10px;font-weight:700;cursor:pointer;padding:6px 12px;font-family:inherit;transition:color .2s}
.nbtn svg{width:22px;height:22px}
.nbtn.on{color:var(--primary)}
.nbtn .count{position:absolute;top:0;right:4px;background:var(--primary);color:#fff;font-size:9px;font-weight:800;min-width:16px;height:16px;border-radius:99px;display:grid;place-items:center;padding:0 4px}
.fab{width:56px;height:56px;border-radius:50%;background:linear-gradient(145deg,#7a63c0,var(--primary));color:#fff;border:none;display:grid;place-items:center;box-shadow:0 12px 26px rgba(103,80,164,.45);transform:translateY(-16px);cursor:pointer;transition:transform .2s,box-shadow .2s}
.fab svg{width:24px;height:24px}
.fab:hover{transform:translateY(-19px) scale(1.05);box-shadow:0 16px 32px rgba(103,80,164,.55)}
.fab:active{transform:translateY(-14px) scale(.96)}

/* ---------- Generische UI ---------- */
.head{display:flex;align-items:center;gap:12px;margin:8px 0 14px}
.head h2{font-size:20px;font-weight:800;margin:0;letter-spacing:-.3px}
.ibtn{width:40px;height:40px;border-radius:50%;background:#fff;display:grid;place-items:center;color:var(--primary);box-shadow:0 4px 14px rgba(16,15,13,.10);border:none;cursor:pointer;flex:0 0 auto;transition:transform .15s}
.ibtn:active{transform:scale(.92)}
.ibtn svg{width:20px;height:20px}
.btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;border:none;border-radius:999px;padding:16px;font-weight:700;font-size:15px;cursor:pointer;transition:transform .15s,box-shadow .2s,background .2s;font-family:inherit}
.btn svg{width:19px;height:19px}
.btn:active{transform:scale(.97)}
.btn[disabled]{opacity:.45;pointer-events:none}
.btn-primary{background:var(--primary);color:#fff;box-shadow:0 10px 24px rgba(103,80,164,.35)}
.btn-primary:hover{background:var(--primary-dark)}
.btn-secondary{background:var(--secondary);color:var(--primary)}
.btn-secondary:hover{background:#c3b2ec}
.btn-ghost{background:var(--surface);color:var(--text)}
.btn-sm{padding:11px 14px;font-size:13px}
.btn-sm svg{width:16px;height:16px}
.badge{display:inline-flex;align-items:center;gap:6px;background:var(--badge);color:var(--primary);padding:7px 16px;border-radius:999px;font-size:12px;font-weight:800;letter-spacing:.2px}
.badge svg{width:14px;height:14px}
.app-title{text-align:center;font-size:32px;font-weight:800;letter-spacing:-.8px;margin:12px 0 12px;color:var(--ink)}
.app-title span{color:var(--primary)}
.chips{display:flex;gap:8px;overflow-x:auto;padding:2px 2px 8px;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;background:var(--badge);color:var(--primary);font-weight:700;font-size:12px;padding:9px 15px;border-radius:999px;border:none;cursor:pointer;font-family:inherit;transition:all .2s}
.chip.on{background:var(--primary);color:#fff;box-shadow:0 6px 14px rgba(103,80,164,.3)}
.section-label{display:flex;align-items:center;gap:6px;font-size:11px;font-weight:800;color:var(--primary);text-transform:uppercase;letter-spacing:.6px;margin:16px 2px 8px}
.section-label svg{width:14px;height:14px}
.field{width:100%;border:2px solid var(--surface);background:#fff;border-radius:16px;padding:12px 14px;font:inherit;font-size:14px;color:var(--ink);outline:none;transition:border-color .2s}
.field:focus{border-color:var(--primary)}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.empty{text-align:center;padding:46px 20px;color:var(--muted);font-size:13.5px;font-weight:600}
.empty .emo{font-size:46px;display:block;margin-bottom:12px}

/* ---------- Home / Carousel ---------- */
.carousel{position:relative;border-radius:26px;overflow:hidden;box-shadow:0 14px 34px rgba(103,80,164,.18);margin:14px 0 4px;background:var(--surface)}
.track{display:flex;transition:transform .5s cubic-bezier(.22,.8,.28,1)}
.slide{flex:0 0 100%;position:relative;aspect-ratio:1/1}
.slide img{width:100%;height:100%;object-fit:cover;display:block}
.slide .cap{position:absolute;left:0;right:0;bottom:0;padding:16px;background:linear-gradient(transparent,rgba(16,15,13,.62));color:#fff;display:flex;justify-content:space-between;align-items:flex-end;gap:10px}
.cap b{font-size:15px;font-weight:700;text-shadow:0 1px 6px rgba(0,0,0,.4)}
.cap .price{background:rgba(255,255,255,.94);color:var(--primary);padding:6px 12px;border-radius:999px;font-weight:800;font-size:12px;flex:0 0 auto}
.car-btn{position:absolute;top:50%;transform:translateY(-50%);width:34px;height:34px;border-radius:50%;border:none;background:rgba(255,255,255,.88);color:var(--primary);display:grid;place-items:center;cursor:pointer;backdrop-filter:blur(4px);z-index:5;transition:transform .15s}
.car-btn:active{transform:translateY(-50%) scale(.9)}
.car-btn svg{width:18px;height:18px}
.car-btn.l{left:10px}.car-btn.r{right:10px}
.dots{display:flex;gap:6px;justify-content:center;margin:12px 0 6px}
.dot{width:7px;height:7px;border-radius:99px;background:var(--secondary);border:none;padding:0;cursor:pointer;transition:all .3s}
.dot.on{width:22px;background:var(--primary)}
.home-actions{display:flex;flex-direction:column;gap:12px;margin-top:10px}

/* ---------- Suche ---------- */
.searchbar{position:relative;margin:2px 0 12px}
.searchbar svg{position:absolute;left:15px;top:50%;transform:translateY(-50%);color:#9a8fc0;width:18px;height:18px;pointer-events:none}
.searchbar input{width:100%;border:2px solid var(--surface);background:#fff;border-radius:999px;padding:14px 16px 14px 44px;font:inherit;font-size:14px;color:var(--ink);outline:none;transition:border-color .2s,box-shadow .2s}
.searchbar input:focus{border-color:var(--primary);box-shadow:0 0 0 4px rgba(103,80,164,.12)}
.count-line{font-size:12px;color:var(--muted);margin:0 2px 10px;font-weight:600}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.card{background:#fff;border-radius:20px;padding:8px;box-shadow:0 6px 18px rgba(103,80,164,.10);display:flex;flex-direction:column;gap:7px;animation:pageIn .4s both}
.card .thumb{position:relative;border-radius:15px;overflow:hidden;aspect-ratio:1;cursor:pointer}
.thumb img{width:100%;height:100%;object-fit:cover;transition:transform .45s}
.card:hover .thumb img{transform:scale(1.07)}
.fav-btn{position:absolute;top:8px;right:8px;width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.92);border:none;display:grid;place-items:center;color:var(--primary);cursor:pointer;transition:transform .15s}
.fav-btn svg{width:16px;height:16px}
.fav-btn:active{transform:scale(.85)}
.fav-btn.on{color:var(--danger)}
.fav-btn.on svg path{fill:currentColor}
.card h4{font-size:13.5px;font-weight:700;margin:0 3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card .tagsline{font-size:10.5px;color:var(--muted);margin:0 3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:600}

/* ---------- Detail ---------- */
.detail-img{position:relative;border-radius:26px;overflow:hidden;aspect-ratio:1;box-shadow:0 14px 34px rgba(103,80,164,.18)}
.detail-img img{width:100%;height:100%;object-fit:cover}
.detail-img .fav-btn{width:42px;height:42px;top:12px;right:12px}
.detail-img .fav-btn svg{width:20px;height:20px}
.detail-name{font-size:22px;font-weight:800;letter-spacing:-.4px;margin:16px 2px 4px}
.seller{display:flex;align-items:center;gap:10px;margin:10px 2px 4px}
.avatar{width:38px;height:38px;border-radius:50%;background:var(--secondary);color:var(--primary);display:grid;place-items:center;font-weight:800;font-size:13px}
.seller b{font-size:13px;display:block}
.seller small{font-size:11px;color:var(--muted);font-weight:600}
.pill{background:var(--badge);color:var(--primary);font-size:10.5px;font-weight:800;padding:5px 11px;border-radius:999px;margin-left:auto}
.meta{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:14px 0 6px}
.meta div{background:#fff;border-radius:14px;padding:10px 6px;text-align:center;box-shadow:0 4px 12px rgba(103,80,164,.08)}
.meta small{display:block;color:var(--muted);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;margin-bottom:2px}
.meta b{font-size:13.5px;color:var(--ink)}
.tagwrap{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 18px}
.detail-actions{display:flex;flex-direction:column;gap:12px;margin-top:6px}
.btn-secondary.on{background:var(--primary);color:#fff;box-shadow:0 10px 24px rgba(103,80,164,.35)}

/* ---------- Upload ---------- */
.dropzone{border:2px dashed var(--secondary);border-radius:24px;padding:30px 20px;text-align:center;cursor:pointer;background:rgba(255,255,255,.6);transition:all .2s;color:var(--muted)}
.dropzone:hover,.dropzone.drag{background:#fff;border-color:var(--primary);transform:scale(1.01)}
.dropzone .cam{width:58px;height:58px;border-radius:50%;background:var(--secondary);color:var(--primary);display:grid;place-items:center;margin:0 auto 12px}
.dropzone .cam svg{width:26px;height:26px}
.dropzone b{display:block;color:var(--ink);font-size:15px;margin-bottom:4px}
.dropzone small{font-size:11.5px;font-weight:600}
.up-preview{position:relative;border-radius:24px;overflow:hidden;aspect-ratio:1;background:var(--surface);margin-top:14px;box-shadow:0 10px 26px rgba(103,80,164,.16)}
.up-preview img{width:100%;height:100%;object-fit:cover}
.scanbox{position:absolute;inset:0;background:rgba(254,247,255,.78);backdrop-filter:blur(6px);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;z-index:5}
.ring{width:62px;height:62px;border-radius:50%;border:5px solid var(--secondary);border-top-color:var(--primary);animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.scanbox p{margin:0;font-size:13px;font-weight:700;color:var(--primary)}
.progress{width:68%;height:8px;background:var(--surface);border-radius:99px;overflow:hidden}
.progress i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--primary),#9b7fe0);border-radius:99px;transition:width .5s ease}
.result-card{background:#fff;border-radius:22px;padding:16px;box-shadow:0 8px 22px rgba(103,80,164,.12);margin-top:14px;display:flex;flex-direction:column;gap:12px;animation:pageIn .4s}
.result-card h3{margin:0;font-size:16px;font-weight:800;display:flex;align-items:center;gap:8px}
.result-card h3 svg{width:17px;height:17px;color:var(--primary)}
.tag-editor{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.tag-chip{display:inline-flex;align-items:center;gap:7px;background:var(--badge);color:var(--primary);font-weight:700;font-size:12px;padding:8px 12px;border-radius:999px}
.tag-chip button{border:none;background:none;color:inherit;cursor:pointer;display:grid;place-items:center;padding:0}
.tag-chip button svg{width:12px;height:12px}
.tag-add{display:flex;gap:8px;margin-top:2px}
.tag-add .field{padding:9px 12px;font-size:13px;border-radius:999px}
.tag-add .ibtn{width:38px;height:38px}
.hintline{font-size:11.5px;color:var(--muted);font-weight:600;text-align:center;margin:10px 0 0}

/* ---------- Listen ---------- */
.row{display:flex;align-items:center;gap:12px;background:#fff;border-radius:18px;padding:10px;box-shadow:0 6px 16px rgba(103,80,164,.10);margin-bottom:10px;animation:pageIn .35s both}
.row img{width:56px;height:56px;border-radius:14px;object-fit:cover;flex:0 0 auto}
.row .info{flex:1;min-width:0}
.row h4{margin:0 0 2px;font-size:14px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row p{margin:0;font-size:11px;color:var(--muted);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* ---------- Overlay / Toast / FX ---------- */
.overlay{position:absolute;inset:0;background:rgba(16,15,13,.45);backdrop-filter:blur(3px);display:flex;align-items:center;justify-content:center;padding:26px;z-index:60;animation:fade .25s}
.overlay[hidden]{display:none}
@keyframes fade{from{opacity:0}}
.modal{background:var(--screen);border-radius:26px;padding:22px;width:100%;max-width:330px;animation:pop .32s cubic-bezier(.22,.8,.28,1);display:flex;flex-direction:column;gap:12px}
@keyframes pop{from{opacity:0;transform:scale(.9) translateY(14px)}}
.modal h3{margin:0;font-size:18px;font-weight:800}
.modal .sub{margin:-6px 0 2px;font-size:12.5px;color:var(--muted);font-weight:600}
.modal textarea.field{resize:none;min-height:84px}
.toasts{position:absolute;left:0;right:0;bottom:100px;display:flex;flex-direction:column;align-items:center;gap:8px;z-index:70;pointer-events:none;padding:0 24px}
.toast{background:var(--ink);color:#fff;padding:11px 18px;border-radius:999px;font-size:13px;font-weight:600;box-shadow:0 10px 24px rgba(0,0,0,.28);animation:toastIn .3s cubic-bezier(.22,.8,.28,1);transition:opacity .3s,transform .3s;text-align:center}
.toast.out{opacity:0;transform:translateY(10px)}
@keyframes toastIn{from{opacity:0;transform:translateY(14px) scale(.94)}}
.fx{position:absolute;inset:0;pointer-events:none;z-index:80;overflow:hidden}
.balloon{position:absolute;bottom:-50px;animation:rise linear forwards}
@keyframes rise{to{transform:translateY(-115vh) rotate(24deg)}}

.desk-hint{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);z-index:1;background:rgba(255,255,255,.8);backdrop-filter:blur(8px);color:var(--primary);font-size:12px;font-weight:700;padding:9px 18px;border-radius:999px;box-shadow:0 6px 18px rgba(103,80,164,.16);white-space:nowrap}

@media (max-width:520px){
  body{overflow:auto}
  .phone{width:100vw;height:100dvh;border-radius:0;padding:0;box-shadow:none}
  .screen{border-radius:0}
  .notch{display:none}
  .statusbar{padding-top:10px}
  .desk-hint{display:none}
  body::before,body::after{display:none}
}
@media (min-width:521px) and (max-height:880px){
  .phone{height:94vh}
}
</style>
</head>
<body>
<div class="phone">
  <div class="screen" id="screen">
    <div class="notch"></div>
    <div class="statusbar">
      <span id="clock">9:41</span>
      <span class="sb-icons">
        <svg viewBox="0 0 18 12" fill="currentColor"><rect x="0" y="8" width="3" height="4" rx="1"/><rect x="5" y="5" width="3" height="7" rx="1"/><rect x="10" y="2" width="3" height="10" rx="1"/><rect x="15" y="0" width="3" height="12" rx="1" opacity=".4"/></svg>
        <svg viewBox="0 0 16 12" fill="currentColor"><path d="M8 9.6 1.6 3.4A9 9 0 0 1 8 1a9 9 0 0 1 6.4 2.4L8 9.6Z" opacity=".9"/><path d="M3.4 5.2 8 9.6l4.6-4.4A6.4 6.4 0 0 0 8 3.4a6.4 6.4 0 0 0-4.6 1.8Z"/></svg>
        <svg viewBox="0 0 25 12" fill="none"><rect x=".5" y=".5" width="21" height="11" rx="3" stroke="currentColor" opacity=".45"/><rect x="2" y="2" width="15" height="8" rx="1.6" fill="currentColor"/><path d="M23 4v4a2.2 2.2 0 0 0 0-4Z" fill="currentColor" opacity=".45"/></svg>
      </span>
    </div>
    <main class="view" id="view"></main>
    <nav class="nav" id="nav"></nav>
    <div class="toasts" id="toasts"></div>
    <div class="fx" id="fx"></div>
    <div class="overlay" id="overlay" hidden></div>
  </div>
</div>
<div class="desk-hint">💜 Fundgrube · Secondhand-App mit KI-Tags · Design aus den SVG-Mockups umgesetzt</div>

<script>
/* ============ Icons ============ */
const IC = {
  home:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/></svg>',
  search:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.5-4.5"/></svg>',
  plus:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  heart:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M20.8 8.6a5 5 0 0 0-8.8-3.2A5 5 0 0 0 3.2 8.6c0 5 8.8 10 8.8 10s8.8-5 8.8-10z"/></svg>',
  book:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 3h12v18l-6-4.5L6 21z"/></svg>',
  back:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>',
  spark:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.5l1.9 5.6 5.6 1.9-5.6 1.9L12 17.5l-1.9-5.6-5.6-1.9 5.6-1.9z"/><path d="M19 15l.9 2.6 2.6.9-2.6.9L19 22l-.9-2.6-2.6-.9 2.6-.9z"/></svg>',
  mail:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m3 7.5 9 6 9-6"/></svg>',
  x:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
  check:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg>',
  cam:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M4 8h3l2-3h6l2 3h3v12H4z"/><circle cx="12" cy="13.5" r="3.5"/></svg>',
  chevL:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>',
  chevR:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>',
  up:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>',
  save:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M5 3h11l5 5v13H5z"/><path d="M8 3v6h8V3M8 21v-7h8v7"/></svg>'
};
const PLACEHOLDER = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><rect width='100%' height='100%' fill='%23ece6f0'/><text x='50%' y='54%' font-size='70' text-anchor='middle'>👕</text></svg>";
function fgImgFail(img){ img.onerror=null; img.src=PLACEHOLDER; }
window.fgImgFail = fgImgFail;

/* ============ Daten ============ */
const IMG_BASE = 'https://image.qwenlm.ai/public_source/eb1442b2-84be-470b-9d4e-407314fab36b/';
const BASE_ITEMS = [
  {id:1,name:'Beiger Strickpullover',tags:['pullover','beige','strick','winter'],img:IMG_BASE+'18c7b7da9-dcaf-4659-971d-490b7382fa3e.png',price:'29 €',size:'M',zustand:'Sehr gut'},
  {id:2,name:'Roter Rentier-Pulli',tags:['pullover','rot','weihnachten','rentier'],img:IMG_BASE+'1b54d1bb7-8344-44de-86df-7d4666c1e3b4.png',price:'24 €',size:'L',zustand:'Gut'},
  {id:3,name:'Blaue Vintage Jeansjacke',tags:['jacke','denim','blau','vintage'],img:IMG_BASE+'1bf69780a-888e-439f-a6b7-ce0747e67213.png',price:'39 €',size:'M',zustand:'Gut'},
  {id:4,name:'Weiße Canvas-Sneaker',tags:['schuhe','sneaker','weiß','sommer'],img:IMG_BASE+'1acccf06d-4f43-4274-bbdd-b3f693bddd50.png',price:'35 €',size:'42',zustand:'Sehr gut'},
  {id:5,name:'Pasteller Blumenrock',tags:['rock','floral','pastell','sommer'],img:IMG_BASE+'15411b335-e140-453d-8865-be4dec7a6049.png',price:'19 €',size:'S',zustand:'Wie neu'},
  {id:6,name:'Schwarze Ledertasche',tags:['tasche','leder','schwarz','elegant'],img:IMG_BASE+'1b68ac464-4bd4-431e-aa70-cdfdd2.png',price:'45 €',size:'One Size',zustand:'Sehr gut'},
  {id:7,name:'Grüne Cordhose',tags:['hose','cord','grün','herbst'],img:IMG_BASE+'198c5d37d-48ec-480c-b629-2457e83e50a5.png',price:'27 €',size:'38',zustand:'Gut'},
  {id:8,name:'Grauer Wollschal',tags:['schal','wolle','grau','winter'],img:IMG_BASE+'166345dda-9f84-4f6f-bf92-47094ab1bd74.png',price:'12 €',size:'One Size',zustand:'Wie neu'}
];

/* ============ State ============ */
function fgLoad(key,def){ try{ const v=JSON.parse(localStorage.getItem(key)); return v==null?def:v; }catch(e){ return def; } }
function fgSave(key,val){ try{ localStorage.setItem(key,JSON.stringify(val)); }catch(e){} }
const FG = {
  page:'home', idx:0, sel:null, query:'', tag:null,
  reserved: fgLoad('fg_res',[]), favs: fgLoad('fg_fav',[]), userItems: fgLoad('fg_user',[]),
  pendingFile:null, pending:null, pendingTags:[], scanBusy:false, carTimer:null
};
const elView = document.getElementById('view');
const elNav  = document.getElementById('nav');
const elToasts = document.getElementById('toasts');
const elFx = document.getElementById('fx');
const elOverlay = document.getElementById('overlay');

function db(){ return BASE_ITEMS.concat(FG.userItems); }
function findItem(id){ return db().find(it=>String(it.id)===String(id)); }
function esc(s){ return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }

/* ============ Toast / FX ============ */
function toast(msg){
  const t=document.createElement('div'); t.className='toast'; t.textContent=msg;
  elToasts.appendChild(t);
  setTimeout(()=>{ t.classList.add('out'); setTimeout(()=>t.remove(),320); },2500);
}
function confetti(){
  const emos=['🎈','✨','💜','','💫'];
  for(let i=0;i<18;i++){
    const b=document.createElement('span'); b.className='balloon';
    b.textContent=emos[Math.floor(Math.random()*emos.length)];
    b.style.left=(5+Math.random()*90)+'%';
    b.style.fontSize=(18+Math.random()*20)+'px';
    b.style.animationDuration=(2+Math.random()*1.6)+'s';
    b.style.animationDelay=(Math.random()*0.5)+'s';
    elFx.appendChild(b);
    setTimeout(()=>b.remove(),4200);
  }
}

/* ============ Rendering ============ */
function topTags(){
  const count={};
  db().forEach(it=>it.tags.forEach(t=>{count[t]=(count[t]||0)+1;}));
  return Object.keys(count).sort((a,b)=>count[b]-count[a]).slice(0,8);
}
function carouselList(){ return db().slice().reverse(); }

const PAGES = {
  home(){
    const list=carouselList();
    if(FG.idx>=list.length) FG.idx=0;
    const slides=list.map(it=>`
      <div class="slide">
        <img src="${it.img}" alt="${esc(it.name)}" onerror="fgImgFail(this)">
        <div class="cap"><b>${esc(it.name)}</b><span class="price">${esc(it.price||'VB')}</span></div>
      </div>`).join('');
    const dots=list.map((_,i)=>`<button class="dot ${i===FG.idx?'on':''}" data-action="dot" data-i="${i}" aria-label="Slide ${i+1}"></button>`).join('');
    const chips=topTags().slice(0,6).map(t=>`<button class="chip" data-action="chip" data-tag="${esc(t)}">#${esc(t)}</button>`).join('');
    return `<div class="page">
      <h1 class="app-title">Fund<span>grube</span></h1>
      <div style="text-align:center"><span class="badge">${IC.spark} Zuletzt Hinzugefügt</span></div>
      <div class="carousel" id="carousel">
        <div class="track" id="carTrack" style="transform:translateX(-${FG.idx*100}%)">${slides}</div>
        <button class="car-btn l" data-action="car-prev" aria-label="Zurück">${IC.chevL}</button>
        <button class="car-btn r" data-action="car-next" aria-label="Weiter">${IC.chevR}</button>
      </div>
      <div class="dots" id="carDots">${dots}</div>
      <div class="home-actions">
        <button class="btn btn-secondary" data-action="nav" data-page="search">${IC.search} Artikel Suchen</button>
        <button class="btn btn-primary" data-action="nav" data-page="upload">${IC.up} Artikel Hochladen</button>
      </div>
      <div class="section-label">${IC.spark} Beliebte Tags</div>
      <div class="chips">${chips}</div>
    </div>`;
  },
  search(){
    const chips=['alle'].concat(topTags()).map(t=>
      t==='alle'
        ? `<button class="chip ${!FG.tag?'on':''}" data-action="clear-tag">Alle</button>`
        : `<button class="chip ${FG.tag===t?'on':''}" data-action="chip" data-tag="${esc(t)}">#${esc(t)}</button>`
    ).join('');
    return `<div class="page">
      <div class="head"><button class="ibtn" data-action="nav" data-page="home">${IC.back}</button><h2>Artikel Suchen</h2></div>
      <div class="searchbar">${IC.search}<input id="searchInput" type="text" placeholder="Suchen nach Name oder Tag …" value="${esc(FG.query)}" autocomplete="off"></div>
      <div class="chips">${chips}</div>
      <p class="count-line" id="searchCount"></p>
      <div class="grid" id="searchGrid"></div>
    </div>`;
  },
  detail(){
    const it=findItem(FG.sel);
    if(!it) return PAGES.search();
    const isFav=FG.favs.includes(it.id), isRes=FG.reserved.includes(it.id);
    const tags=it.tags.map(t=>`<button class="chip" data-action="chip" data-tag="${esc(t)}">#${esc(t)}</button>`).join('');
    return `<div class="page">
      <div class="head"><button class="ibtn" data-action="nav" data-page="search">${IC.back}</button><h2>Details</h2></div>
      <div class="detail-img">
        <img src="${it.img}" alt="${esc(it.name)}" onerror="fgImgFail(this)">
        <button class="fav-btn ${isFav?'on':''}" data-action="fav" data-id="${it.id}" aria-label="Merken">${IC.heart}</button>
      </div>
      <h2 class="detail-name">${esc(it.name)}</h2>
      <div class="seller"><span class="avatar">FG</span><span><b>Fundgrube Community</b><small>Privater Verkauf · ${it.user?'neu eingestellt':'aktiv seit 2024'}</small></span><span class="pill">✓ Verifiziert</span></div>
      <div class="meta">
        <div><small>Zustand</small><b>${esc(it.zustand||'Gut')}</b></div>
        <div><small>Größe</small><b>${esc(it.size||'–')}</b></div>
        <div><small>Preis</small><b>${esc(it.price||'VB')}</b></div>
      </div>
      <div class="section-label">${IC.spark} KI-Tags</div>
      <div class="tagwrap">${tags}</div>
      <div class="detail-actions">
        <button class="btn btn-secondary ${isRes?'on':''}" data-action="reserve" data-id="${it.id}">${isRes?IC.check+' Reserviert ✓':IC.book+' Reservieren'}</button>
        <button class="btn btn-primary" data-action="contact" data-id="${it.id}">${IC.mail} Kontaktieren</button>
      </div>
    </div>`;
  },
  upload(){
    const p=FG.pending;
    const preview = p ? `
      <div class="up-preview"><img src="${p.url}" alt="Vorschau"></div>` : `
      <div class="up-preview" id="upPreview" hidden><img id="upImg" alt="Vorschau">
        <div class="scanbox" id="scanBox" hidden>
          <div class="ring"></div><p id="scanStatus">Bild wird vorbereitet …</p>
          <div class="progress"><i id="scanBar"></i></div>
        </div>
      </div>`;
    const result = p ? `
      <div class="result-card">
        <h3>${IC.spark} KI-Scan abgeschlossen</h3>
        <label class="field" style="display:flex;align-items:center;gap:8px;background:var(--surface);border:none;border-radius:12px;padding:10px 12px;font-size:12px;font-weight:700;color:var(--primary)">
          ${IC.check} Farben, Kategorie & Merkmale automatisch erkannt
        </label>
        <input class="field" id="upName" placeholder="Name des Artikels" value="${esc(p.name)}">
        <div class="section-label" style="margin:2px 0 0">Erkannte Tags</div>
        <div class="tag-editor" id="tagEditor">
          ${FG.pendingTags.map((t,i)=>`<span class="tag-chip">#${esc(t)}<button data-action="tag-remove" data-i="${i}" aria-label="Tag entfernen">${IC.x}</button></span>`).join('')}
        </div>
        <div class="tag-add">
          <input class="field" id="tagInput" placeholder="Tag hinzufügen …" autocomplete="off">
          <button class="ibtn" id="tagAddBtn" aria-label="Tag hinzufügen">${IC.plus}</button>
        </div>
        <div class="row2">
          <input class="field" id="upPrice" placeholder="Preis (z. B. 19 €)">
          <input class="field" id="upSize" placeholder="Größe (z. B. M)">
        </div>
        <button class="btn btn-primary" data-action="save-item">${IC.save} In Fundgrube speichern</button>
        <button class="btn btn-ghost btn-sm" data-action="reset-scan">Neuen Scan starten</button>
      </div>` : `
      <div class="dropzone" id="dz">
        <span class="cam">${IC.cam}</span>
        <b>Bild auswählen</b>
        <small>oder Foto hierher ziehen · JPG · PNG · WebP</small>
      </div>
      <input type="file" id="fileInput" accept="image/*" hidden>
      ${preview}
      <div style="margin-top:14px">
        <button class="btn btn-primary" id="scanBtn" data-action="scan" disabled>${IC.spark} Hochladen &amp; KI-Scan</button>
      </div>
      <p class="hintline">Der KI-Scan läuft komplett lokal in deinem Browser – Farbanalyse, Kategorie-Erkennung &amp; Tag-Vorschläge in Echtzeit.</p>`;
    return `<div class="page">
      <div class="head"><button class="ibtn" data-action="nav" data-page="home">${IC.back}</button><h2>Neuer Artikel</h2></div>
      ${p?preview+result:`<div id="uploadFlow">${result}</div>`}
    </div>`;
  },
  reserved(){
    const rows=FG.reserved.map(id=>findItem(id)).filter(Boolean);
    const body=rows.length? rows.map(it=>`
      <div class="row">
        <img src="${it.img}" alt="${esc(it.name)}" onerror="fgImgFail(this)">
        <div class="info"><h4>${esc(it.name)}</h4><p>#${it.tags.join(' #')}</p></div>
        <span class="pill">Reserviert</span>
        <button class="ibtn" data-action="release" data-id="${it.id}" aria-label="Freigeben">${IC.x}</button>
      </div>`).join('')
      : `<div class="empty"><span class="emo">🔖</span>Noch keine Reservierungen.<br>Stöbere in der Fundgrube!</div>`;
    return `<div class="page">
      <div class="head"><button class="ibtn" data-action="nav" data-page="home">${IC.back}</button><h2>Reservierungen</h2></div>
      ${body}
    </div>`;
  },
  favs(){
    const rows=FG.favs.map(id=>findItem(id)).filter(Boolean);
    const body=rows.length? rows.map(it=>`
      <div class="row">
        <img src="${it.img}" alt="${esc(it.name)}" onerror="fgImgFail(this)">
        <div class="info"><h4>${esc(it.name)}</h4><p>${esc(it.price||'VB')} · #${it.tags.slice(0,3).join(' #')}</p></div>
        <button class="ibtn" data-action="view" data-id="${it.id}" aria-label="Öffnen">${IC.chevR}</button>
        <button class="ibtn" style="color:var(--danger)" data-action="fav" data-id="${it.id}" aria-label="Entfernen">${IC.x}</button>
      </div>`).join('')
      : `<div class="empty"><span class="emo">💜</span>Deine Merkliste ist leer.<br>Tippe auf das Herz eines Artikels!</div>`;
    return `<div class="page">
      <div class="head"><button class="ibtn" data-action="nav" data-page="home">${IC.back}</button><h2>Merkliste</h2></div>
      ${body}
    </div>`;
  }
};

function renderNav(){
  const active = FG.page==='detail' ? 'search' : FG.page;
  const navBtn=(page,icon,label,count)=>`
    <button class="nbtn ${active===page?'on':''}" data-action="nav" data-page="${page}">
      ${icon}<span>${label}</span>${count?`<span class="count">${count}</span>`:''}
    </button>`;
  elNav.innerHTML =
    navBtn('home',IC.home,'Home') +
    navBtn('search',IC.search,'Suche') +
    `<button class="fab" data-action="nav" data-page="upload" aria-label="Hochladen">${IC.plus}</button>` +
    navBtn('favs',IC.heart,'Merkliste',FG.favs.length) +
    navBtn('reserved',IC.book,'Reserv.',FG.reserved.length);
}
function render(){
  clearInterval(FG.carTimer);
  elView.innerHTML = PAGES[FG.page]();
  elView.classList.remove('anim'); void elView.offsetWidth; elView.classList.add('anim');
  elView.scrollTop = 0;
  renderNav();
  bindPage();
}
function rerenderKeepScroll(){
  const s=elView.scrollTop; render(); elView.scrollTop=s;
}

/* ============ Carousel ============ */
function goCarousel(i){
  const list=carouselList(), n=list.length; if(!n) return;
  FG.idx=((i%n)+n)%n;
  const track=document.getElementById('carTrack');
  if(track) track.style.transform=`translateX(-${FG.idx*100}%)`;
  document.querySelectorAll('#carDots .dot').forEach((d,k)=>d.classList.toggle('on',k===FG.idx));
}
function bindCarousel(){
  const car=document.getElementById('carousel'); if(!car) return;
  let startX=null;
  car.addEventListener('touchstart',e=>{startX=e.touches[0].clientX;},{passive:true});
  car.addEventListener('touchend',e=>{
    if(startX==null) return;
    const dx=e.changedTouches[0].clientX-startX;
    if(Math.abs(dx)>40) goCarousel(FG.idx+(dx<0?1:-1));
    startX=null;
  },{passive:true});
  FG.carTimer=setInterval(()=>{ if(FG.page==='home') goCarousel(FG.idx+1); },4500);
}

/* ============ Suche ============ */
function searchResults(){
  const q=FG.query.toLowerCase().trim();
  return db().filter(it=>{
    const okQ=!q || it.name.toLowerCase().includes(q) || it.tags.some(t=>t.toLowerCase().includes(q));
    const okT=!FG.tag || it.tags.includes(FG.tag);
    return okQ&&okT;
  });
}
function renderSearchGrid(){
  const grid=document.getElementById('searchGrid'), cnt=document.getElementById('searchCount');
  if(!grid) return;
  const res=searchResults();
  if(cnt) cnt.textContent = res.length===0 ? '' : `${res.length} Artikel gefunden`;
  grid.innerHTML = res.length ? res.map((it,i)=>`
    <div class="card" style="animation-delay:${Math.min(i*45,320)}ms">
      <div class="thumb" data-action="view" data-id="${it.id}">
        <img src="${it.img}" alt="${esc(it.name)}" loading="lazy" onerror="fgImgFail(this)">
        <button class="fav-btn ${FG.favs.includes(it.id)?'on':''}" data-action="fav" data-id="${it.id}" aria-label="Merken">${IC.heart}</button>
      </div>
      <h4>${esc(it.name)}</h4>
      <p class="tagsline">#${it.tags.join(' #')}</p>
      <button class="btn btn-secondary btn-sm" data-action="view" data-id="${it.id}">Ansehen</button>
    </div>`).join('')
    : `<div class="empty" style="grid-column:1/-1"><span class="emo">🔍</span>Keine Treffer für deine Suche.<br>Versuche einen anderen Begriff oder Tag!</div>`;
}

/* ============ Upload / KI-Scan ============ */
function fileToDataUrl(file){ return new Promise((res,rej)=>{ const r=new FileReader(); r.onload=()=>res(r.result); r.onerror=rej; r.readAsDataURL(file); }); }
function loadImgEl(src){ return new Promise((res,rej)=>{ const im=new Image(); im.onload=()=>res(im); im.onerror=rej; im.src=src; }); }
function rgbToHsl(r,g,b){
  r/=255;g/=255;b/=255;
  const mx=Math.max(r,g,b), mn=Math.min(r,g,b); let h=0,s=0; const l=(mx+mn)/2;
  if(mx!==mn){
    const d=mx-mn;
    s=l>0.5? d/(2-mx-mn) : d/(mx+mn);
    if(mx===r) h=((g-b)/d+(g<b?6:0));
    else if(mx===g) h=(b-r)/d+2;
    else h=(r-g)/d+4;
    h*=60;
  }
  return [h,s,l];
}
function colorFromHsl(h,s,l){
  if(l<0.16) return 'schwarz';
  if(l>0.9 && s<0.3) return 'weiß';
  if(s<0.14) return l<0.5?'schwarz':'grau';
  if(h>=20&&h<=50&&s<0.5&&l>0.55&&l<0.88) return 'beige';
  if(h<15||h>=345) return 'rot';
  if(h<40) return l<0.45?'braun':'orange';
  if(h<70) return 'gelb';
  if(h<165) return 'grün';
  if(h<200) return 'türkis';
  if(h<255) return 'blau';
  if(h<290) return 'lila';
  return 'rosa';
}
const CATS=[
  ['pullover',['pullover','pulli','sweater','strick','hoodie']],
  ['jacke',['jacke','jacket','blazer','mantel','coat']],
  ['hose',['hose','jeans','pants','chino']],
  ['schuhe',['schuh','sneaker','stiefel','boots','heels']],
  ['tasche',['tasche','bag','rucksack']],
  ['kleid',['kleid','dress']],
  ['rock',['rock','skirt']],
  ['schal',['schal','scarf','mütze','beanie']],
  ['hemd',['hemd','shirt','bluse','top','tee']]
];
const CAT_NOUN={pullover:'Pullover',jacke:'Jacke',hose:'Hose',schuhe:'Sneaker',tasche:'Tasche',kleid:'Kleid',rock:'Rock',schal:'Schal',hemd:'Shirt'};
const COLOR_ADJ={rot:'Roter',orange:'Orangener',gelb:'Gelber',grün:'Grüner',türkis:'Türkiser',blau:'Blauer',lila:'Lila',rosa:'Rosa',braun:'Brauner',beige:'Beiger',grau:'Grauer',schwarz:'Schwarzer',weiß:'Weißer'};
function categoryFromName(fname){
  const n=fname.toLowerCase();
  for(const [key,words] of CATS){ if(words.some(w=>n.includes(w))) return key; }
  return null;
}
async function processImage(file){
  const raw=await fileToDataUrl(file);
  const im=await loadImgEl(raw);
  const c=document.createElement('canvas'); const S=48; c.width=S; c.height=S;
  const cx=c.getContext('2d',{willReadFrequently:true});
  cx.drawImage(im,0,0,S,S);
  const d=cx.getImageData(0,0,S,S).data;
  let r=0,g=0,b=0,n=0;
  for(let p=0;p<d.length;p+=4){ if(d[p+3]<10) continue; r+=d[p]; g+=d[p+1]; b+=d[p+2]; n++; }
  if(n){ r/=n; g/=n; b/=n; }
  const [h,s,l]=rgbToHsl(r,g,b);
  const color=colorFromHsl(h,s,l);
  const max=640, k=Math.min(1,max/Math.max(im.width,im.height));
  const c2=document.createElement('canvas');
  c2.width=Math.max(1,Math.round(im.width*k)); c2.height=Math.max(1,Math.round(im.height*k));
  c2.getContext('2d').drawImage(im,0,0,c2.width,c2.height);
  let url; try{ url=c2.toDataURL('image/jpeg',0.86); }catch(e){ url=raw; }
  return {url,color};
}
async function runScan(){
  if(FG.scanBusy) return;
  if(!FG.pendingFile){ toast('Bitte zuerst ein Bild wählen 📸'); return; }
  FG.scanBusy=true;
  const box=document.getElementById('scanBox'), status=document.getElementById('scanStatus'), bar=document.getElementById('scanBar');
  if(box) box.hidden=false;
  const steps=[['Bild wird vorbereitet …',22,500],['Farben & Merkmale analysiert …',52,800],['KI-Taggt das Bild …',84,700],['Fertig! ✨',100,350]];
  try{
    for(const [txt,pct,ms] of steps){
      if(status) status.textContent=txt;
      if(bar) bar.style.width=pct+'%';
      await sleep(ms);
    }
    const {url,color}=await processImage(FG.pendingFile);
    const cat=categoryFromName(FG.pendingFile.name||'');
    const tags=[...new Set([color, cat||'mode', 'secondhand'])];
    const noun=cat?CAT_NOUN[cat]:'Teil';
    FG.pending={url, name:`${COLOR_ADJ[color]||'Schönes'} ${noun}`};
    FG.pendingTags=tags;
    FG.pendingFile=null;
    render();
    toast('KI-Scan abgeschlossen ✨ Tags geprüft & gespeichert?');
  }catch(err){
    toast('Fehler bei der KI-Analyse: '+err.message);
    if(box) box.hidden=true;
  }
  FG.scanBusy=false;
}
function saveItem(){
  if(!FG.pending) return;
  const nameEl=document.getElementById('upName');
  const name=(nameEl&&nameEl.value.trim())||FG.pending.name;
  if(FG.pendingTags.length===0){ toast('Mindestens ein Tag benötigt 🏷️'); return; }
  const priceEl=document.getElementById('upPrice'), sizeEl=document.getElementById('upSize');
  const item={
    id:Date.now(), name, tags:FG.pendingTags.slice(), img:FG.pending.url,
    price:(priceEl&&priceEl.value.trim())||'VB',
    size:(sizeEl&&sizeEl.value.trim())||'One Size',
    zustand:'Sehr gut', user:true
  };
  FG.userItems.push(item);
  fgSave('fg_user',FG.userItems);
  FG.pending=null; FG.pendingTags=[];
  confetti();
  toast('Artikel eingestellt! 🎉');
  FG.sel=item.id; FG.page='detail'; FG.idx=0;
  render();
}

/* ============ Overlay / Kontakt ============ */
function openContact(id){
  const it=findItem(id); if(!it) return;
  elOverlay.innerHTML=`
    <div class="modal">
      <h3>✉️ Kontaktieren</h3>
      <p class="sub">Nachricht an Verkäufer:in wegen <b>${esc(it.name)}</b></p>
      <input class="field" id="cName" placeholder="Dein Name">
      <input class="field" id="cMail" type="email" placeholder="Deine E-Mail">
      <textarea class="field" id="cMsg" placeholder="Hallo! Ich interessiere mich für den Artikel …"></textarea>
      <button class="btn btn-primary btn-sm" id="cSend">${IC.mail} Senden</button>
      <button class="btn btn-ghost btn-sm" data-action="close-modal">Abbrechen</button>
    </div>`;
  elOverlay.hidden=false;
  document.getElementById('cSend').addEventListener('click',()=>{
    const nm=document.getElementById('cName').value.trim();
    const ml=document.getElementById('cMail').value.trim();
    const ms=document.getElementById('cMsg').value.trim();
    if(nm.length<2){ toast('Bitte Namen angeben 🙂'); return; }
    if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(ml)){ toast('Ungültige E-Mail-Adresse 📮'); return; }
    if(ms.length<4){ toast('Bitte kurze Nachricht schreiben ✍️'); return; }
    closeOverlay();
    toast('Nachricht gesendet! ✉️ Antwort kommt per E-Mail.');
  });
}
function closeOverlay(){ elOverlay.hidden=true; elOverlay.innerHTML=''; }
elOverlay.addEventListener('click',e=>{ if(e.target===elOverlay) closeOverlay(); });

/* ============ Bindings ============ */
function bindPage(){
  if(FG.page==='home') bindCarousel();
  if(FG.page==='search'){
    const inp=document.getElementById('searchInput');
    if(inp) inp.addEventListener('input',e=>{ FG.query=e.target.value; renderSearchGrid(); });
    renderSearchGrid();
  }
  if(FG.page==='upload' && !FG.pending){
    const dz=document.getElementById('dz'), fi=document.getElementById('fileInput');
    if(dz&&fi){
      dz.addEventListener('click',()=>fi.click());
      ['dragover','dragenter'].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.add('drag');}));
      ['dragleave','drop'].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.remove('drag');}));
      dz.addEventListener('drop',e=>{ if(e.dataTransfer.files&&e.dataTransfer.files[0]) pickFile(e.dataTransfer.files[0]); });
      fi.addEventListener('change',()=>{ if(fi.files[0]) pickFile(fi.files[0]); });
    }
  }
  if(FG.page==='upload' && FG.pending){
    const addTag=()=>{
      const inp=document.getElementById('tagInput');
      const v=inp.value.trim().toLowerCase().replace(/^#/,'').replace(/\s+/g,'-');
      if(!v){ return; }
      if(!FG.pendingTags.includes(v)) FG.pendingTags.push(v);
      inp.value='';
      const ed=document.getElementById('tagEditor');
      if(ed) ed.innerHTML=FG.pendingTags.map((t,i)=>`<span class="tag-chip">#${esc(t)}<button data-action="tag-remove" data-i="${i}" aria-label="Tag entfernen">${IC.x}</button></span>`).join('');
    };
    const btn=document.getElementById('tagAddBtn'), inp=document.getElementById('tagInput');
    if(btn) btn.addEventListener('click',addTag);
    if(inp) inp.addEventListener('keydown',e=>{ if(e.key==='Enter'){ e.preventDefault(); addTag(); } });
  }
}
function pickFile(file){
  if(!file.type.startsWith('image/')){ toast('Bitte eine Bilddatei wählen 🖼️'); return; }
  FG.pendingFile=file;
  const prev=document.getElementById('upPreview'), img=document.getElementById('upImg'), btn=document.getElementById('scanBtn');
  if(prev&&img){
    img.src=URL.createObjectURL(file);
    prev.hidden=false;
  }
  if(btn) btn.disabled=false;
  toast('Bild geladen – KI-Scan kann starten 🚀');
}

/* ============ Globale Delegation ============ */
document.addEventListener('click',e=>{
  const t=e.target.closest('[data-action]'); if(!t) return;
  const a=t.dataset.action, id=t.dataset.id;
  switch(a){
    case 'nav': FG.page=t.dataset.page; render(); break;
    case 'view': FG.sel=id; FG.page='detail'; render(); break;
    case 'fav': {
      const num=Number(id);
      if(FG.favs.includes(num)) FG.favs=FG.favs.filter(x=>x!==num);
      else { FG.favs.push(num); toast('Zur Merkliste hinzugefügt 💜'); }
      fgSave('fg_fav',FG.favs); renderNav(); rerenderKeepScroll(); break;
    }
    case 'reserve': {
      const num=Number(id);
      if(FG.reserved.includes(num)){ FG.reserved=FG.reserved.filter(x=>x!==num); toast('Reservierung aufgehoben'); }
      else { FG.reserved.push(num); toast('Artikel reserviert! 🔖'); }
      fgSave('fg_res',FG.reserved); renderNav(); rerenderKeepScroll(); break;
    }
    case 'release': {
      const num=Number(id);
      FG.reserved=FG.reserved.filter(x=>x!==num);
      fgSave('fg_res',FG.reserved); renderNav(); rerenderKeepScroll(); toast('Freigegeben ✅'); break;
    }
    case 'contact': openContact(id); break;
    case 'close-modal': closeOverlay(); break;
    case 'car-prev': goCarousel(FG.idx-1); break;
    case 'car-next': goCarousel(FG.idx+1); break;
    case 'dot': goCarousel(Number(t.dataset.i)); break;
    case 'chip': FG.tag=t.dataset.tag; FG.page='search'; render(); break;
    case 'clear-tag': FG.tag=null; render(); break;
    case 'scan': runScan(); break;
    case 'save-item': saveItem(); break;
    case 'reset-scan': FG.pending=null; FG.pendingTags=[]; FG.pendingFile=null; render(); break;
    case 'tag-remove': {
      FG.pendingTags.splice(Number(t.dataset.i),1);
      const ed=document.getElementById('tagEditor');
      if(ed) ed.innerHTML=FG.pendingTags.map((tt,i)=>`<span class="tag-chip">#${esc(tt)}<button data-action="tag-remove" data-i="${i}" aria-label="Tag entfernen">${IC.x}</button></span>`).join('');
      break;
    }
  }
});

/* ============ Uhr ============ */
function tickClock(){
  const d=new Date();
  document.getElementById('clock').textContent=d.getHours()+':'+String(d.getMinutes()).padStart(2,'0');
}
tickClock(); setInterval(tickClock,15000);

render();
</script>
</body>
</html>

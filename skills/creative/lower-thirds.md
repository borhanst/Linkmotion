# Lower Thirds

Reusable lower-third overlay built as an HTML component (GSAP). Author it inside
`projects/<slug>/src/html/<scene>/index.html` (never globally). Starter template:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background: transparent; overflow: hidden; width:1920px; height:1080px; }
    .lt { position:absolute; left:80px; bottom:90px; display:flex; align-items:center; gap:18px; opacity:0; transform:translateX(-60px); }
    .lt .bar { width:6px; height:70px; background:#ff3b3b; }
    .lt .name { color:#fff; font-size:42px; font-weight:800; }
    .lt .title { color:#bbb; font-size:22px; margin-top:6px; }
  </style>
</head>
<body>
  <div class="lt" id="lt">
    <div class="bar"></div>
    <div><div class="name">Jane Doe</div><div class="title">AI Research Lead</div></div>
  </div>
  <script>
    const tl = gsap.timeline();
    tl.to('#lt', { opacity:1, x:0, duration:0.6, ease:'power3.out' })
      .to('#lt', { opacity:0, x:-60, duration:0.4, delay:3.5, ease:'power2.in' });
  </script>
</body>
</html>
```

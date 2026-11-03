# Page Transitions

Reusable page-transition treatment (wipe) as HTML (GSAP). Author inside
`projects/<slug>/src/html/<scene>/index.html`. Starter template:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#0b0b0f; overflow:hidden; width:1920px; height:1080px; }
    .wipe { position:absolute; inset:0; background:#ff3b3b; transform:scaleX(0); transform-origin:left; }
  </style>
</head>
<body>
  <div class="wipe" id="wipe"></div>
  <script>
    const tl = gsap.timeline();
    tl.to('#wipe',{scaleX:1,duration:0.5,ease:'power2.inOut'})
      .to('#wipe',{scaleX:0,transformOrigin:'right',duration:0.5,delay:0.6,ease:'power2.inOut'});
  </script>
</body>
</html>
```

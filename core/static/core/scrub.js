/**
 * Frame Scrubber: scroll/wheel-driven image-sequence animation on a <canvas>.
 * Smoothness comes from lerp (easing toward the target) + crossfading neighbouring frames.
 *
 * Usage:
 *   const scrubber = createFrameScrubber({
 *     canvas: document.getElementById('introCanvas'),
 *     frameCount: 240,
 *     src: i => `/static/core/frames/f_${String(i).padStart(4, '0')}.webp`,
 *   });
 *   scrubber.addDelta(0.02);   // wheel-driven
 *   scrubber.setProgress(0.5); // or jump directly (0..1)
 */
window.createFrameScrubber = function ({
  canvas,
  frameCount,
  src,
  lerp = 0.08,       // lower = floatier, higher = snappier
  onProgress = null, // called with eased progress 0..1
  onLoad = null      // called with loaded fraction 0..1
}) {
  const ctx = canvas.getContext('2d');
  const images = new Array(frameCount);
  let loaded = 0;
  let current = 0;   // eased frame position (float)
  let target = 0;    // target frame position (float)
  let rafId = null;
  let sized = false;

  // ---- Preload: first frame first, then the rest ----
  function load(i) {
    return new Promise(resolve => {
      const img = new Image();
      img.decoding = 'async';
      img.onload = img.onerror = () => {
        loaded++;
        if (onLoad) onLoad(loaded / frameCount);
        if (!sized && img.naturalWidth) {
          canvas.width = img.naturalWidth;
          canvas.height = img.naturalHeight;
          sized = true;
        }
        resolve();
      };
      img.src = src(i + 1);
      images[i] = img;
    });
  }

  const ready = load(0).then(() => {
    draw();
    // Load the rest in small batches so the first paint isn't blocked
    const rest = [];
    for (let i = 1; i < frameCount; i++) rest.push(i);
    return (async () => {
      while (rest.length) {
        await Promise.all(rest.splice(0, 12).map(load));
      }
    })();
  });

  // ---- Draw two neighbouring frames with a crossfade ----
  function draw() {
    const f = Math.floor(current);
    const t = current - f;
    const a = images[f];
    const b = images[Math.min(f + 1, frameCount - 1)];
    if (!a || !a.complete || !a.naturalWidth) return;

    ctx.globalAlpha = 1;
    ctx.drawImage(a, 0, 0, canvas.width, canvas.height);
    if (t > 0.01 && b && b.complete && b.naturalWidth) {
      ctx.globalAlpha = t;
      ctx.drawImage(b, 0, 0, canvas.width, canvas.height);
      ctx.globalAlpha = 1;
    }
  }

  // ---- Render loop: runs only while the animation is still settling ----
  function tick() {
    current += (target - current) * lerp;
    if (Math.abs(target - current) < 0.01) current = target;
    draw();
    if (onProgress) onProgress(current / (frameCount - 1));

    rafId = current !== target ? requestAnimationFrame(tick) : null;
  }

  function kick() {
    if (rafId === null) rafId = requestAnimationFrame(tick);
  }

  // ---- Public API ----
  return {
    ready,
    setProgress(p) {
      target = Math.min(1, Math.max(0, p)) * (frameCount - 1);
      kick();
    },
    addDelta(dp) {
      this.setProgress(target / (frameCount - 1) + dp);
    },
    getProgress() {
      return target / (frameCount - 1);
    },
    getEasedProgress() {
      return current / (frameCount - 1);
    },
    reset() {
      current = target = 0;
      draw();
    }
  };
};

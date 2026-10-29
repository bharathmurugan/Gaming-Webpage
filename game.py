from flask import Flask, render_template_string

app = Flask(__name__)

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dino Run — Cinematic Edition</title>
<style>
  :root {
    --sky-top: #0b1030;
    --sky-bottom: #2a1450;
    --sun: #ff7a3d;
    --ground: #e7e2d6;
    --accent: #ffd166;
    --dino: #f5f5f5;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    height: 100%;
    background: #05040c;
    color: #eee;
    font-family: "Segoe UI", system-ui, sans-serif;
    overflow: hidden;
  }

  /* ---------- POWER-OFF INTRO ---------- */
  #powerScreen {
    position: fixed; inset: 0; z-index: 100;
    background: #fff;
    display: flex; align-items: center; justify-content: center;
    animation: flicker 0.6s steps(2) 0s 1;
  }
  #powerScreen.collapse {
    animation: crtOff 0.9s ease-in forwards;
  }
  @keyframes flicker {
    0% { opacity: 1; } 20% { opacity: 0.2; } 40% { opacity: 1; }
    60% { opacity: 0.4; } 100% { opacity: 1; }
  }
  @keyframes crtOff {
    0% { transform: scale(1, 1); filter: brightness(1.5); }
    60% { transform: scale(1, 0.01); filter: brightness(3); }
    100% { transform: scale(0.001, 0.01); opacity: 0; }
  }
  .scanlines::after {
    content: ""; position: absolute; inset: 0;
    background: repeating-linear-gradient(to bottom, rgba(0,0,0,0.12) 0 2px, transparent 2px 4px);
    pointer-events: none;
  }
  #powerScreen .msg {
    font-family: "Courier New", monospace; color: #111;
    font-size: clamp(14px, 2vw, 20px); letter-spacing: 3px;
    position: relative;
  }

  /* ---------- POPUP CARD ---------- */
  #popup {
    position: fixed; inset: 0; z-index: 90;
    display: none; align-items: center; justify-content: center;
    background: radial-gradient(ellipse at center, rgba(10,6,30,0.85), rgba(0,0,0,0.97));
    backdrop-filter: blur(4px);
  }
  #popup.show { display: flex; animation: fadeUp 0.8s ease-out both; }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(30px) scale(0.96); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }
  .card {
    text-align: center; padding: 40px 48px;
    border: 1px solid rgba(255,209,102,0.35);
    border-radius: 18px;
    background: linear-gradient(160deg, rgba(40,20,80,0.6), rgba(10,8,25,0.9));
    box-shadow: 0 0 60px rgba(255,122,61,0.25);
    max-width: 480px;
  }
  .card h1 {
    font-size: clamp(28px, 5vw, 46px); letter-spacing: 4px;
    background: linear-gradient(90deg, #ffd166, #ff7a3d, #ff4d8d);
    -webkit-background-clip: text; background-clip: text; color: transparent;
    margin-bottom: 10px;
  }
  .card p { color: #bfb8d9; margin-bottom: 24px; line-height: 1.5; }
  .btn {
    display: inline-block; cursor: pointer; border: none;
    padding: 14px 40px; border-radius: 999px;
    font-size: 16px; font-weight: 700; letter-spacing: 2px;
    color: #1a1030; background: linear-gradient(90deg, #ffd166, #ff7a3d);
    box-shadow: 0 8px 30px rgba(255,122,61,0.45);
    transition: transform .15s ease, box-shadow .15s ease;
  }
  .btn:hover { transform: translateY(-2px) scale(1.03); box-shadow: 0 12px 40px rgba(255,122,61,0.6); }
  .hint { margin-top: 18px; font-size: 13px; color: #8d86ad; }

  /* ---------- GAME SCENE ---------- */
  #scene {
    position: fixed; inset: 0;
    background: linear-gradient(to bottom, var(--sky-top), var(--sky-bottom));
    display: none; flex-direction: column; align-items: center; justify-content: center;
  }
  #scene.show { display: flex; animation: fadeIn 1s ease both; }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

  .stars { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
  .star {
    position: absolute; width: 2px; height: 2px; background: #fff; border-radius: 50%;
    animation: twinkle 3s infinite ease-in-out;
  }
  @keyframes twinkle { 0%,100% { opacity: .2; } 50% { opacity: 1; } }

  .sun {
    position: absolute; top: 8%; right: 10%;
    width: 110px; height: 110px; border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #ffd9a0, var(--sun) 60%, #c2410c);
    box-shadow: 0 0 80px 20px rgba(255,122,61,0.35);
    animation: sunPulse 6s ease-in-out infinite;
  }
  @keyframes sunPulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.06); } }

  .mountains {
    position: absolute; bottom: 0; left: 0; width: 200%; height: 40%;
    pointer-events: none;
    background:
      linear-gradient(160deg, transparent 0 30%, #1f1446 30% 55%, transparent 55%) 0 0 / 240px 100% repeat-x,
      linear-gradient(200deg, transparent 0 30%, #140c33 30% 60%, transparent 60%) 0 0 / 320px 100% repeat-x;
    opacity: .75;
    animation: parallax 30s linear infinite;
  }
  @keyframes parallax { from { transform: translateX(0); } to { transform: translateX(-50%); } }

  #hud {
    position: absolute; top: 20px; left: 0; right: 0;
    display: flex; justify-content: space-between; padding: 0 40px;
    font-family: "Courier New", monospace; font-size: 18px; letter-spacing: 2px;
    color: var(--accent); text-shadow: 0 0 10px rgba(255,209,102,.6);
    z-index: 5;
  }

  #gameWrap {
    position: relative; width: min(900px, 95vw); height: min(360px, 60vh);
    border-bottom: 3px solid rgba(231,226,214,0.8);
    z-index: 2;
  }
  canvas#game {
    width: 100%; height: 100%; display: block;
    image-rendering: pixelated;
  }

  #gameOver {
    position: absolute; inset: 0; display: none;
    align-items: center; justify-content: center; flex-direction: column;
    background: rgba(5,4,12,0.55); z-index: 6;
  }
  #gameOver.show { display: flex; animation: fadeIn .4s ease both; }
  #gameOver h2 {
    font-size: clamp(28px, 4vw, 44px); letter-spacing: 6px; color: #ff4d8d;
    text-shadow: 0 0 20px rgba(255,77,141,.6); margin-bottom: 16px;
  }
  #gameOver p { color: #ddd; margin-bottom: 20px; }

  .controls-hint {
    margin-top: 14px; font-size: 13px; color: #8d86ad; letter-spacing: 1px; z-index: 2;
  }
  .exit {
    position: absolute; bottom: 16px; right: 20px; z-index: 6;
    background: none; border: 1px solid rgba(255,255,255,0.25); color: #aaa;
    padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 12px;
  }
  .exit:hover { color: #fff; border-color: #fff; }
</style>
</head>
<body>

<!-- Power-off screen -->
<div id="powerScreen" class="scanlines">
  <div class="msg">SIGNAL LOST — STANDBY</div>
</div>

<!-- Popup -->
<div id="popup">
  <div class="card">
    <h1>DINO RUN</h1>
    <p>Power failed. Survive the desert. Jump the cacti, duck the pterodactyls, and beat your best run.</p>
    <button class="btn" id="startBtn">START RUN</button>
    <div class="hint">SPACE / ↑ to jump &nbsp;·&nbsp; ↓ to duck</div>
  </div>
</div>

<!-- Game scene -->
<div id="scene">
  <div class="stars" id="stars"></div>
  <div class="sun"></div>
  <div class="mountains"></div>

  <div id="hud">
    <span>SCORE <span id="score">00000</span></span>
    <span>HI <span id="hi">00000</span></span>
  </div>

  <div id="gameWrap">
    <canvas id="game"></canvas>
    <div id="gameOver">
      <h2>GAME OVER</h2>
      <p>Score: <span id="finalScore">0</span></p>
      <button class="btn" id="restartBtn">RUN AGAIN</button>
    </div>
  </div>
  <div class="controls-hint">SPACE / ↑ jump &nbsp;·&nbsp; ↓ duck &nbsp;·&nbsp; P pause</div>
  <button class="exit" id="exitBtn">EXIT</button>
</div>

<script>
// ---------- Starfield ----------
(function makeStars() {
  const box = document.getElementById("stars");
  for (let i = 0; i < 90; i++) {
    const s = document.createElement("div");
    s.className = "star";
    s.style.left = Math.random() * 100 + "%";
    s.style.top = Math.random() * 60 + "%";
    s.style.animationDelay = (Math.random() * 3) + "s";
    box.appendChild(s);
  }
})();

// ---------- Power-off -> popup sequence ----------
const powerScreen = document.getElementById("powerScreen");
const popup = document.getElementById("popup");

setTimeout(() => powerScreen.classList.add("collapse"), 1400);
setTimeout(() => {
  powerScreen.style.display = "none";
  popup.classList.add("show");
}, 2300);

// ---------- Game ----------
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scene = document.getElementById("scene");
const gameOverEl = document.getElementById("gameOver");
const scoreEl = document.getElementById("score");
const hiEl = document.getElementById("hi");
const finalScoreEl = document.getElementById("finalScore");

let W, H, GROUND;
function resize() {
  const r = canvas.getBoundingClientRect();
  canvas.width = r.width * devicePixelRatio;
  canvas.height = r.height * devicePixelRatio;
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  W = r.width; H = r.height;
  GROUND = H - 40;
}
window.addEventListener("resize", resize);

const G = 0.65, JUMP_V = -12.5;
let state, obstacles, clouds, particles, speed, frame, score, hi, paused;
hi = parseInt(localStorage.getItem("dino_hi") || "0", 10);
hiEl.textContent = String(hi).padStart(5, "0");

function resetGame() {
  state = {
    x: 70, y: 0, vy: 0, onGround: true, ducking: false,
    legPhase: 0, blink: 0
  };
  obstacles = []; clouds = []; particles = [];
  speed = 6; frame = 0; score = 0; paused = false;
  gameOverEl.classList.remove("show");
  scoreEl.textContent = "00000";
}

function spawnObstacle() {
  const r = Math.random();
  if (r < 0.55) {
    // cactus cluster
    const count = Math.random() < 0.3 ? 2 : 1;
    const h = 34 + Math.random() * 22;
    obstacles.push({ type: "cactus", x: W + 10, w: 18 * count + (count - 1) * 6, h, y: GROUND - h, count });
  } else if (r < 0.8 && score > 200) {
    // pterodactyl, flies at 3 heights
    const heights = [GROUND - 40, GROUND - 70, GROUND - 100];
    obstacles.push({ type: "ptero", x: W + 10, w: 46, h: 26, y: heights[Math.floor(Math.random() * 3)], wing: 0 });
  } else {
    // rock
    const h = 20 + Math.random() * 10;
    obstacles.push({ type: "rock", x: W + 10, w: 26, h, y: GROUND - h });
  }
}

function spawnCloud() {
  clouds.push({ x: W + 20, y: 20 + Math.random() * 90, s: 0.6 + Math.random() * 0.6 });
}

function burst(x, y, color) {
  for (let i = 0; i < 14; i++) {
    particles.push({
      x, y, vx: (Math.random() - 0.5) * 6, vy: (Math.random() - 1.2) * 5,
      life: 40 + Math.random() * 20, color
    });
  }
}

function collides(a, b) {
  const pad = 4;
  return a.x + pad < b.x + b.w - pad && a.x + a.w - pad > b.x + pad &&
         a.y + pad < b.y + b.h - pad && a.y + a.h - pad > b.y + pad;
}

function dinoBox() {
  if (state.ducking && state.onGround) {
    return { x: state.x, y: GROUND - 26, w: 52, h: 26 };
  }
  const h = 46;
  return { x: state.x, y: GROUND - h + state.y, w: 40, h };
}

function drawDino() {
  const b = dinoBox();
  ctx.save();
  ctx.fillStyle = "#f5f5f5";
  ctx.shadowColor = "rgba(255,209,102,0.6)";
  ctx.shadowBlur = 12;

  if (state.ducking && state.onGround) {
    // ducking body
    ctx.fillRect(b.x, b.y + 6, 50, 14);
    ctx.fillRect(b.x + 40, b.y, 14, 12);
    ctx.fillStyle = "#0b1030";
    ctx.fillRect(b.x + 48, b.y + 3, 3, 3);
  } else {
    // body
    ctx.fillRect(b.x + 8, b.y + 8, 26, 26);
    // head
    ctx.fillRect(b.x + 20, b.y, 22, 20);
    // snout
    ctx.fillRect(b.x + 34, b.y + 8, 10, 8);
    // tail
    ctx.beginPath();
    ctx.moveTo(b.x + 8, b.y + 20);
    ctx.lineTo(b.x, b.y + 14);
    ctx.lineTo(b.x + 8, b.y + 28);
    ctx.fill();
    // eye
    ctx.fillStyle = "#0b1030";
    const blinking = state.blink > 0;
    if (!blinking) ctx.fillRect(b.x + 33, b.y + 4, 3, 3);
    // legs (animated)
    ctx.fillStyle = "#f5f5f5";
    if (state.onGround) {
      const phase = Math.floor(state.legPhase) % 2;
      if (phase === 0) {
        ctx.fillRect(b.x + 12, b.y + 34, 7, 12);
        ctx.fillRect(b.x + 24, b.y + 38, 7, 8);
      } else {
        ctx.fillRect(b.x + 12, b.y + 38, 7, 8);
        ctx.fillRect(b.x + 24, b.y + 34, 7, 12);
      }
    } else {
      ctx.fillRect(b.x + 14, b.y + 34, 7, 10);
      ctx.fillRect(b.x + 24, b.y + 34, 7, 10);
    }
  }
  ctx.restore();
}

function drawCactus(o) {
  ctx.fillStyle = "#3fbf7f";
  ctx.shadowColor = "rgba(63,191,127,0.6)";
  ctx.shadowBlur = 10;
  for (let i = 0; i < o.count; i++) {
    const cx = o.x + i * (18 + 6);
    ctx.fillRect(cx + 6, o.y, 6, o.h);
    ctx.fillRect(cx, o.y + o.h * 0.35, 6, 8);
    ctx.fillRect(cx, o.y + o.h * 0.35, 12, 4);
    ctx.fillRect(cx + 12, o.y + o.h * 0.15, 6, 16);
    ctx.fillRect(cx + 12, o.y + o.h * 0.15, 6, 4);
  }
  ctx.shadowBlur = 0;
}

function drawRock(o) {
  ctx.fillStyle = "#8b7fb0";
  ctx.shadowColor = "rgba(139,127,176,0.5)";
  ctx.shadowBlur = 8;
  ctx.beginPath();
  ctx.ellipse(o.x + o.w / 2, o.y + o.h / 2, o.w / 2, o.h / 2, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;
}

function drawPtero(o) {
  o.wing += 0.25;
  const up = Math.sin(o.wing) > 0;
  ctx.fillStyle = "#ff4d8d";
  ctx.shadowColor = "rgba(255,77,141,0.6)";
  ctx.shadowBlur = 12;
  // body
  ctx.fillRect(o.x + 10, o.y + 8, 26, 10);
  // head
  ctx.fillRect(o.x + 32, o.y + 6, 10, 8);
  // wing
  if (up) {
    ctx.beginPath();
    ctx.moveTo(o.x + 16, o.y + 8);
    ctx.lineTo(o.x + 22, o.y - 8);
    ctx.lineTo(o.x + 28, o.y + 8);
    ctx.fill();
  } else {
    ctx.beginPath();
    ctx.moveTo(o.x + 16, o.y + 18);
    ctx.lineTo(o.x + 22, o.y + 30);
    ctx.lineTo(o.x + 28, o.y + 18);
    ctx.fill();
  }
  ctx.shadowBlur = 0;
}

function drawGround() {
  ctx.fillStyle = "#e7e2d6";
  ctx.fillRect(0, GROUND, W, 2);
  ctx.fillStyle = "rgba(231,226,214,0.35)";
  for (let i = 0; i < 14; i++) {
    const x = ((i * 97 - frame * speed * 0.5) % W + W) % W;
    ctx.fillRect(x, GROUND + 8 + (i % 3) * 6, 8 + (i % 4) * 4, 2);
  }
}

function drawClouds() {
  ctx.fillStyle = "rgba(255,255,255,0.12)";
  for (const c of clouds) {
    ctx.beginPath();
    ctx.ellipse(c.x, c.y, 34 * c.s, 10 * c.s, 0, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawParticles() {
  for (const p of particles) {
    ctx.globalAlpha = Math.max(p.life / 60, 0);
    ctx.fillStyle = p.color;
    ctx.fillRect(p.x, p.y, 3, 3);
  }
  ctx.globalAlpha = 1;
}

function update() {
  if (paused) return;
  frame++;
  speed = Math.min(6 + score / 300, 16);

  // dino physics
  if (!state.onGround) {
    state.vy += G;
    state.y += state.vy;
    if (state.y >= 0) {
      state.y = 0; state.vy = 0; state.onGround = true;
    }
  }
  if (state.onGround) state.legPhase += speed * 0.05;
  if (state.blink > 0) state.blink--;
  else if (Math.random() < 0.005) state.blink = 6;

  // obstacles
  if (frame % Math.max(60 - Math.floor(speed * 2), 36) === 0 || (frame > 60 && Math.random() < 0.006)) {
    if (obstacles.length === 0 || obstacles[obstacles.length - 1].x < W - 220) spawnObstacle();
  }
  for (const o of obstacles) o.x -= speed;
  obstacles = obstacles.filter(o => o.x + o.w > -20);

  if (Math.random() < 0.008) spawnCloud();
  for (const c of clouds) c.x -= speed * 0.2;
  clouds = clouds.filter(c => c.x > -80);

  for (const p of particles) {
    p.x += p.vx; p.y += p.vy; p.vy += 0.2; p.life--;
  }
  particles = particles.filter(p => p.life > 0);

  // collision
  const db = dinoBox();
  for (const o of obstacles) {
    if (collides(db, o)) {
      burst(state.x + 20, GROUND - 20, "#ff4d8d");
      endGame();
      return;
    }
  }

  score++;
  if (score % 100 === 0) {
    burst(W - 60, 40, "#ffd166");
  }
  scoreEl.textContent = String(score).padStart(5, "0");
}

function render() {
  ctx.clearRect(0, 0, W, H);
  drawClouds();
  drawGround();
  for (const o of obstacles) {
    if (o.type === "cactus") drawCactus(o);
    else if (o.type === "rock") drawRock(o);
    else drawPtero(o);
  }
  drawDino();
  drawParticles();
}

let running = false;
function loop() {
  if (!running) return;
  update();
  render();
  requestAnimationFrame(loop);
}

function startGame() {
  resetGame();
  resize();
  running = true;
  loop();
}

function endGame() {
  running = false;
  if (score > hi) {
    hi = score;
    localStorage.setItem("dino_hi", String(hi));
    hiEl.textContent = String(hi).padStart(5, "0");
  }
  finalScoreEl.textContent = score;
  gameOverEl.classList.add("show");
  render();
}

// ---------- Input ----------
function jump() {
  if (!running) return;
  if (state.onGround && !state.ducking) {
    state.vy = JUMP_V;
    state.onGround = false;
  }
}
function setDuck(on) {
  if (!running) return;
  if (on && state.onGround) state.ducking = true;
  if (!on) state.ducking = false;
}

document.addEventListener("keydown", (e) => {
  if (e.code === "Space" || e.code === "ArrowUp") {
    e.preventDefault();
    if (!running && gameOverEl.classList.contains("show")) return;
    jump();
  } else if (e.code === "ArrowDown") {
    e.preventDefault();
    setDuck(true);
  } else if (e.code === "KeyP") {
    paused = !paused;
    if (!paused && running) loop();
  }
});
document.addEventListener("keyup", (e) => {
  if (e.code === "ArrowDown") setDuck(false);
});

// ---------- Buttons ----------
document.getElementById("startBtn").addEventListener("click", () => {
  popup.classList.remove("show");
  scene.classList.add("show");
  resize();
  startGame();
});
document.getElementById("restartBtn").addEventListener("click", () => {
  startGame();
});
document.getElementById("exitBtn").addEventListener("click", () => {
  running = false;
  scene.classList.remove("show");
  popup.classList.add("show");
});
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE)


if __name__ == "__main__":
    app.run(debug=True)
/*
  BATYR BOL — Система частиц для экрана победы
  Canvas-based particle system
*/

class ParticleSystem {
  constructor() {
    this.canvas = null;
    this.ctx = null;
    this.particles = [];
    this.animationFrame = null;
  }

  // Создание canvas для частиц
  createCanvas() {
    if (this.canvas) return;

    this.canvas = document.createElement('canvas');
    this.canvas.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 100;
    `;
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    document.body.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
  }

  // Золотые частицы при победе
  celebrateVictory() {
    this.createCanvas();
    this.particles = [];

    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;

    // 80-100 частиц
    for (let i = 0; i < 90; i++) {
      const angle = (Math.random() * Math.PI * 2);
      const speed = 2 + Math.random() * 6;

      this.particles.push({
        x: centerX,
        y: centerY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 2,
        radius: 2 + Math.random() * 4,
        color: Math.random() > 0.3
          ? `rgba(212, 175, 55, ${0.6 + Math.random() * 0.4})`
          : `rgba(245, 240, 232, ${0.4 + Math.random() * 0.4})`,
        life: 1,
        decay: 0.008 + Math.random() * 0.012,
        gravity: 0.05 + Math.random() * 0.05,
      });
    }

    this.animate();

    // Остановить через 2.5 секунды
    setTimeout(() => this.stop(), 2500);
  }

  // XP flash анимация
  xpFlash() {
    this.createCanvas();
    this.particles = [];

    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;

    // Круговая вспышка
    for (let i = 0; i < 40; i++) {
      const angle = (Math.PI * 2 / 40) * i;
      const speed = 3 + Math.random() * 3;

      this.particles.push({
        x: centerX,
        y: centerY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        radius: 1.5 + Math.random() * 2,
        color: `rgba(240, 208, 96, ${0.5 + Math.random() * 0.5})`,
        life: 1,
        decay: 0.02 + Math.random() * 0.015,
        gravity: 0,
      });
    }

    this.animate();
    setTimeout(() => this.stop(), 1500);
  }

  animate() {
    if (!this.ctx || !this.canvas) return;

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.particles = this.particles.filter(p => p.life > 0);

    if (this.particles.length === 0) {
      this.stop();
      return;
    }

    for (const p of this.particles) {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += p.gravity;
      p.life -= p.decay;

      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.radius * p.life, 0, Math.PI * 2);
      this.ctx.fillStyle = p.color;
      this.ctx.fill();
    }

    this.animationFrame = requestAnimationFrame(() => this.animate());
  }

  stop() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = null;
    }
    if (this.canvas) {
      this.canvas.remove();
      this.canvas = null;
      this.ctx = null;
    }
    this.particles = [];
  }
}

// XP счетчик с анимацией
function animateXPCounter(element, from, to, duration = 1000) {
  const start = performance.now();
  const diff = to - from;

  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic

    element.textContent = Math.round(from + diff * eased);

    if (progress < 1) {
      requestAnimationFrame(tick);
    }
  }

  requestAnimationFrame(tick);
}

// Глобальный экземпляр
window.batyrParticles = new ParticleSystem();
window.animateXPCounter = animateXPCounter;

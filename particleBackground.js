/**
 * Particle Background Effect
 * Creates an animated particle background effect for the application
 */

export default class ParticleBackground {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      console.error(`Container with ID "${containerId}" not found.`);
      return;
    }
    
    // Default options
    this.options = {
      particleCount: options.particleCount || 50,
      particleColor: options.particleColor || '#0ea5e9',
      minSize: options.minSize || 1,
      maxSize: options.maxSize || 5,
      minSpeed: options.minSpeed || 0.2,
      maxSpeed: options.maxSpeed || 1,
      connectParticles: options.connectParticles || true,
      lineColor: options.lineColor || 'rgba(14, 165, 233, 0.3)',
      lineWidth: options.lineWidth || 1,
      lineDistance: options.lineDistance || 150,
      responsive: options.responsive || [
        {
          breakpoint: 768,
          options: {
            particleCount: 30,
            connectParticles: true
          }
        },
        {
          breakpoint: 425,
          options: {
            particleCount: 15,
            connectParticles: false
          }
        }
      ]
    };
    
    this.particles = [];
    this.width = this.container.offsetWidth;
    this.height = this.container.offsetHeight;
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.animationFrame = null;
    
    this.init();
  }
  
  init() {
    // Set canvas size
    this.canvas.width = this.width;
    this.canvas.height = this.height;
    this.canvas.style.position = 'absolute';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.zIndex = '-1';
    
    // Append canvas to container
    this.container.appendChild(this.canvas);
    
    // Create particles
    this.createParticles();
    
    // Start animation
    this.animate();
    
    // Handle window resize
    window.addEventListener('resize', this.handleResize.bind(this));
  }
  
  createParticles() {
    this.particles = [];
    
    // Apply responsive options
    let particleCount = this.options.particleCount;
    let connectParticles = this.options.connectParticles;
    
    if (this.options.responsive) {
      this.options.responsive.forEach(config => {
        if (window.innerWidth <= config.breakpoint) {
          if (config.options.particleCount) {
            particleCount = config.options.particleCount;
          }
          if (typeof config.options.connectParticles !== 'undefined') {
            connectParticles = config.options.connectParticles;
          }
        }
      });
    }
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
      const size = Math.random() * (this.options.maxSize - this.options.minSize) + this.options.minSize;
      const speed = Math.random() * (this.options.maxSpeed - this.options.minSpeed) + this.options.minSpeed;
      
      this.particles.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        size: size,
        color: this.options.particleColor,
        speedX: Math.random() * speed * (Math.random() > 0.5 ? 1 : -1),
        speedY: Math.random() * speed * (Math.random() > 0.5 ? 1 : -1),
        connect: connectParticles
      });
    }
  }
  
  animate() {
    this.ctx.clearRect(0, 0, this.width, this.height);
    
    // Update and draw particles
    this.particles.forEach(particle => {
      // Update position
      particle.x += particle.speedX;
      particle.y += particle.speedY;
      
      // Bounce off edges
      if (particle.x < 0 || particle.x > this.width) {
        particle.speedX *= -1;
      }
      
      if (particle.y < 0 || particle.y > this.height) {
        particle.speedY *= -1;
      }
      
      // Draw particle
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      this.ctx.fillStyle = particle.color;
      this.ctx.fill();
      
      // Connect particles
      if (particle.connect) {
        this.particles.forEach(otherParticle => {
          if (particle !== otherParticle) {
            const dx = particle.x - otherParticle.x;
            const dy = particle.y - otherParticle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.options.lineDistance) {
              const opacity = 1 - (distance / this.options.lineDistance);
              this.ctx.beginPath();
              this.ctx.moveTo(particle.x, particle.y);
              this.ctx.lineTo(otherParticle.x, otherParticle.y);
              this.ctx.strokeStyle = this.options.lineColor.replace(')', `, ${opacity})`).replace('rgb', 'rgba');
              this.ctx.lineWidth = this.options.lineWidth;
              this.ctx.stroke();
            }
          }
        });
      }
    });
    
    this.animationFrame = requestAnimationFrame(this.animate.bind(this));
  }
  
  handleResize() {
    this.width = this.container.offsetWidth;
    this.height = this.container.offsetHeight;
    this.canvas.width = this.width;
    this.canvas.height = this.height;
    this.createParticles();
  }
  
  destroy() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
    
    if (this.canvas && this.canvas.parentNode) {
      this.canvas.parentNode.removeChild(this.canvas);
    }
    
    window.removeEventListener('resize', this.handleResize.bind(this));
  }
}

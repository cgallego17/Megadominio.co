// JavaScript para Megadominio.co - Con efectos de movimiento suaves
document.addEventListener('DOMContentLoaded', function() {
    
    // ===== NAVEGACIÓN SUAVE =====
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ===== MENÚ HAMBURGUESA =====
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Cerrar menú al hacer click en un enlace
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }
    
    // ===== HEADER CON SCROLL =====
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                header.style.background = 'rgba(0, 0, 0, 0.9)';
                header.style.backdropFilter = 'blur(20px)';
            } else {
                header.style.background = 'rgba(0, 0, 0, 0.7)';
                header.style.backdropFilter = 'blur(25px)';
            }
        });
    }
    
    // ===== EFECTOS DE PARALLAX SUAVE =====
    let ticking = false;
    
    function updateParallax() {
        const scrollY = window.scrollY;
        
        // Parallax muy sutil en las tarjetas del hero
        const heroCard = document.querySelector('.hero-card');
        if (heroCard) {
            const cardTransform = scrollY * -0.1;
            heroCard.style.transform = `translateY(${cardTransform}px)`;
        }
        
        // Parallax en iconos de servicios
        const servicioIcons = document.querySelectorAll('.servicio-icon');
        servicioIcons.forEach((icon, index) => {
            const speed = 0.05 + (index * 0.01);
            const yPos = scrollY * speed;
            icon.style.transform = `translateY(${yPos}px)`;
        });
        
        // Parallax en imágenes de proyectos
        const portfolioImages = document.querySelectorAll('.portfolio-image img');
        portfolioImages.forEach((img, index) => {
            const speed = 0.03 + (index * 0.005);
            const yPos = scrollY * speed;
            img.style.transform = `translateY(${yPos}px) scale(1)`;
        });
        
        ticking = false;
    }
    
    function requestParallax() {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestParallax);
    
    // ===== EFECTOS DE MOUSE EN EL HERO =====
    const hero = document.querySelector('.hero');
    const heroContent = document.querySelector('.hero-content');
    const heroVisual = document.querySelector('.hero-visual');
    
    if (hero && heroContent && heroVisual) {
        hero.addEventListener('mousemove', function(e) {
            const rect = hero.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const deltaX = (x - centerX) / centerX;
            const deltaY = (y - centerY) / centerY;
            
            // Movimiento muy sutil del contenido
            const moveX = deltaX * 10;
            const moveY = deltaY * 10;
            
            heroContent.style.transform = `translate(${moveX * 0.5}px, ${moveY * 0.5}px)`;
            heroVisual.style.transform = `translate(${moveX * -0.3}px, ${moveY * -0.3}px)`;
        });
        
        hero.addEventListener('mouseleave', function() {
            heroContent.style.transform = '';
            heroVisual.style.transform = '';
        });
    }
    
    // ===== ANIMACIONES SIMPLES PARA TARJETAS =====
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                // Añadir un pequeño delay escalonado
                if (entry.target.classList.contains('servicio-card') || 
                    entry.target.classList.contains('proyecto-card')) {
                    const cards = Array.from(entry.target.parentElement.children);
                    const index = cards.indexOf(entry.target);
                    entry.target.style.transitionDelay = `${index * 0.1}s`;
                }
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    // Observar elementos que necesitan animación
    const animatedElements = document.querySelectorAll('.servicio-card, .proyecto-card, .stat-item, .testimonial-item');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });
    
    // ===== EFECTOS FLOTANTES SUTILES =====
    function createFloatingElements() {
        const sections = document.querySelectorAll('.servicios, .proyectos, .stats, .testimonials, .contacto');
        
        sections.forEach(section => {
            // Crear elementos flotantes muy sutiles
            for (let i = 0; i < 3; i++) {
                const float = document.createElement('div');
                float.style.position = 'absolute';
                float.style.width = '2px';
                float.style.height = '2px';
                float.style.background = `rgba(255, 102, 0, ${Math.random() * 0.1 + 0.05})`;
                float.style.borderRadius = '50%';
                float.style.pointerEvents = 'none';
                float.style.left = Math.random() * 100 + '%';
                float.style.top = Math.random() * 100 + '%';
                float.style.zIndex = '1';
                
                // Animación flotante muy sutil
                float.animate([
                    { transform: 'translateY(0px)', opacity: 0.1 },
                    { transform: 'translateY(-20px)', opacity: 0.3 },
                    { transform: 'translateY(0px)', opacity: 0.1 }
                ], {
                    duration: Math.random() * 4000 + 6000,
                    iterations: Infinity,
                    easing: 'ease-in-out'
                });
                
                section.appendChild(float);
            }
        });
    }
    
    // Crear elementos flotantes después de un pequeño delay
    setTimeout(createFloatingElements, 1000);
    
    // ===== FORMULARIO DE CONTACTO =====
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const button = this.querySelector('.btn-form');
            const originalText = button.textContent;
            
            // Efecto de envío
            button.textContent = 'Enviando...';
            button.style.background = 'rgba(255, 102, 0, 0.5)';
            button.disabled = true;
            
            // Simular envío (aquí conectarías con tu backend)
            setTimeout(() => {
                button.textContent = '✓ Enviado';
                button.style.background = 'rgba(0, 255, 136, 0.8)';
                
                setTimeout(() => {
                    button.textContent = originalText;
                    button.style.background = '';
                    button.disabled = false;
                    this.reset();
                }, 2000);
            }, 1500);
        });
    }
    
    // ===== TESTIMONIALS SLIDER SIMPLE =====
    const testimonials = document.querySelectorAll('.testimonial-item');
    if (testimonials.length > 1) {
        let currentTestimonial = 0;
        
        // Mostrar solo el primero inicialmente
        testimonials.forEach((item, index) => {
            if (index === 0) {
                item.classList.add('active');
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
        
        // Cambiar testimonial cada 5 segundos
        setInterval(() => {
            testimonials[currentTestimonial].classList.remove('active');
            testimonials[currentTestimonial].style.display = 'none';
            
            currentTestimonial = (currentTestimonial + 1) % testimonials.length;
            
            testimonials[currentTestimonial].classList.add('active');
            testimonials[currentTestimonial].style.display = 'block';
        }, 5000);
    }
    
    // ===== EFECTOS HOVER MEJORADOS =====
    const buttons = document.querySelectorAll('.btn-hero-primary, .btn-hero-secondary, .btn-form, .portfolio-link');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // ===== EFECTOS ESPECIALES EN TARJETAS =====
    const servicioCards = document.querySelectorAll('.servicio-card');
    servicioCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Efecto de inclinación muy sutil
            this.style.transform = 'translateY(-5px) rotateX(5deg) rotateY(2deg)';
            this.style.transformStyle = 'preserve-3d';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    const proyectoCards = document.querySelectorAll('.proyecto-card');
    proyectoCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Efecto de zoom y rotación muy sutil
            this.style.transform = 'translateY(-5px) scale(1.02) rotateZ(1deg)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // ===== CONTADOR DE ESTADÍSTICAS =====
    const statNumbers = document.querySelectorAll('.stat-number');
    const countObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const finalNumber = parseInt(target.textContent.replace(/\D/g, ''));
                const suffix = target.textContent.replace(/\d/g, '');
                
                if (finalNumber > 0) {
                    let currentNumber = 0;
                    const increment = Math.ceil(finalNumber / 50);
                    
                    const counter = setInterval(() => {
                        currentNumber += increment;
                        if (currentNumber >= finalNumber) {
                            currentNumber = finalNumber;
                            clearInterval(counter);
                        }
                        target.textContent = currentNumber + suffix;
                        
                        // Efecto de pulso durante el conteo
                        target.style.transform = 'scale(1.05)';
                        setTimeout(() => {
                            target.style.transform = 'scale(1)';
                        }, 100);
                    }, 30);
                }
                
                countObserver.unobserve(target);
            }
        });
    }, { threshold: 0.5 });
    
    statNumbers.forEach(stat => {
        stat.style.transition = 'transform 0.1s ease';
        countObserver.observe(stat);
    });
    
    // ===== EFECTOS DE SCROLL SUAVES =====
    window.addEventListener('scroll', function() {
        const scrollPercent = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
        
        // Cambio muy sutil en la opacidad de elementos
        const sections = document.querySelectorAll('.servicios, .proyectos, .stats, .testimonials, .contacto');
        sections.forEach((section, index) => {
            const rect = section.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
            
            if (isVisible) {
                const opacity = Math.max(0.8, 1 - Math.abs(rect.top) / window.innerHeight);
                section.style.opacity = opacity;
            }
        });
    });
    
    console.log('✅ Megadominio.co cargado con efectos de movimiento');
}); 
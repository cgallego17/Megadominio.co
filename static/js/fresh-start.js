// JavaScript limpio para Megadominio.co - Nuevo comienzo
document.addEventListener('DOMContentLoaded', function() {
    
    console.log('🚀 Megadominio.co - Nuevo comienzo cargado');
    
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
    
    // ===== HEADER DINÁMICO =====
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
    
    // ===== EFECTOS SUAVES EN EL HERO =====
    const hero = document.querySelector('.hero');
    const heroContent = document.querySelector('.hero-content');
    const heroVisual = document.querySelector('.hero-visual');
    
    if (hero && heroContent && heroVisual) {
        // Efecto de mouse muy sutil en el hero
        hero.addEventListener('mousemove', function(e) {
            const rect = hero.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const deltaX = (x - centerX) / centerX;
            const deltaY = (y - centerY) / centerY;
            
            // Movimiento muy sutil del contenido
            const moveX = deltaX * 5;
            const moveY = deltaY * 5;
            
            heroContent.style.transform = `translate(${moveX * 0.3}px, ${moveY * 0.3}px)`;
            heroVisual.style.transform = `translate(${moveX * -0.2}px, ${moveY * -0.2}px)`;
        });
        
        hero.addEventListener('mouseleave', function() {
            heroContent.style.transform = '';
            heroVisual.style.transform = '';
        });
    }
    
    // ===== EFECTOS HOVER MEJORADOS =====
    const buttons = document.querySelectorAll('.btn-hero-primary, .btn-hero-secondary');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // ===== OBSERVADOR PARA ANIMACIONES DE ENTRADA =====
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Preparar elementos para animaciones futuras
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'all 0.8s ease-out';
        observer.observe(section);
    });
    
    // ===== UTILIDADES GENERALES =====
    
    // Función para animar elementos cuando entran en vista
    function animateOnScroll(selector, animationClass = 'fade-in') {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'all 0.6s ease-out';
            observer.observe(element);
        });
    }
    
    // Función para efectos de hover personalizados
    function addHoverEffect(selector, hoverTransform = 'translateY(-5px)') {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.addEventListener('mouseenter', function() {
                this.style.transform = hoverTransform;
            });
            
            element.addEventListener('mouseleave', function() {
                this.style.transform = '';
            });
        });
    }
    
    // Función para parallax suave
    function addParallax(selector, speed = 0.1) {
        const elements = document.querySelectorAll(selector);
        
        window.addEventListener('scroll', function() {
            const scrollY = window.scrollY;
            
            elements.forEach(element => {
                const yPos = scrollY * speed;
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }
    
    // Función para contador animado
    function animateCounter(selector, duration = 2000) {
        const counters = document.querySelectorAll(selector);
        
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    const finalNumber = parseInt(target.textContent.replace(/\D/g, ''));
                    const suffix = target.textContent.replace(/\d/g, '');
                    
                    if (finalNumber > 0) {
                        let currentNumber = 0;
                        const increment = Math.ceil(finalNumber / (duration / 30));
                        
                        const counter = setInterval(() => {
                            currentNumber += increment;
                            if (currentNumber >= finalNumber) {
                                currentNumber = finalNumber;
                                clearInterval(counter);
                            }
                            target.textContent = currentNumber + suffix;
                        }, 30);
                    }
                    
                    counterObserver.unobserve(target);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => counterObserver.observe(counter));
    }
    
    // ===== FUNCIONES PÚBLICAS PARA USAR EN NUEVAS SECCIONES =====
    
    // Exponer funciones útiles globalmente para facilitar el desarrollo
    window.MegadominionUtils = {
        animateOnScroll,
        addHoverEffect,
        addParallax,
        animateCounter,
        observer,
        observerOptions
    };
    
    console.log('✨ Utilidades disponibles: window.MegadominionUtils');
    console.log('📖 Ejemplo: MegadominionUtils.animateOnScroll(".mi-elemento")');
    
    // ===== EFECTO MATRIX RAIN =====
    function createMatrixRain() {
        const matrixContainer = document.createElement('div');
        matrixContainer.className = 'matrix-rain';
        document.body.appendChild(matrixContainer);
        
        const matrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*(){}[]<>?/|\\+=~`';
        const columns = Math.floor(window.innerWidth / 30);
        
        function createColumn() {
            const column = document.createElement('div');
            column.className = 'matrix-column';
            
            // Generar texto para la columna
            let text = '';
            const length = Math.floor(Math.random() * 15) + 8;
            for (let i = 0; i < length; i++) {
                text += matrixChars[Math.floor(Math.random() * matrixChars.length)];
                if (i < length - 1) text += '\n';
            }
            
            column.textContent = text;
            column.style.left = Math.random() * 100 + '%';
            column.style.animationDuration = (Math.random() * 4 + 3) + 's';
            column.style.animationDelay = Math.random() * 3 + 's';
            column.style.fontSize = (Math.random() * 8 + 12) + 'px';
            
            matrixContainer.appendChild(column);
            
            // Remover columna después de la animación
            setTimeout(() => {
                if (column.parentNode) {
                    column.parentNode.removeChild(column);
                }
            }, 7000);
        }
        
        // Crear columnas iniciales
        for (let i = 0; i < Math.min(columns, 12); i++) {
            setTimeout(createColumn, i * 300);
        }
        
        // Crear columnas continuamente
        setInterval(() => {
            if (Math.random() < 0.6) {
                createColumn();
            }
        }, 1200);
    }
    
    // Iniciar efecto Matrix después de cargar la página
    setTimeout(createMatrixRain, 2000);
    
    // ===== EFECTOS DE SISTEMAS TECNOLÓGICOS =====
    function createSystemElements() {
        const systemContainer = document.createElement('div');
        systemContainer.className = 'system-elements';
        systemContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            overflow: hidden;
        `;
        document.body.appendChild(systemContainer);
        
                 // Crear nodos de conexión tecnológicos
         function createNode() {
             const node = document.createElement('div');
             node.className = 'tech-node';
             const isOrange = Math.random() > 0.5;
             node.style.cssText = `
                 position: absolute;
                 width: 4px;
                 height: 4px;
                 background: ${isOrange ? 'rgba(255, 102, 0, 0.7)' : 'rgba(0, 150, 255, 0.6)'};
                 border-radius: 50%;
                 box-shadow: 0 0 12px ${isOrange ? 'rgba(255, 102, 0, 0.4)' : 'rgba(0, 150, 255, 0.3)'};
                 animation: techFloat 12s ease-in-out infinite;
             `;
             
             node.style.left = Math.random() * 100 + '%';
             node.style.top = Math.random() * 100 + '%';
             node.style.animationDelay = Math.random() * 5 + 's';
             
             systemContainer.appendChild(node);
             
             setTimeout(() => {
                 if (node.parentNode) {
                     node.parentNode.removeChild(node);
                 }
             }, 15000);
         }
         
         // Crear líneas de conexión dinámicas
         function createConnectionLine() {
             const line = document.createElement('div');
             line.className = 'connection-line';
             const isHorizontal = Math.random() > 0.5;
             line.style.cssText = `
                 position: absolute;
                 background: linear-gradient(${isHorizontal ? '90deg' : '0deg'}, 
                     transparent 0%, 
                     rgba(255, 102, 0, 0.3) 50%, 
                     transparent 100%);
                 ${isHorizontal ? 'width: 100px; height: 1px;' : 'width: 1px; height: 80px;'}
                 animation: lineFlow 8s linear infinite;
             `;
             
             line.style.left = Math.random() * 90 + '%';
             line.style.top = Math.random() * 90 + '%';
             line.style.animationDelay = Math.random() * 3 + 's';
             
             systemContainer.appendChild(line);
             
             setTimeout(() => {
                 if (line.parentNode) {
                     line.parentNode.removeChild(line);
                 }
             }, 10000);
         }
         
         // Crear elementos de circuito
         function createCircuitElement() {
             const circuit = document.createElement('div');
             circuit.className = 'circuit-element';
             const symbols = ['◢', '◣', '◤', '◥', '○', '□', '◊'];
             circuit.textContent = symbols[Math.floor(Math.random() * symbols.length)];
             circuit.style.cssText = `
                 position: absolute;
                 color: rgba(0, 150, 255, 0.4);
                 font-size: ${Math.random() * 6 + 8}px;
                 font-family: 'Courier New', monospace;
                 animation: circuitPulse 10s ease-in-out infinite;
                 text-shadow: 0 0 8px rgba(0, 150, 255, 0.3);
             `;
             
             circuit.style.left = Math.random() * 95 + '%';
             circuit.style.top = Math.random() * 95 + '%';
             circuit.style.animationDelay = Math.random() * 5 + 's';
             
             systemContainer.appendChild(circuit);
             
             setTimeout(() => {
                 if (circuit.parentNode) {
                     circuit.parentNode.removeChild(circuit);
                 }
             }, 12000);
         }
        
        
        
                 // Crear indicadores de datos
         function createDataIndicator() {
             const indicator = document.createElement('div');
             const texts = ['[OK]', '[RUN]', '[SYS]', '[NET]', '[DATA]', '[CONN]'];
             indicator.textContent = texts[Math.floor(Math.random() * texts.length)];
             indicator.style.cssText = `
                 position: absolute;
                 color: rgba(120, 120, 120, 0.3);
                 font-family: 'Courier New', monospace;
                 font-size: 9px;
                 font-weight: bold;
                 animation: dataMove 20s linear infinite;
                 white-space: nowrap;
             `;
             
             indicator.style.left = Math.random() * 90 + '%';
             indicator.style.top = Math.random() * 90 + '%';
             indicator.style.animationDelay = Math.random() * 10 + 's';
             
             systemContainer.appendChild(indicator);
             
             setTimeout(() => {
                 if (indicator.parentNode) {
                     indicator.parentNode.removeChild(indicator);
                 }
             }, 25000);
         }
        
        // CSS para las animaciones tecnológicas
        const techStyles = document.createElement('style');
        techStyles.textContent = `
            @keyframes techFloat {
                0%, 100% { 
                    transform: translateY(0px) scale(1);
                    opacity: 0.7;
                }
                25% { 
                    transform: translateY(-15px) scale(1.1);
                    opacity: 1;
                }
                50% { 
                    transform: translateY(-8px) scale(0.9);
                    opacity: 0.9;
                }
                75% { 
                    transform: translateY(-18px) scale(1.05);
                    opacity: 1;
                }
            }
            
            @keyframes lineFlow {
                0% { 
                    opacity: 0;
                    transform: scale(0.5);
                }
                20% { 
                    opacity: 0.8;
                    transform: scale(1);
                }
                80% { 
                    opacity: 0.8;
                    transform: scale(1);
                }
                100% { 
                    opacity: 0;
                    transform: scale(0.5);
                }
            }
            
            @keyframes circuitPulse {
                0%, 100% { 
                    opacity: 0.4;
                    transform: scale(1) rotate(0deg);
                }
                25% { 
                    opacity: 0.8;
                    transform: scale(1.1) rotate(90deg);
                }
                50% { 
                    opacity: 0.6;
                    transform: scale(0.9) rotate(180deg);
                }
                75% { 
                    opacity: 0.9;
                    transform: scale(1.05) rotate(270deg);
                }
            }
            
            @keyframes dataMove {
                0% { 
                    transform: translateX(0px);
                    opacity: 0;
                }
                10% { 
                    opacity: 0.3;
                }
                90% { 
                    opacity: 0.3;
                }
                100% { 
                    transform: translateX(150px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(techStyles);
        
                 // Generar elementos tecnológicos continuamente
         setInterval(() => {
             if (Math.random() < 0.2) createNode();
             if (Math.random() < 0.15) createConnectionLine();
             if (Math.random() < 0.1) createCircuitElement();
             if (Math.random() < 0.08) createDataIndicator();
         }, 2500);
    }
    
    // Iniciar efectos de sistemas
    setTimeout(createSystemElements, 3000);
    
    // ===== EFECTOS DE COPIA CONSOLA =====
    
    // Función para copiar contenido específico de línea
    function copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text).then(() => true).catch(() => false);
        } else {
            // Fallback para navegadores más antiguos
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                textArea.remove();
                return true;
            } catch (error) {
                textArea.remove();
                return false;
            }
        }
    }
    
    // Función para mostrar indicador de copia
    function showCopyIndicator(element) {
        const indicator = element.querySelector('.copy-indicator');
        if (indicator) {
            indicator.classList.add('show');
            setTimeout(() => {
                indicator.classList.remove('show');
            }, 2000);
        }
    }
    
    // Función principal para copiar todo el contenido de la consola
    window.copyConsoleContent = function() {
        const consoleContent = [
            "console.log('Megadominio iniciado...')",
            "✓ Sitios web modernos",
            "✓ Software personalizado", 
            "✓ Ecommerce avanzado",
            "✓ Hosting premium",
            "> Estado: ONLINE"
        ].join('\n');
        
        const success = copyToClipboard(consoleContent);
        const copyButton = document.querySelector('.copy-button');
        
        if (success) {
            // Efecto visual en el botón
            if (copyButton) {
                const originalContent = copyButton.innerHTML;
                copyButton.innerHTML = '<i class="fas fa-check"></i>';
                copyButton.style.background = 'rgba(0, 255, 102, 0.2)';
                copyButton.style.borderColor = 'rgba(0, 255, 102, 0.5)';
                copyButton.style.color = '#00ff66';
                
                setTimeout(() => {
                    copyButton.innerHTML = originalContent;
                    copyButton.style.background = '';
                    copyButton.style.borderColor = '';
                    copyButton.style.color = '';
                }, 1500);
            }
        }
    };
    
    // Añadir eventos a líneas copiables individuales
    const copyableLines = document.querySelectorAll('.copyable-line');
    copyableLines.forEach((line, index) => {
        line.addEventListener('click', function(e) {
            e.preventDefault();
            const textToCopy = this.getAttribute('data-copy');
            
            if (textToCopy) {
                const success = copyToClipboard(textToCopy);
                
                if (success) {
                    showCopyIndicator(this);
                    
                    // Efecto de pulso en la línea
                    this.style.animation = 'copyLinePulse 0.6s ease-out';
                    setTimeout(() => {
                        this.style.animation = '';
                    }, 600);
                }
            }
        });
        
        // Efecto de typing al hacer hover (solo en la línea de consola)
        if (line.classList.contains('console-line')) {
            let typingTimeout;
            
            line.addEventListener('mouseenter', function() {
                clearTimeout(typingTimeout);
                const terminalIcon = this.querySelector('.fas.fa-terminal');
                if (terminalIcon) {
                    terminalIcon.style.animation = 'terminalBlink 1s ease-in-out infinite';
                }
            });
            
            line.addEventListener('mouseleave', function() {
                const terminalIcon = this.querySelector('.fas.fa-terminal');
                if (terminalIcon) {
                    terminalIcon.style.animation = '';
                }
            });
        }
    });
    
    // Añadir estilos CSS dinámicos para animaciones adicionales
    const additionalStyles = document.createElement('style');
    additionalStyles.textContent = `
        @keyframes copyLinePulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); box-shadow: 0 0 20px rgba(255, 102, 0, 0.4); }
            100% { transform: scale(1); }
        }
        
        @keyframes terminalBlink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .copyable-line:hover {
            position: relative;
            z-index: 10;
        }
        
        .copy-button {
            position: relative;
            z-index: 20;
        }
    `;
    document.head.appendChild(additionalStyles);
    
    console.log('✅ Efectos de copia de consola activados');
}); 
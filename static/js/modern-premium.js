// NAVEGACIÓN SUAVE Y ACTIVA
document.addEventListener('DOMContentLoaded', function() {
    // Navegación suave
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Navegación activa basada en scroll
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    function updateActiveNav() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', updateActiveNav);

    // EFECTO DE ESCRITURA DE CÓDIGO Y TRANSFORMACIÓN
    function initCodeTypewriter() {
        const services = [
            {
                name: 'Páginas Web',
                loadingText: '🌐 Creando página web...',
                commands: [
                    '> crear_sitio.py',
                    '> html = estructura()',
                    '> css = diseño_moderno()',
                    '> responsive = true',
                    '> deploy_web()',
                    '> ¡sitio_listo! ✅'
                ],
                steps: [
                    { icon: '⚙️', text: 'Configurando estructura...' },
                    { icon: '🎨', text: 'Aplicando diseño moderno...' },
                    { icon: '📱', text: 'Optimizando responsive...' },
                    { icon: '✅', text: '¡Página web lista!' }
                ],
                website: {
                    logo: '🌐 MiWeb',
                    title: '¡Tu Página Web Lista!',
                    subtitle: 'Diseño moderno y profesional',
                    items: [
                        { icon: '🏠', name: 'Inicio', desc: 'Página principal' },
                        { icon: '📋', name: 'Servicios', desc: 'Nuestros servicios' },
                        { icon: '📞', name: 'Contacto', desc: 'Contáctanos' }
                    ],
                    cta: '🌐 Ver Sitio'
                }
            },
            {
                name: 'Ecommerce',
                loadingText: '🛒 Creando tienda online...',
                commands: [
                    '> crear_tienda.py',
                    '> productos = cargar()',
                    '> carrito = activar()',
                    '> pagos = stripe_api()',
                    '> deploy_shop()',
                    '> ¡tienda_activa! ✅'
                ],
                steps: [
                    { icon: '🏪', text: 'Configurando tienda...' },
                    { icon: '📦', text: 'Cargando productos...' },
                    { icon: '💳', text: 'Integrando pagos...' },
                    { icon: '✅', text: '¡Tienda lista!' }
                ],
                website: {
                    logo: '🛒 TiendaOnline',
                    title: '¡Tu Tienda Online Lista!',
                    subtitle: 'Vende tus productos al mundo',
                    items: [
                        { icon: '📱', name: 'iPhone 15', desc: '$899' },
                        { icon: '💻', name: 'MacBook Pro', desc: '$1,299' },
                        { icon: '⌚', name: 'Apple Watch', desc: '$399' }
                    ],
                    cta: '🛒 Comprar Ahora'
                }
            },
            {
                name: 'Software a la Medida',
                loadingText: '⚙️ Desarrollando software...',
                commands: [
                    '> analizar_requisitos()',
                    '> backend = django()',
                    '> frontend = react()',
                    '> database = postgresql()',
                    '> testing = pytest()',
                    '> ¡software_listo! ✅'
                ],
                steps: [
                    { icon: '💻', text: 'Analizando requisitos...' },
                    { icon: '🔧', text: 'Programando lógica...' },
                    { icon: '🧪', text: 'Ejecutando pruebas...' },
                    { icon: '✅', text: '¡Software listo!' }
                ],
                website: {
                    logo: '⚙️ MiSoftware',
                    title: '¡Software Personalizado!',
                    subtitle: 'Solución hecha a tu medida',
                    items: [
                        { icon: '📊', name: 'Dashboard', desc: 'Panel de control' },
                        { icon: '👥', name: 'Usuarios', desc: 'Gestión de usuarios' },
                        { icon: '📈', name: 'Reportes', desc: 'Análisis de datos' }
                    ],
                    cta: '⚙️ Usar Software'
                }
            },
            {
                name: 'WordPress',
                loadingText: '📝 Creando sitio WordPress...',
                commands: [
                    '> install_wordpress()',
                    '> theme = premium()',
                    '> plugins = instalar()',
                    '> content = crear()',
                    '> seo = optimizar()',
                    '> ¡wordpress_listo! ✅'
                ],
                steps: [
                    { icon: '📝', text: 'Instalando WordPress...' },
                    { icon: '🎨', text: 'Configurando tema...' },
                    { icon: '🔌', text: 'Instalando plugins...' },
                    { icon: '✅', text: '¡WordPress listo!' }
                ],
                website: {
                    logo: '📝 MiBlog',
                    title: '¡Tu Blog WordPress Listo!',
                    subtitle: 'Comparte tu contenido con el mundo',
                    items: [
                        { icon: '📄', name: 'Mi primer post', desc: 'Hace 2 días' },
                        { icon: '📸', name: 'Galería de fotos', desc: 'Hace 5 días' },
                        { icon: '💬', name: 'Sobre nosotros', desc: 'Hace 1 semana' }
                    ],
                    cta: '📝 Leer Blog'
                }
            },
            {
                name: 'WooCommerce',
                loadingText: '🛍️ Creando tienda WooCommerce...',
                commands: [
                    '> install_woocommerce()',
                    '> payment = paypal()',
                    '> shipping = config()',
                    '> products = import()',
                    '> taxes = setup()',
                    '> ¡woo_activo! ✅'
                ],
                steps: [
                    { icon: '🛍️', text: 'Configurando WooCommerce...' },
                    { icon: '💳', text: 'Integrando pagos...' },
                    { icon: '📦', text: 'Configurando envíos...' },
                    { icon: '✅', text: '¡WooCommerce listo!' }
                ],
                website: {
                    logo: '🛍️ WooShop',
                    title: '¡Tu Tienda WooCommerce!',
                    subtitle: 'Potente tienda con WordPress',
                    items: [
                        { icon: '👕', name: 'Camiseta', desc: '$25' },
                        { icon: '👟', name: 'Zapatillas', desc: '$89' },
                        { icon: '🎒', name: 'Mochila', desc: '$45' }
                    ],
                    cta: '🛍️ Comprar'
                }
            },
            {
                name: 'Correos Corporativos',
                loadingText: '📧 Configurando correos...',
                commands: [
                    '> server = mail_config()',
                    '> ssl = security()',
                    '> accounts = create()',
                    '> spam = filter()',
                    '> backup = enable()',
                    '> ¡correos_activos! ✅'
                ],
                steps: [
                    { icon: '📧', text: 'Configurando servidor...' },
                    { icon: '🔐', text: 'Aplicando seguridad...' },
                    { icon: '👥', text: 'Creando cuentas...' },
                    { icon: '✅', text: '¡Correos listos!' }
                ],
                website: {
                    logo: '📧 MiCorreo',
                    title: '¡Correos Corporativos!',
                    subtitle: 'Comunicación profesional',
                    items: [
                        { icon: '📨', name: 'admin@empresa.com', desc: 'Administrador' },
                        { icon: '💼', name: 'ventas@empresa.com', desc: 'Departamento ventas' },
                        { icon: '🛠️', name: 'soporte@empresa.com', desc: 'Soporte técnico' }
                    ],
                    cta: '📧 Abrir Email'
                }
            },
            {
                name: 'Hosting',
                loadingText: '🌐 Configurando hosting...',
                commands: [
                    '> server = provision()',
                    '> ssl = letsencrypt()',
                    '> cache = redis()',
                    '> backup = daily()',
                    '> monitor = uptime()',
                    '> ¡hosting_activo! ✅'
                ],
                steps: [
                    { icon: '🖥️', text: 'Preparando servidor...' },
                    { icon: '🔒', text: 'Configurando SSL...' },
                    { icon: '⚡', text: 'Optimizando velocidad...' },
                    { icon: '✅', text: '¡Hosting listo!' }
                ],
                website: {
                    logo: '🌐 MiHosting',
                    title: '¡Hosting Configurado!',
                    subtitle: 'Servidor rápido y seguro',
                    items: [
                        { icon: '⚡', name: 'Velocidad', desc: '99.9% uptime' },
                        { icon: '🔒', name: 'Seguridad', desc: 'SSL incluido' },
                        { icon: '📊', name: 'Panel', desc: 'Control total' }
                    ],
                    cta: '🌐 Ver Panel'
                }
            },
            {
                name: 'Dominios',
                loadingText: '🔗 Registrando dominio...',
                commands: [
                    '> check_availability()',
                    '> register_domain()',
                    '> dns = configure()',
                    '> whois = protect()',
                    '> redirect = setup()',
                    '> ¡dominio_activo! ✅'
                ],
                steps: [
                    { icon: '🔍', text: 'Verificando disponibilidad...' },
                    { icon: '📝', text: 'Registrando dominio...' },
                    { icon: '🌐', text: 'Configurando DNS...' },
                    { icon: '✅', text: '¡Dominio listo!' }
                ],
                website: {
                    logo: '🔗 MiDominio',
                    title: '¡Dominio Registrado!',
                    subtitle: 'Tu marca en internet',
                    items: [
                        { icon: '🌐', name: 'miempresa.com', desc: 'Dominio principal' },
                        { icon: '📧', name: 'DNS configurado', desc: 'Correos activos' },
                        { icon: '🔒', name: 'Protección WHOIS', desc: 'Privacidad incluida' }
                    ],
                    cta: '🔗 Ver Dominio'
                }
            },
            {
                name: 'SSL',
                loadingText: '🔒 Instalando certificado SSL...',
                commands: [
                    '> generate_csr()',
                    '> ssl = certificate()',
                    '> install_cert()',
                    '> force_https()',
                    '> verify_ssl()',
                    '> ¡ssl_seguro! ✅'
                ],
                steps: [
                    { icon: '🔐', text: 'Generando certificado...' },
                    { icon: '🔒', text: 'Instalando SSL...' },
                    { icon: '✅', text: 'Verificando seguridad...' },
                    { icon: '🛡️', text: '¡SSL activo!' }
                ],
                website: {
                    logo: '🔒 SitioSeguro',
                    title: '¡Certificado SSL Activo!',
                    subtitle: 'Tu sitio web está protegido',
                    items: [
                        { icon: '🔒', name: 'HTTPS activo', desc: 'Conexión segura' },
                        { icon: '🛡️', name: 'Datos protegidos', desc: 'Encriptación 256-bit' },
                        { icon: '✅', name: 'Confianza', desc: 'Certificado válido' }
                    ],
                    cta: '🔒 Ver Certificado'
                }
            }
        ];

        let currentServiceIndex = 0;
        let currentChar = 0;
        let terminalChar = 0;
        let consoleIndex = 0;

        function getCurrentService() {
            return services[currentServiceIndex];
        }

        function typeCode() {
            const lineElement = document.getElementById('code-line-1');
            const cursor = document.getElementById('code-cursor');
            
            if (!lineElement) return;

            const currentService = getCurrentService();
            const currentText = currentService.loadingText;
            const displayText = currentText.substring(0, currentChar);
            
            // Aplicar resaltado de sintaxis
            lineElement.innerHTML = `<span class="comentario">${displayText}</span>`;
            
            // Posicionar cursor
            if (cursor) {
                const rect = lineElement.getBoundingClientRect();
                const cardRect = lineElement.closest('.card-content').getBoundingClientRect();
                cursor.style.left = (rect.right - cardRect.left) + 'px';
                cursor.style.top = (rect.top - cardRect.top + 2) + 'px';
                cursor.style.opacity = '1';
            }

            currentChar++;

            if (currentChar > currentText.length) {
                // Esperar menos tiempo antes de mostrar terminal
                setTimeout(() => {
                    startTerminalHeader();
                }, 300); // Reducido de 500ms a 300ms
                return;
            } else {
                // Velocidad de escritura más rápida
                const delay = Math.random() * 8 + 3; // ULTRA RÁPIDO
                setTimeout(typeCode, delay);
            }
        }

        function startTerminalHeader() {
            const cursor = document.getElementById('code-cursor');
            if (cursor) cursor.style.opacity = '0';
            
            typeTerminalHeader();
        }

        function typeTerminalHeader() {
            const lineElement = document.getElementById('code-line-2');
            const terminalHeader = '🖥️ terminal';
            
            if (!lineElement) return;

            const displayText = terminalHeader.substring(0, terminalChar);
            lineElement.innerHTML = `<span class="terminal-header">${displayText}</span>`;

            terminalChar++;

            if (terminalChar > terminalHeader.length) {
                // Terminal header completo, esperar menos tiempo
                setTimeout(() => {
                    startConsoleInLines();
                }, 400); // Reducido de 600ms a 400ms
                return;
            } else {
                // Velocidad de escritura más rápida para terminal
                const delay = Math.random() * 5 + 2; // ULTRA RÁPIDO
                setTimeout(typeTerminalHeader, delay);
            }
        }

        function startConsoleInLines() {
            // Ejecutar comandos de consola en las líneas 3-8
            executeConsoleCommands();
        }

        function executeConsoleCommands() {
            const currentService = getCurrentService();
            const consoleCommands = currentService.commands; // Usar comandos específicos del servicio

            if (consoleIndex >= consoleCommands.length) {
                // Todos los comandos ejecutados, hacer efecto de ventana más rápido
                setTimeout(() => {
                    windowSlideEffect();
                }, 500); // Reducido de 800ms a 500ms
                return;
            }

            // Usar líneas 3-8 para mostrar comandos de consola
            const lineNumber = consoleIndex + 3;
            const lineElement = document.getElementById(`code-line-${lineNumber}`);
            
            if (lineElement) {
                const command = consoleCommands[consoleIndex];
                
                // Efecto de escritura carácter por carácter más rápido
                let charIndex = 0;
                const typeCommand = () => {
                    if (charIndex <= command.length) {
                        const partialCommand = command.substring(0, charIndex);
                        lineElement.innerHTML = `<span class="console-command">${partialCommand}<span class="typing-cursor">|</span></span>`;
                        charIndex++;
                        setTimeout(typeCommand, 5); // ULTRA RÁPIDO
                    } else {
                        // Comando completo, remover cursor y agregar efecto de completado
                        lineElement.innerHTML = `<span class="console-command">${command}</span>`;
                        lineElement.classList.add('command-completed');
                        
                        // Scroll automático suave hacia la línea actual
                        scrollToActiveLine(lineElement);
                        
                        // Efecto de highlight temporal más rápido
                        setTimeout(() => {
                            lineElement.classList.add('command-highlight');
                            setTimeout(() => {
                                lineElement.classList.remove('command-highlight');
                            }, 500); // Reducido de 800ms a 500ms
                        }, 100); // Reducido de 200ms a 100ms
                    }
                };
                
                // Añadir efecto de aparición inicial más rápido
                lineElement.style.opacity = '0';
                lineElement.style.transform = 'translateX(-20px)';
                lineElement.style.transition = 'all 0.2s ease-out'; // Reducido de 0.3s a 0.2s
                
                setTimeout(() => {
                    lineElement.style.opacity = '1';
                    lineElement.style.transform = 'translateX(0)';
                    
                    // Iniciar escritura más rápido después de la animación
                    setTimeout(typeCommand, 20); // ULTRA RÁPIDO
                }, 50); // Reducido de 100ms a 50ms
            }

            consoleIndex++;
            
            // Pausa más corta entre comandos
            setTimeout(executeConsoleCommands, 100); // ULTRA RÁPIDO
        }

        function scrollToActiveLine(element) {
            const cardContent = element.closest('.card-content');
            if (cardContent) {
                const elementTop = element.offsetTop;
                const elementHeight = element.offsetHeight;
                const containerHeight = cardContent.offsetHeight;
                const containerScrollTop = cardContent.scrollTop;
                
                // Calcular posición ideal (centrar el elemento)
                const idealScrollTop = elementTop - (containerHeight / 2) + (elementHeight / 2);
                
                // Scroll más rápido
                smoothScrollTo(cardContent, idealScrollTop, 400); // Reducido de 600ms a 400ms
                
                // Efecto de pulso más rápido en el contenedor
                cardContent.classList.add('scrolling-active');
                setTimeout(() => {
                    cardContent.classList.remove('scrolling-active');
                }, 400); // Reducido de 600ms a 400ms
            }
        }

        function smoothScrollTo(element, targetScrollTop, duration) {
            const startScrollTop = element.scrollTop;
            const distance = targetScrollTop - startScrollTop;
            const startTime = performance.now();

            function animation(currentTime) {
                const timeElapsed = currentTime - startTime;
                const progress = Math.min(timeElapsed / duration, 1);
                
                // Easing function (ease-in-out)
                const easeInOut = progress < 0.5 
                    ? 2 * progress * progress 
                    : 1 - Math.pow(-2 * progress + 2, 3) / 2;
                
                element.scrollTop = startScrollTop + (distance * easeInOut);
                
                if (progress < 1) {
                    requestAnimationFrame(animation);
                }
            }
            
            requestAnimationFrame(animation);
        }

        function animateProgress() {
            const progressFill = document.getElementById('progress-fill');
            const progressText = document.getElementById('progress-text');
            const currentService = getCurrentService();
            const steps = currentService.steps.map((step, index) => ({
                id: `step-${index + 1}`,
                delay: 20 + (index * 100) // ULTRA RÁPIDO
            }));

            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += 5; // ULTRA RÁPIDO
                progressFill.style.width = progress + '%';
                progressText.textContent = Math.round(progress) + '%';

                if (progress >= 100) {
                    clearInterval(progressInterval);
                    // Efecto final de completado
                    progressText.innerHTML = '100% <span style="color: #00ff88;">✅</span>';
                }
            }, 8); // ULTRA RÁPIDO

            // Activar pasos más rápido
            steps.forEach((step, index) => {
                setTimeout(() => {
                    const stepElement = document.getElementById(step.id);
                    if (stepElement) {
                        stepElement.classList.add('step-active');
                        
                        // Scroll automático a cada paso activo
                        scrollToActiveStep(stepElement);
                        
                        // Efecto de ondas cuando se activa
                        createRippleEffect(stepElement);
                    }
                }, step.delay);
            });
        }

        function scrollToActiveStep(element) {
            const stepsContainer = element.closest('.loading-steps');
            if (stepsContainer) {
                const elementTop = element.offsetTop;
                const elementHeight = element.offsetHeight;
                const containerHeight = stepsContainer.offsetHeight;
                
                // Calcular posición para centrar el elemento
                const targetScroll = elementTop - (containerHeight / 2) + (elementHeight / 2);
                
                // Scroll súper rápido
                smoothScrollTo(stepsContainer, Math.max(0, targetScroll), 50); // ULTRA RÁPIDO
            }
        }

        function createRippleEffect(element) {
            const ripple = document.createElement('div');
            ripple.className = 'step-ripple';
            element.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 1000);
        }

        function windowSlideEffect() {
            const heroCard = document.querySelector('.hero-card');
            
            // Efecto de ventana más rápido
            heroCard.style.transform = 'translateY(-100%)';
            heroCard.style.transition = 'transform 0.1s ease-in-out'; // ULTRA RÁPIDO
            
            setTimeout(() => {
                // Mostrar efecto de carga mientras está fuera de vista
                showLoadingEffect();
                
                // Traer de vuelta la ventana más rápido
                setTimeout(() => {
                    heroCard.style.transform = 'translateY(100%)';
                    
                    setTimeout(() => {
                        heroCard.style.transform = 'translateY(0)';
                        
                        // Tiempo de carga reducido
                        setTimeout(() => {
                            transformToWebsite();
                            
                            // Tiempo de visualización reducido
                            setTimeout(() => {
                                resetToCode();
                            }, 600); // ULTRA RÁPIDO
                        }, 400); // ULTRA RÁPIDO
                                          }, 5); // ULTRA RÁPIDO
                  }, 10); // ULTRA RÁPIDO
                
            }, 100); // ULTRA RÁPIDO
        }

        function showLoadingEffect() {
            const cardContent = document.querySelector('.card-content');
            const currentService = getCurrentService();
            
            // Crear efecto de carga específico para el servicio
            const stepsHTML = currentService.steps.map((step, index) => 
                `<div class="loading-step" id="step-${index + 1}">
                    <span class="step-icon">${step.icon}</span>
                    <span class="step-text">${step.text}</span>
                </div>`
            ).join('');

            cardContent.innerHTML = `
                <div class="loading-container">
                    <div class="loading-header">
                        <div class="loading-title">${currentService.loadingText}</div>
                    </div>
                    <div class="loading-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                        <div class="progress-text" id="progress-text">0%</div>
                    </div>
                    <div class="loading-steps">
                        ${stepsHTML}
                    </div>
                </div>
            `;

            // Iniciar animación de progreso
            animateProgress();
        }

        function transformToWebsite() {
            const cardContent = document.querySelector('.card-content');
            const currentService = getCurrentService();
            const website = currentService.website;
            
            // Efecto de transición más rápido
            cardContent.style.opacity = '0';
            cardContent.style.transform = 'scale(0.9)';
            cardContent.style.transition = 'all 0.05s ease-out'; // ULTRA RÁPIDO
            
            setTimeout(() => {
                // Crear contenido específico del servicio
                const itemsHTML = website.items.map(item => 
                    `<div class="service-item">
                        <div class="service-item-icon">${item.icon}</div>
                        <div class="service-item-info">
                            <div class="service-item-name">${item.name}</div>
                            <div class="service-item-desc">${item.desc}</div>
                        </div>
                    </div>`
                ).join('');

                cardContent.innerHTML = `
                    <div class="website-header">
                        <div class="nav-bar">
                            <div class="logo">${website.logo}</div>
                            <div class="nav-items">
                                <span>Inicio</span>
                                <span>Servicios</span>
                                <span>Contacto</span>
                            </div>
                        </div>
                    </div>
                    <div class="website-content">
                        <div class="hero-section">
                            <h2>${website.title}</h2>
                            <p>${website.subtitle}</p>
                        </div>
                        <div class="services-grid">
                            ${itemsHTML}
                        </div>
                        <div class="website-footer">
                            <button class="cta-button">${website.cta}</button>
                        </div>
                    </div>
                `;

                // Animar la aparición del sitio web
                cardContent.style.opacity = '1';
                cardContent.style.transform = 'scale(1)';
                
                // Mostrar la página web generada
                codeContainer.style.display = 'none';
                webResult.style.display = 'block';
                webResult.innerHTML = webPages[currentService];
                
                                    // El contenido ahora se adapta sin necesidad de scroll
            }, 30); // ULTRA RÁPIDO
        }

        function resetToCode() {
            const heroCard = document.querySelector('.hero-card');
            
            // Efecto de ventana más rápido
            heroCard.style.transform = 'translateY(-100%)';
            
            setTimeout(() => {
                // Restaurar contenido de código
                const cardContent = document.querySelector('.card-content');
                cardContent.innerHTML = `
                    <div class="code-editor">
                        <div class="code-line-number">1</div>
                        <div class="code-text" id="code-line-1"></div>
                    </div>
                    <div class="code-editor">
                        <div class="code-line-number">2</div>
                        <div class="code-text" id="code-line-2"></div>
                    </div>
                    <div class="code-editor">
                        <div class="code-line-number">3</div>
                        <div class="code-text" id="code-line-3"></div>
                    </div>
                    <div class="code-editor">
                        <div class="code-line-number">4</div>
                        <div class="code-text" id="code-line-4"></div>
                    </div>
                    <div class="code-editor">
                        <div class="code-line-number">5</div>
                        <div class="code-text" id="code-line-5"></div>
                    </div>
                    <div class="code-editor">
                        <div class="code-line-number">6</div>
                        <div class="code-text" id="code-line-6"></div>
                    </div>
                    <div class="code-editor">
                        <div class="code-line-number">7</div>
                        <div class="code-text" id="code-line-7"></div>
                    </div>
                    <div class="code-editor">
                        <div class="code-line-number">8</div>
                        <div class="code-text" id="code-line-8"></div>
                    </div>
                    <div class="code-cursor" id="code-cursor">|</div>
                `;
                
                // Traer de vuelta la ventana más rápido
                setTimeout(() => {
                    heroCard.style.transform = 'translateY(100%)';
                    
                    setTimeout(() => {
                        heroCard.style.transform = 'translateY(0)';
                        
                        // Avanzar al siguiente servicio
                        currentServiceIndex = (currentServiceIndex + 1) % services.length;
                        
                        // Reiniciar el ciclo más rápido
                        currentChar = 0;
                        terminalChar = 0;
                        consoleIndex = 0;
                        setTimeout(typeCode, 50); // ULTRA RÁPIDO
                    }, 5); // ULTRA RÁPIDO
                }, 10); // ULTRA RÁPIDO
                
            }, 50); // ULTRA RÁPIDO
        }

        // Iniciar la escritura más rápido
        setTimeout(typeCode, 50); // ULTRA RÁPIDO
    }

    initCodeTypewriter();

    // EFECTOS PARALLAX AVANZADOS
    function initParallax() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        const particles = document.querySelectorAll('.particle[data-speed]');
        const sections = document.querySelectorAll('.servicios, .proyectos, .stats, .testimonials, .contacto');
        
        function updateParallax() {
            const scrolled = window.pageYOffset;
            const windowHeight = window.innerHeight;

            // Parallax para elementos con data-parallax
            parallaxElements.forEach(element => {
                const speed = element.dataset.parallax;
                const yPos = -(scrolled * speed);
                element.style.transform = `translate3d(0, ${yPos}px, 0)`;
            });

            // Parallax para partículas con velocidades diferentes
            particles.forEach(particle => {
                const speed = parseFloat(particle.dataset.speed);
                const yPos = scrolled * speed;
                const xPos = Math.sin(scrolled * 0.001) * 50;
                particle.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
            });

            // Parallax para todas las secciones
            sections.forEach(section => {
                const rect = section.getBoundingClientRect();
                const sectionTop = rect.top + scrolled;
                const sectionHeight = rect.height;
                
                // Calcular el offset de parallax basado en la posición del scroll
                const parallaxOffset = (scrolled - sectionTop + windowHeight) * 0.1;
                
                // Aplicar el offset como variable CSS
                section.style.setProperty('--parallax-offset', `${parallaxOffset}px`);
            });
        }

        // Usar requestAnimationFrame para mejor rendimiento
        let ticking = false;
        function requestTick() {
            if (!ticking) {
                requestAnimationFrame(updateParallax);
                ticking = true;
                setTimeout(() => ticking = false, 16); // 60fps
            }
        }

        window.addEventListener('scroll', requestTick);
        updateParallax(); // Ejecutar una vez al cargar
    }

    initParallax();

    // ANIMACIONES AL HACER SCROLL (AOS)
    function initScrollAnimations() {
        const animatedElements = document.querySelectorAll('[data-aos]');
        
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const animationType = element.dataset.aos;
                    const delay = element.dataset.aosDelay || 0;
                    
                    setTimeout(() => {
                        element.classList.add('aos-animate');
                        
                        // Aplicar animación específica
                        switch(animationType) {
                            case 'fade-up':
                                element.style.opacity = '1';
                                element.style.transform = 'translateY(0)';
                                break;
                            case 'zoom-in':
                                element.style.opacity = '1';
                                element.style.transform = 'scale(1)';
                                break;
                            case 'slide-left':
                                element.style.opacity = '1';
                                element.style.transform = 'translateX(0)';
                                break;
                        }
                    }, delay);
                    
                    observer.unobserve(element);
                }
            });
        }, observerOptions);

        animatedElements.forEach(element => {
            // Configurar estado inicial
            const animationType = element.dataset.aos;
            element.style.transition = 'all 0.6s ease';
            
            switch(animationType) {
                case 'fade-up':
                    element.style.opacity = '0';
                    element.style.transform = 'translateY(30px)';
                    break;
                case 'zoom-in':
                    element.style.opacity = '0';
                    element.style.transform = 'scale(0.8)';
                    break;
                case 'slide-left':
                    element.style.opacity = '0';
                    element.style.transform = 'translateX(-30px)';
                    break;
            }
            
            observer.observe(element);
        });
    }

    initScrollAnimations();

    // SLIDER DE TESTIMONIOS MEJORADO
    function initTestimonialSlider() {
        const testimonials = document.querySelectorAll('.testimonial-item');
        let currentIndex = 0;
        const totalTestimonials = testimonials.length;

        function showTestimonial(index) {
            testimonials.forEach((testimonial, i) => {
                testimonial.classList.remove('active');
                if (i === index) {
                    testimonial.classList.add('active');
                }
            });
        }

        function nextTestimonial() {
            currentIndex = (currentIndex + 1) % totalTestimonials;
            showTestimonial(currentIndex);
        }

        // Auto-reproducir cada 5 segundos
        setInterval(nextTestimonial, 5000);

        // Mostrar primer testimonio
        showTestimonial(0);
    }

    initTestimonialSlider();

    // EFECTOS DE PARTÍCULAS INTERACTIVAS
    function initInteractiveParticles() {
        const heroSection = document.querySelector('.hero-ultra');
        if (!heroSection) return;

        // Crear partículas adicionales en movimiento del mouse
        let mouseX = 0;
        let mouseY = 0;

        heroSection.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;

            // Crear partícula temporal
            const particle = document.createElement('div');
            particle.className = 'mouse-particle';
            particle.style.cssText = `
                position: fixed;
                width: 4px;
                height: 4px;
                background: rgba(255, 102, 0, 0.6);
                border-radius: 50%;
                pointer-events: none;
                z-index: 1000;
                left: ${mouseX}px;
                top: ${mouseY}px;
                animation: particle-fade 1s ease-out forwards;
            `;

            document.body.appendChild(particle);

            // Remover partícula después de la animación
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, 1000);
        });

        // Agregar CSS para la animación de partículas del mouse
        const style = document.createElement('style');
        style.textContent = `
            @keyframes particle-fade {
                0% { opacity: 1; transform: scale(1); }
                100% { opacity: 0; transform: scale(0) translateY(-20px); }
            }
        `;
        document.head.appendChild(style);
    }

    initInteractiveParticles();

    // CONTADOR ANIMADO PARA ESTADÍSTICAS
    function initCounterAnimation() {
        const counters = document.querySelectorAll('.stat-number');
        
        const observerOptions = {
            threshold: 0.5
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = counter.textContent;
                    const isPercent = target.includes('%');
                    const isRating = target.includes('★');
                    const isTime = target.includes('/');
                    
                    let endValue;
                    if (isPercent) {
                        endValue = parseInt(target);
                    } else if (isRating) {
                        endValue = 5;
                    } else if (isTime) {
                        endValue = 24;
                    } else {
                        endValue = parseInt(target);
                    }

                    animateCounter(counter, 0, endValue, 2000, target);
                    observer.unobserve(counter);
                }
            });
        }, observerOptions);

        counters.forEach(counter => observer.observe(counter));
    }

    function animateCounter(element, start, end, duration, originalText) {
        const startTime = performance.now();
        const isPercent = originalText.includes('%');
        const isRating = originalText.includes('★');
        const isTime = originalText.includes('/');

        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = Math.floor(start + (end - start) * progress);

            if (isPercent) {
                element.textContent = current + '%';
            } else if (isRating) {
                element.textContent = current + '★';
            } else if (isTime) {
                element.textContent = current + '/7';
            } else {
                element.textContent = current + '+';
            }

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        }

        requestAnimationFrame(updateCounter);
    }

    initCounterAnimation();

    // EFECTOS DE HOVER MEJORADOS PARA SERVICIOS
    function initServiceHoverEffects() {
        const serviceCards = document.querySelectorAll('.service-card');
        
        serviceCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                // Efecto de inclinación 3D
                this.style.transform = 'translateY(-10px) rotateX(5deg) rotateY(5deg)';
                this.style.transition = 'all 0.3s ease';
                
                // Efecto de brillo en el icono
                const icon = this.querySelector('.service-svg, .service-icon i');
                if (icon) {
                    icon.style.filter = 'brightness(1.2) drop-shadow(0 0 10px rgba(255, 102, 0, 0.5))';
                }
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) rotateX(0) rotateY(0)';
                
                const icon = this.querySelector('.service-svg, .service-icon i');
                if (icon) {
                    icon.style.filter = 'none';
                }
            });

            // Efecto de seguimiento del mouse
            card.addEventListener('mousemove', function(e) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;
                
                this.style.transform = `translateY(-10px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            });
        });
    }

    initServiceHoverEffects();

    // NAVEGACIÓN MÓVIL
    function initMobileNavigation() {
        // Crear hamburger menu si no existe
        const nav = document.querySelector('.nav');
        if (!document.querySelector('.hamburger')) {
            const hamburger = document.createElement('div');
            hamburger.className = 'hamburger';
            hamburger.innerHTML = '<span></span><span></span><span></span>';
            nav.appendChild(hamburger);
        }
        
        const hamburger = document.querySelector('.hamburger');
        const navMenu = document.querySelector('.nav-menu');
        
        if (hamburger && navMenu) {
            hamburger.addEventListener('click', () => {
                hamburger.classList.toggle('active');
                navMenu.classList.toggle('active');
                document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
            });
            
            // Cerrar menú al hacer click en un enlace
            const navLinks = document.querySelectorAll('.nav-menu a');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                    document.body.style.overflow = '';
                });
            });
            
            // Cerrar menú al redimensionar ventana
            window.addEventListener('resize', () => {
                if (window.innerWidth > 768) {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });
        }
    }
    
    // Ajustar code editor según el tamaño de pantalla
    function adjustCodeEditorSize() {
        const codeEditor = document.querySelector('.code-editor');
        if (!codeEditor) return;
        
        const width = window.innerWidth;
        
        if (width <= 767) {
            // Móvil
            codeEditor.style.width = '95%';
            codeEditor.style.maxWidth = '350px';
            codeEditor.style.height = '300px';
        } else if (width <= 1023) {
            // Tablet
            codeEditor.style.width = '80%';
            codeEditor.style.maxWidth = '450px';
            codeEditor.style.height = '350px';
        } else {
            // Desktop
            codeEditor.style.width = '550px';
            codeEditor.style.maxWidth = 'none';
            codeEditor.style.height = '400px';
        }
    }
    
    // Optimizar animaciones para móviles
    function optimizeAnimationsForMobile() {
        const isMobile = window.innerWidth <= 767;
        const particles = document.querySelectorAll('.particle');
        
        particles.forEach(particle => {
            if (isMobile) {
                // Reducir animaciones en móvil para mejor rendimiento
                particle.style.animationDuration = '8s';
                particle.style.opacity = '0.3';
            } else {
                // Restaurar animaciones completas en desktop
                particle.style.animationDuration = '6s';
                particle.style.opacity = '0.6';
            }
        });
    }
    
    // Ajustar velocidad de scroll automático según dispositivo
    function getScrollSpeed() {
        const width = window.innerWidth;
        if (width <= 767) return 1.5; // Más lento en móvil
        if (width <= 1023) return 2; // Medio en tablet
        return 2.5; // Normal en desktop
    }
    
    // Detectar orientación en móviles
    function handleOrientationChange() {
        if (window.innerWidth <= 767) {
            setTimeout(() => {
                adjustCodeEditorSize();
                optimizeAnimationsForMobile();
            }, 100);
        }
    }

    initMobileNavigation();

    // EFECTOS DE SCROLL EN LA NAVEGACIÓN
    function initNavScrollEffects() {
        const nav = document.querySelector('.modern-nav');
        let lastScrollY = window.scrollY;

        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > 100) {
                nav.style.background = 'rgba(255, 255, 255, 0.98)';
                nav.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
            } else {
                nav.style.background = 'rgba(255, 255, 255, 0.95)';
                nav.style.boxShadow = 'none';
            }

            // Ocultar/mostrar navegación en scroll
            if (currentScrollY > lastScrollY && currentScrollY > 200) {
                nav.style.transform = 'translateY(-100%)';
            } else {
                nav.style.transform = 'translateY(0)';
            }

            lastScrollY = currentScrollY;
        });
    }

    initNavScrollEffects();

    // CARGA PEREZOSA PARA IMÁGENES
    function initLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    initLazyLoading();

    // EFECTOS DE TEXTO MÁQUINA DE ESCRIBIR
    function initTypewriterEffect() {
        const typewriterElements = document.querySelectorAll('.typewriter');
        
        typewriterElements.forEach(element => {
            const text = element.textContent;
            element.textContent = '';
            element.style.borderRight = '2px solid #ff6600';
            
            let i = 0;
            const timer = setInterval(() => {
                element.textContent += text.charAt(i);
                i++;
                
                if (i > text.length) {
                    clearInterval(timer);
                    element.style.borderRight = 'none';
                }
            }, 100);
        });
    }

    // OPTIMIZACIÓN DE RENDIMIENTO
    let ticking = false;
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateAnimations);
            ticking = true;
        }
    }
    
    function updateAnimations() {
        // Actualizar todas las animaciones aquí
        ticking = false;
    }
    
    window.addEventListener('scroll', requestTick);

    console.log('🚀 megadominio.co - Todos los efectos cargados correctamente');

    // INICIALIZACIÓN
    initSmoothScrolling();
    initActiveNavigation();
    initMobileNavigation();
    initParallaxEffects();
    initCounterAnimation();
    initTestimonialsSlider();
    initHoverEffects();
    initLazyLoading();
    initCodeEditor();
    
    // Funciones responsive
    adjustCodeEditorSize();
    optimizeAnimationsForMobile();
    
    // Event listeners para responsive
    window.addEventListener('resize', () => {
        adjustCodeEditorSize();
        optimizeAnimationsForMobile();
    });
    
    window.addEventListener('orientationchange', handleOrientationChange);
    
    // Optimizar rendimiento en móviles
    if (window.innerWidth <= 767) {
        // Reducir frecuencia de eventos scroll en móvil
        let ticking = false;
        function updateOnScroll() {
            if (!ticking) {
                requestAnimationFrame(() => {
                    // Aquí van las funciones de scroll optimizadas
                    ticking = false;
                });
                ticking = true;
            }
        }
        window.addEventListener('scroll', updateOnScroll, { passive: true });
    }
}); 

const webPages = {
    'paginas-web': `
        <div class="web-content">
            <div class="hero-section">
                <h2>🌐 Sitio Web Profesional</h2>
                <p>Diseño moderno y responsive</p>
            </div>
            <div class="features-compact">
                <div class="feature-item">📱 Responsive</div>
                <div class="feature-item">⚡ Rápido</div>
                <div class="feature-item">🎨 Moderno</div>
            </div>
            <div class="cta-compact">
                <button class="cta-btn">Contactar Ahora</button>
            </div>
        </div>
    `,
    'ecommerce': `
        <div class="web-content">
            <div class="hero-section">
                <h2>🛒 Tienda Online</h2>
                <p>¡Bienvenido a nuestra tienda!</p>
            </div>
            <div class="products-compact">
                <div class="product-item">📱 Smartphone $599</div>
                <div class="product-item">💻 Laptop $999</div>
                <div class="product-item">🎧 Audífonos $199</div>
            </div>
            <div class="cta-compact">
                <button class="cta-btn">Agregar al Carrito</button>
            </div>
        </div>
    `,
    'software': `
        <div class="web-content">
            <div class="hero-section">
                <h2>💻 Software Personalizado</h2>
                <p>Soluciones a medida para tu negocio</p>
            </div>
            <div class="features-compact">
                <div class="feature-item">🔧 Backend Robusto</div>
                <div class="feature-item">🎨 UI Moderna</div>
                <div class="feature-item">📊 Analytics</div>
            </div>
            <div class="cta-compact">
                <button class="cta-btn">Ver Demo</button>
            </div>
        </div>
    `,
    'wordpress': `
        <div class="web-content">
            <div class="hero-section">
                <h2>📝 WordPress Premium</h2>
                <p>Sitio web profesional con WordPress</p>
            </div>
            <div class="features-compact">
                <div class="feature-item">🎨 Tema Premium</div>
                <div class="feature-item">🔌 Plugins</div>
                <div class="feature-item">📱 Responsive</div>
            </div>
            <div class="status-compact">
                <span class="status-item">✓ SEO optimizado</span>
                <span class="status-item">✓ Seguridad avanzada</span>
            </div>
        </div>
    `,
    'woocommerce': `
        <div class="web-content">
            <div class="hero-section">
                <h2>🛍️ WooCommerce Store</h2>
                <p>Tienda online con WordPress</p>
            </div>
            <div class="stats-compact">
                <div class="stat-item">📊 $12,450</div>
                <div class="stat-item">📦 89 pedidos</div>
                <div class="stat-item">👥 156 clientes</div>
            </div>
            <div class="products-list">
                <div class="product-line">�� Producto A - $49</div>
                <div class="product-line">⭐ Producto B - $79</div>
            </div>
        </div>
    `,
    'correos': `
        <div class="web-content">
            <div class="hero-section">
                <h2>📧 Correo Corporativo</h2>
                <p>Sistema de email profesional</p>
            </div>
            <div class="email-compact">
                <div class="email-line">📥 Cliente Importante - Propuesta...</div>
                <div class="email-line">📧 Equipo Marketing - Campaña Q4...</div>
                <div class="email-line">🔧 Soporte - Ticket #1234 resuelto</div>
            </div>
            <div class="status-compact">
                <span class="status-item">✓ SSL seguro</span>
                <span class="status-item">✓ Sync móvil</span>
            </div>
        </div>
    `,
    'hosting': `
        <div class="web-content">
            <div class="hero-section">
                <h2>🌐 Hosting Premium</h2>
                <p>Servidor optimizado y seguro</p>
            </div>
            <div class="stats-compact">
                <div class="stat-item">⚡ 95% más rápido</div>
                <div class="stat-item">🔒 SSL incluido</div>
                <div class="stat-item">📈 99.9% uptime</div>
            </div>
            <div class="status-compact">
                <span class="status-item">✓ Backup diario</span>
                <span class="status-item">✓ Soporte 24/7</span>
            </div>
        </div>
    `,
    'dominios': `
        <div class="web-content">
            <div class="hero-section">
                <h2>🌍 Registro de Dominios</h2>
                <p>Tu nombre en internet</p>
            </div>
            <div class="domain-search">
                <input type="text" placeholder="tuempresa.com" readonly>
                <button>Buscar</button>
            </div>
            <div class="domain-results">
                <div class="domain-line">✓ tuempresa.com - $12/año</div>
                <div class="domain-line">✓ tuempresa.net - $15/año</div>
                <div class="domain-line">✗ tuempresa.org - No disponible</div>
            </div>
        </div>
    `,
    'ssl': `
        <div class="web-content">
            <div class="hero-section">
                <h2>🔒 Certificado SSL</h2>
                <p>Seguridad y confianza para tu sitio</p>
            </div>
            <div class="ssl-status">
                <div class="security-badge">
                    <span class="lock-icon">🔒</span>
                    <span>Conexión Segura</span>
                </div>
            </div>
            <div class="ssl-info">
                <div class="info-line">Emisor: Let's Encrypt</div>
                <div class="info-line">Estado: ✅ Válido hasta 2024</div>
            </div>
            <div class="status-compact">
                <span class="status-item">✓ Encriptación 256-bit</span>
                <span class="status-item">✓ Mejor SEO</span>
            </div>
        </div>
    `
}; 
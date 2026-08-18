// Inicializar AOS
AOS.init({
    duration: 1000,
    once: true,
    offset: 100
});
// Loader
window.addEventListener('load', () => {
    setTimeout(() => {
        document.getElementById('loader').classList.add('hidden');
    }, 500);
});
// Navbar Scroll
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});
// Active Nav Link al Scrollear
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 100;
        const sectionHeight = section.offsetHeight;
        if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
            current = section.getAttribute('id');
        }
    });
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').slice(1) === current) {
            link.classList.add('active');
        }
    });
});
// Efecto de escritura
const texts = [
    'Python Django Full Stack Developer',
    'Unity C# Developer',
    'Game Designer',
    'Python Enthusiast',
    'Problem Solver'
];
let textIndex = 0;
let charIndex = 0;
let isDeleting = false;
const typingSpeed = 100;
const deletingSpeed = 50;
const pauseTime = 2000;
function typeText() {
    const currentText = texts[textIndex];
    const typingElement = document.getElementById('typing-text');
    if (!typingElement) return;
    if (isDeleting) {
        typingElement.textContent = currentText.substring(0, charIndex - 1);
        charIndex--;
    } else {
        typingElement.textContent = currentText.substring(0, charIndex + 1);
        charIndex++;
    }
    if (!isDeleting && charIndex === currentText.length) {
        isDeleting = true;
        setTimeout(typeText, pauseTime);
    } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        textIndex = (textIndex + 1) % texts.length;
        setTimeout(typeText, 500);
    } else {
        const speed = isDeleting ? deletingSpeed : typingSpeed;
        setTimeout(typeText, speed);
    }
}
typeText();
// Filtros de los Projects
const filterBtns = document.querySelectorAll('.filter-btn');
const projectCards = document.querySelectorAll('.project-card');
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const filter = btn.getAttribute('data-filter');
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        projectCards.forEach(card => {
            if (filter === 'all' || card.getAttribute('data-category') === filter) {
                card.style.display = 'block';
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'scale(1)';
                }, 100);
            } else {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.8)';
                setTimeout(() => {
                    card.style.display = 'none';
                }, 300);
            }
        });
    });
});
// Efecto scroll al hacer click
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
// Form de contact
document.getElementById('contactForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    // Aquí agregar la lógica para enviar el formulario
    alert('Message sent successfully!');
    this.reset();
});
// Cursor custom
const cursor = document.getElementById('cursor');
const cursorFollower = document.getElementById('cursor-follower');
if (cursor && cursorFollower) {
    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
        setTimeout(() => {
            cursorFollower.style.left = e.clientX + 'px';
            cursorFollower.style.top = e.clientY + 'px';
        }, 100);
    });
    document.addEventListener('mousedown', () => {
        cursor.style.transform = 'translate(-40%, -50%) scale(1.5)';
        cursorFollower.style.transform = 'translate(-50%, -70%) scale(1.5)';
    });
    document.addEventListener('mouseup', () => {
        cursor.style.transform = 'translate(-40%, -50%) scale(1)';
        cursorFollower.style.transform = 'translate(-50%, -70%) scale(1)';
    });
}
const inputs = document.querySelectorAll('input, textarea, select');
inputs.forEach((el) => {
    el.addEventListener('mouseenter', () => {
        if (cursor) cursor.style.opacity = '0';
        if (cursorFollower) cursorFollower.style.opacity = '0';
    });
    el.addEventListener('mouseleave', () => {
        if (cursor) cursor.style.opacity = '1';
        if (cursorFollower) cursorFollower.style.opacity = '1';
    });
});
// Efecto Parallax en el nombre
document.addEventListener('mousemove', (e) => {
    const shapes = document.querySelectorAll('.shape');
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;

    shapes.forEach((shape, index) => {
        const speed = (index + 1) * 20;
        shape.style.transform = `translate(${x * speed}px, ${y * speed}px)`;
    });
});
// Animación en la barra de progreso de las skills
const observerOptions = {
    threshold: 0.5,
    rootMargin: '0px 0px -100px 0px'
};
const skillObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const progressBars = entry.target.querySelectorAll('.skill-progress-bar');
            progressBars.forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 200);
            });
            skillObserver.unobserve(entry.target);
        }
    });
}, observerOptions);
document.querySelectorAll('.skill-card').forEach(card => {
    skillObserver.observe(card);
});
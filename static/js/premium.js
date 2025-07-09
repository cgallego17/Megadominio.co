document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.testimonio-slide');
    let current = 0;
    if (slides.length > 0) {
        slides[0].classList.add('active');
        setInterval(() => {
            slides[current].classList.remove('active');
            current = (current + 1) % slides.length;
            slides[current].classList.add('active');
        }, 4000);
    }
}); 
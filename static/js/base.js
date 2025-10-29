// Плавная прокрутка
document.addEventListener('DOMContentLoaded', function() {
    // Анимация появления элементов
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });

    // Наблюдаем за карточками
    document.querySelectorAll('.card, .post-card').forEach((el) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Интерактивные элементы
    document.querySelectorAll('.btn, .card').forEach(el => {
        el.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });

        el.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});
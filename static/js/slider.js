document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.slider-image');
    const prevButton = document.querySelector('.control-button.prev');
    const nextButton = document.querySelector('.control-button.next');
    const shuffleButton = document.querySelector('.control-button.shuffle');
    let currentIndex = 0;

    function showImage(index) {
        images.forEach(img => img.classList.remove('active'));
        images[index].classList.add('active');
    }

    function nextImage() {
        currentIndex = (currentIndex + 1) % images.length;
        showImage(currentIndex);
    }

    function prevImage() {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        showImage(currentIndex);
    }

    function shuffleImages() {
        currentIndex = Math.floor(Math.random() * images.length);
        showImage(currentIndex);
    }

    nextButton.addEventListener('click', nextImage);
    prevButton.addEventListener('click', prevImage);
    shuffleButton.addEventListener('click', shuffleImages);

    // 초기 이미지 표시
    showImage(currentIndex);
});
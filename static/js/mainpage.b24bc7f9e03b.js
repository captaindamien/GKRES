// jquery скрипт на карту
$(function() {
    $('[data-code]').mouseenter(function() {
        $('.district span').html($(this).attr('data-title'));
        $('.district').show();
    });
    $('[data-code]').mouseleave(function() {
        if (!$('.rf-map').hasClass("open")) {
            $('.district').hide();
        }
    });
    $('.rf-map').on('click', '[data-code], .district-links div', function(){
        let id = $(this).attr('data-code');
        if ($('#' + id).text() != '') {
            $('.district').show();
            $('.district span').html($(this).attr('data-title'));
            $('.rf-map').addClass('open');
            $('#' + id).fadeIn();
        }
    });
    $('.close-district').click(function() {
        $('.rf-map').removeClass('open');
        $('.district-text').hide();
        $('.district').hide();
    });
    $('[data-code]').each(function() {
        let id = $(this).attr('data-code');
        let title = $(this).attr('data-title');
        if ($('#' + id).text() != '') {
            $('.district-links').append('<div data-title="' + title + '" data-code="' + id + '">' + title + '</div>');
        }
    });
});

// скрытие хедера
const header = document.getElementById('header');
header.style.display = 'none';

// скрытие футера
const footer = document.getElementsByClassName('footer-bottom');
for (let i = 0; i < footer.length; i++) {
    footer[i].style.display = 'none';
}

// карусель
const carouselElem = document.getElementsByClassName('region');

for (let i = 0; i < carouselElem.length; i++) {
    carouselElem[i].addEventListener('mouseover', function () {
        [].forEach.call(carouselElem, function (elem) {
            elem.classList.remove('active-region');
            elem.getElementsByTagName('img')[0].classList.remove('active-img');
        });
        carouselElem[i].classList.add('active-region');
        carouselElem[i].getElementsByTagName('img')[0].classList.add('active-img');
    });
}

// scroll snap
const container = document.querySelector('.main');
const items = document.querySelectorAll('.big-block-container');

container.addEventListener('wheel', (event) => {
    event.preventDefault();
    const delta = event.deltaY;

    container.scrollBy({
        top: delta,
        behavior: 'smooth'
    });
});

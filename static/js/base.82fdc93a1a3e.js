const dropdownContainer = document.querySelectorAll('.dropdown-container');

for (let i = 0; i < dropdownContainer.length; i++) {
    dropdownContainer[i].querySelector('.fa-dropdown').addEventListener('click', () => {
        const dropdown = dropdownContainer[i].nextElementSibling;
        dropdown.classList.toggle('open');
    })
}

content = document.querySelector(".content-container");
menuIcon = document.querySelector(".menu-icon");
closeIcon = document.querySelector(".close-icon");
header = document.querySelector(".header");

menuIcon.onclick = function () {
    window.scrollTo(0, 0);
    content.style.display = "none";
    header.style.display = "block";
    menuIcon.style.display = "none";
    closeIcon.style.display = "block";
}

closeIcon.onclick = function () {
    content.style.display = "block";
    header.style.display = "none";
    menuIcon.style.display = "block";
    closeIcon.style.display = "none";
}

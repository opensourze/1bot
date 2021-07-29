AOS.init({ once: true }); // play AOS animation only once

// navbar stuff
const menuBtn = document.getElementsByClassName("navbar__menu-btn")[0];
const navbarLinks = document.getElementsByClassName("navbar__links")[0];
menuBtn.addEventListener("click", () => {
  navbarLinks.classList.toggle("active");
});

// docs dropdown stuff
const categories = document.querySelectorAll("section.collapsed");
for (let category of categories) {
  category.firstElementChild.addEventListener("click", () => {
    category.classList.toggle("collapsed");
    category.classList.toggle("active");
    console.log(category);
  });
}

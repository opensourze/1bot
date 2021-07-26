AOS.init({ once: true });

const menuBtn = document.getElementsByClassName("navbar__menu-btn")[0];
const navbarLinks = document.getElementsByClassName("navbar__links")[0];

menuBtn.addEventListener("click", () => {
  navbarLinks.classList.toggle("active");
});

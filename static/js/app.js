const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const forgot_pass_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
  container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode");
});

forgot_pass_btn.addEventListener("click", () => {
  fetch("http://127.0.0.1:5000/signup-signin")
.then(response => response.json())
.then(data => console.log("Success:", data))
});

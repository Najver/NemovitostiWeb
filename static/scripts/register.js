document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("register-form");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const confirmInput = document.getElementById("confirm_password");
    const errorBox = document.getElementById("form-error");

    // validace formulare
    form.addEventListener("submit", function (e) {
        errorBox.textContent = "";

        const username = usernameInput.value.trim();
        const password = passwordInput.value;
        const confirm = confirmInput.value;

        let errors = [];
        if (!username) {
            errors.push("Uživatelské jméno nesmí být prázdné.");
        }

        if (password.length < 8) {
            errors.push("Heslo musí mít alespoň 8 znaků.");
        }

        if (password !== confirm) {
            errors.push("Hesla se neshodují.");
        }

        if (errors.length > 0) {
            e.preventDefault();
            errorBox.innerHTML = errors.map(err => `<div>${err}</div>`).join("");
        }
    });
});

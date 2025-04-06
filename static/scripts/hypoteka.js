document.addEventListener("DOMContentLoaded", function () {
    console.log("Hypotéka JS načten.");

    const form = document.querySelector("form");
    const chybaBox = document.getElementById("chyba");
    const infoBox = document.getElementById("info");
    const fixaceSelect = document.getElementById("fixace");
    const urokInput = document.getElementById("urok");
    const mesiceInput = document.getElementById("mesice");

    let sazbyFixace = {};

    // nacteni dat z jsonu fixnich sazeb
    fetch("/static/data/sazby.json")
        .then(response => response.json())
        .then(data => {
            sazbyFixace = data;

            const selectedFixace = fixaceSelect.dataset.selected || "5";
            fixaceSelect.innerHTML = "";

            for (const fixace in sazbyFixace) {
                const sazba = sazbyFixace[fixace];
                const option = document.createElement("option");
                option.value = fixace;
                option.textContent = `${fixace} let – ${sazba} %`;
                if (fixace === selectedFixace) option.selected = true;
                fixaceSelect.appendChild(option);
            }

            if (urokInput && selectedFixace in sazbyFixace) {
                urokInput.value = sazbyFixace[selectedFixace];
            }
        });

    // nastaveni sazby podle fixace
    if (fixaceSelect && urokInput) {
        fixaceSelect.addEventListener("change", function () {
            const novaFixace = this.value;
            const novaSazba = sazbyFixace[novaFixace];
            if (novaSazba !== undefined) {
                urokInput.value = novaSazba;

                // volitelne
                //const doporucenaSplatnost = parseInt(novaFixace) * 12;
                //if (mesiceInput && parseInt(mesiceInput.value) < doporucenaSplatnost) {
                //    mesiceInput.value = doporucenaSplatnost;
                //}
            }
        });
    }

    // validace formulare
    if (form) {
        const cenaPredikce = parseFloat(form.dataset.cena || 0);

        form.addEventListener("submit", function (e) {
            chybaBox.textContent = "";
            infoBox.textContent = "";

            let chyba = false;
            let chybaTexty = [];

            let uver = parseFloat(form.uver?.value || "0");
            let urok = parseFloat(urokInput?.value || "0");
            let mesice = parseInt(mesiceInput?.value || "0");
            let fixaceLet = parseInt(fixaceSelect?.value || "0");
            let vlastni = parseFloat(form.vlastni?.value || "0");

            if (uver < 0 && form.uver) {
                form.uver.value = 0;
                chyba = true;
                chybaTexty.push("Úvěr nemůže být záporný, byl opraven na 0.");
            }

            if (urok < 0) {
                urokInput.value = 0;
                chyba = true;
                chybaTexty.push("Úroková sazba nemůže být záporná, byla opravena na 0.");
            }

            if (mesice < 0) {
                mesiceInput.value = 1;
                chyba = true;
                chybaTexty.push("Doba splácení nemůže být záporná, byla opravena na 1 měsíc.");
            }

            if (vlastni < 0 && form.vlastni) {
                form.vlastni.value = 0;
                chyba = true;
                chybaTexty.push("Vlastní prostředky nemohou být záporné, byly opraveny na 0.");
            }

            //kontrola jestli se mesice rovnaji nebo jsou vetsi nez fixni mesice
            if (!chyba && fixaceLet && mesice < fixaceLet * 12) {
                chyba = true;
                chybaTexty.push(`Při fixaci na ${fixaceLet} let musí být doba splácení alespoň ${fixaceLet * 12} měsíců.`);
            }

            if (!chyba && cenaPredikce && vlastni >= cenaPredikce) {
                e.preventDefault();
                infoBox.textContent = "Nemusíte si brát hypotéku – máte dostatek vlastních prostředků.";
                return;
            }

            //zakaze odeslani formulare jestli tam je chyba
            if (chyba) {
                e.preventDefault();
                chybaBox.innerHTML = chybaTexty.map(t => `<div>${t}</div>`).join("");
            }
        });
    }
});

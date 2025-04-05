document.addEventListener("DOMContentLoaded", function () {
    const metrazInput = document.querySelector('input[name="metraz"]');

    if (metrazInput) {
        metrazInput.addEventListener("input", function () {
            let value = parseFloat(this.value);
            if (value > 150) {
                this.value = 150;
            } else if (value < 0) {
                this.value = 0;
            }
        });
    }
});

//export tabulky do CSV
function exportTableToCSV() {
    const table = document.getElementById("comparison-table");
    if (!table) return;

    let csv = "";
    for (const row of table.rows) {
        const cells = Array.from(row.cells).map(cell => `"${cell.innerText}"`);
        csv += cells.join(",") + "\n";
    }

    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "srovnani_cen.csv";
    a.click();
}

//export tlačítko
document.addEventListener("DOMContentLoaded", () => {
    const exportBtn = document.getElementById("export-csv-btn");
    if (exportBtn) {
        exportBtn.addEventListener("click", exportTableToCSV);
    }
});


document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector(".comparison-table");
    if (!table) return; // safety check
    const tbody = table.tBodies[0];
    const originalRows = Array.from(tbody.rows); // save original order
    const sortState = {}; // columnIndex -> 0(original), 1(asc), 2(desc)

    window.sortTable = function(columnIndex) {
        if (sortState[columnIndex] === undefined) sortState[columnIndex] = 0;

        // cycle: 0(original) -> 1(asc) -> 2(desc) -> 0(original)
        sortState[columnIndex] = (sortState[columnIndex] + 1) % 3;
        const state = sortState[columnIndex];

        let rows;
        if (state === 0) {
            // back to original order
            rows = originalRows.slice();
        } else {
            rows = Array.from(tbody.rows);
            const ascending = state === 1;

            rows.sort((a, b) => {
                let aText = a.cells[columnIndex].innerText.trim();
                let bText = b.cells[columnIndex].innerText.trim();

                // try numeric comparison
                const aNum = parseFloat(aText.replace(/[^\d.,-]/g, '').replace(',', '.'));
                const bNum = parseFloat(bText.replace(/[^\d.,-]/g, '').replace(',', '.'));

                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return ascending ? aNum - bNum : bNum - aNum;
                }

                // fallback to string comparison
                return ascending ? aText.localeCompare(bText) : bText.localeCompare(aText);
            });
        }

        // append sorted rows back
        rows.forEach(row => tbody.appendChild(row));
    };
});

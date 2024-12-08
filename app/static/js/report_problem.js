function openReportForm() {
    document.getElementById("reportProblemModal").style.display = "block";
}

function closeReportForm() {
    document.getElementById("reportProblemModal").style.display = "none";
}

document.getElementById("reportForm").onsubmit = async function (event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    const response = await fetch('/report-problem', {
        method: 'POST',
        body: formData,
    });

    const result = await response.json();
    alert(result.message);
    closeReportForm();
};

document.getElementById("registrationForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = {};
    formData.forEach((value, key) => data[key] = value);

    const responseBox = document.getElementById("response");

    try {
        const response = await fetch("https://datapy.hifrnds.in/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        responseBox.textContent = result.message;
        responseBox.style.color = result.status === "success" ? "green" : "red";
    } catch (err) {
        responseBox.textContent = "Server error. Try again.";
        responseBox.style.color = "red";
    }
});

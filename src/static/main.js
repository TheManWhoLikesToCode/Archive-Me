function showLoadingScreen() {
    var loadingScreen = document.getElementById("loading-screen");
    if (loadingScreen) {
        loadingScreen.style.display = "block";
    }
}

function hideLoadingScreen() {
    var loadingScreen = document.getElementById("loading-screen");
    if (loadingScreen) {
        loadingScreen.style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    function Login(e) {
        e.preventDefault();
        var username = document.getElementById("username").value;
        var password = document.getElementById("password").value;
        var responseContainer = document.getElementById("response-container");

        showLoadingScreen();

        console.log("Fetching /login...");
        fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: username,
                password: password,
            }),
        })
            .then(function (response) {
                if (!response.ok) {
                    return response.json().then(data => {
                        // Extract and throw the server's error message
                        throw new Error(data.error);
                    });
                }
                return response.text();
            })
            .then(function (data) {
                // Display the server's response
                console.log("Server response:", data);
                responseContainer.innerText = data;
                responseContainer.style.display = "block";
                responseContainer.classList.add('alert-success');
            })
            .catch(function (error) {
                // Handle and display the server's error message
                console.error("Error:", error.message);
                responseContainer.innerText = error.message;
                responseContainer.style.display = "block";
                responseContainer.classList.add('alert-danger');
            })
            .finally(function () {
                hideLoadingScreen();
            });
    }

    // Attach the event listener to the form
    var form = document.querySelector("form");
    form.addEventListener("submit", Login);

    hideLoadingScreen();
});

function archiveCourses() {
    showLoadingScreen();

    fetch("/scrape", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then(function (response) {
            if (!response.ok) {
                return response.json().then(data => {
                    // Extract and throw the server's error message
                    throw new Error(data.error);
                });
            }
            return response.json();
        })
        .then(function (data) {
            if (data.file_key) {
                // Construct the download URL
                const downloadUrl = '/download?file_key=' + encodeURIComponent(data.file_key);

                // Create a temporary link and click it to start the download
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.setAttribute('download', data.file_key); // Optional: Set the download file name
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        })
        .catch(function (error) {
            // Handle and display the server's error message
            alert(error.message);
        })
        .finally(function () {
            hideLoadingScreen();
        });
}

function Login(event) {
    event.preventDefault();

    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    var responseContainer = document.getElementById("response-container");

    showLoadingScreen();

    console.log("Fetching /login...");
    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            username: username,
            password: password,
        }),
    })
        .then(function (response) {
            if (!response.ok) {
                return response.json().then(data => {
                    // Extract and throw the server's error message
                    throw new Error(data.error);
                });
            }
            return response.text();
        })
        .then(function (data) {
            // Display the server's response in a new tab
            var newTab = window.open();
            newTab.document.write(data);
            newTab.document.close();

            responseContainer.innerText = data;
            responseContainer.style.display = "block";
            responseContainer.classList.add('alert-success');
        })
        .catch(function (error) {
            // Handle and display the server's error message
            console.error("Error:", error.message);
            responseContainer.innerText = error.message;
            responseContainer.style.display = "block";
            responseContainer.classList.add('alert-danger');
        })
        .finally(function () {
            hideLoadingScreen();
        });
}

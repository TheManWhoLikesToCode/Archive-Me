$(function () {
  // init feather icons
  feather.replace();

  // init tooltip & popovers
  $('[data-toggle="tooltip"]').tooltip();
  $('[data-toggle="popover"]').popover();

  //page scroll
  $("a.page-scroll").bind("click", function (event) {
    var $anchor = $(this);
    $("html, body")
      .stop()
      .animate(
        {
          scrollTop: $($anchor.attr("href")).offset().top - 20,
        },
        1000
      );
    event.preventDefault();
  });

  // slick slider
  $(".slick-about").slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
    dots: true,
    arrows: false,
  });

  //toggle scroll menu
  var scrollTop = 0;
  $(window).scroll(function () {
    var scroll = $(window).scrollTop();
    //adjust menu background
    if (scroll > 80) {
      if (scroll > scrollTop) {
        $(".smart-scroll").addClass("scrolling").removeClass("up");
      } else {
        $(".smart-scroll").addClass("up");
      }
    } else {
      // remove if scroll = scrollTop
      $(".smart-scroll").removeClass("scrolling").removeClass("up");
    }

    scrollTop = scroll;

    // adjust scroll to top
    if (scroll >= 600) {
      $(".scroll-top").addClass("active");
    } else {
      $(".scroll-top").removeClass("active");
    }
    return false;
  });

  // scroll top top
  $(".scroll-top").click(function () {
    $("html, body").stop().animate(
      {
        scrollTop: 0,
      },
      1000
    );
  });

  /**Theme switcher - DEMO PURPOSE ONLY */
  $(".switcher-trigger").click(function () {
    $(".switcher-wrap").toggleClass("active");
  });
  $(".color-switcher ul li").click(function () {
    var color = $(this).attr("data-color");
    $("#theme-color").attr("href", "static/" + color + ".css");
    $(".color-switcher ul li").removeClass("active");
    $(this).addClass("active");
  });
});

// Use a modular approach
const app = (() => {
  let fileKeyGlobal = null;

  const showLoadingScreen = () => {
    const loadingScreen = document.getElementById("loading-screen");
    if (loadingScreen) {
      loadingScreen.style.display = "block";
    }
  };

  const hideLoadingScreen = () => {
    const loadingScreen = document.getElementById("loading-screen");
    if (loadingScreen) {
      loadingScreen.style.display = "none";
    }
  };

  const updateDownloadButtonVisibility = () => {
    const downloadButton = document.getElementById("downloadButton");
    if (fileKeyGlobal) {
      downloadButton.style.display = "block"; // Show button if file_key is present
    } else {
      downloadButton.style.display = "none"; // Hide button otherwise
    }
  };

  const fetchWithErrorHandler = async (url, options) => {
    const response = await fetch(url, options);
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Server responded with an error');
    }
    return response;
  };

  const loginEventHandler = async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const responseContainer = document.getElementById("response-container");

    showLoadingScreen();

    try {
      const response = await fetchWithErrorHandler("http://127.0.0.1:5001/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });
      const message = await response.text();
      responseContainer.textContent = message;
      responseContainer.classList.add("alert-success");
    } catch (error) {
      responseContainer.textContent = error.message;
      responseContainer.classList.add("alert-danger");
    } finally {
      responseContainer.style.display = "block";
      hideLoadingScreen();
    }
  };

  const archiveCourses = async () => {
    showLoadingScreen();
    try {
      console.log("Archiving courses...");
      const response = await fetchWithErrorHandler("http://127.0.0.1:5001/scrape", {
        method: "GET",
        headers: { "Content-Type": "application/json" }
      });
      const data = await response.json();
      if (data.file_key) {
        fileKeyGlobal = data.file_key;
        console.log("Archive successful. Ready for download.");
        alert("Archive successful. Ready for download.");
        updateDownloadButtonVisibility();
      }
    } catch (error) {
      console.error("Error archiving courses:", error);
      alert(error.message);
    } finally {
      hideLoadingScreen();
    }
  };

  const downloadFile = async () => {
    if (!fileKeyGlobal) {
      alert("No file available to download. Please archive courses first.");
      return;
    }
    showLoadingScreen();
    try {
      console.log("Downloading file...");
      const baseUrl = window.location.origin;
      const downloadUrl = `http://127.0.0.1:5001/download/${encodeURIComponent(fileKeyGlobal)}`;
      const response = await fetchWithErrorHandler(downloadUrl);

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", fileKeyGlobal);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading file:", error);
      alert('Error downloading file: ' + error.message);
    } finally {
      hideLoadingScreen();
      fileKeyGlobal = null;
    }
  };

  const init = () => {
    const loginForm = document.querySelector("#loginForm");
    if (loginForm) {
      loginForm.addEventListener("submit", loginEventHandler);
    }
    const archiveButton = document.querySelector("#archiveButton");
    if (archiveButton) {
      archiveButton.addEventListener("click", archiveCourses);
    }
    const downloadButton = document.querySelector("#downloadButton");
    if (downloadButton) {
      downloadButton.addEventListener("click", downloadFile);
    }

    hideLoadingScreen();
    updateDownloadButtonVisibility();
  };

  return { init };
})();

document.addEventListener("DOMContentLoaded", app.init);

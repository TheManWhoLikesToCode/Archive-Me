import { getApiUrl } from './helpers.js';

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
  let currentPath = '';

  const apiUrl = getApiUrl();

  const showLoadingScreen = () => {
    const loadingScreen = document.getElementById("loading-screen");
    if (loadingScreen) {
      loadingScreen.style.display = "flex";
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
    if (downloadButton) {
      if (fileKeyGlobal) {
        downloadButton.style.display = "";
      } else {
        downloadButton.style.display = "none"; // Hide button otherwise
      }
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
    showLoadingScreen();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const responseContainer = document.getElementById("response-container");

    try {
      const response = await fetchWithErrorHandler(`${apiUrl}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
        credentials: 'include',
      });
      const data = await response.json();

      if (response.ok) {
        sessionStorage.setItem("user", JSON.stringify({ username: username }));
        window.location.href = '/userpage';
      } else {
        const message = data.message || 'Error occurred';
        responseContainer.textContent = message;
        responseContainer.classList.add("alert-danger");
      }
    } catch (error) {
      responseContainer.textContent = error.message;
      responseContainer.classList.add("alert-danger");
    } finally {
      responseContainer.style.display = "block";
      hideLoadingScreen();
    }
  };

  const logoutUser = async () => {
    try {
      const response = await fetch(`${apiUrl}/logout`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        sessionStorage.removeItem("user");
        window.location.href = '/logout';
      } else {
        console.error('Logout failed');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const checkLoginStatus = async () => {
    try {
      const response = await fetch(`${apiUrl}/is_logged_in`, {
        method: 'GET',
        credentials: 'include' // Necessary for including cookies
      });

      const data = await response.json();

      if (!data.logged_in) {
        console.log(data);
        window.location.href = '/login'; // Redirect to login page
      }
      // Optionally, handle the case when the user is logged in
      // e.g., display a welcome message, load user data, etc.
    } catch (error) {
      console.error('Error:', error);
      window.location.href = '/login'; // Redirect to login page in case of error
    }
  };


  const archiveCourses = async () => {
    showLoadingScreen();
    try {
      console.log("Archiving courses...");
      // Retrieve user data from session storage
      const user = JSON.parse(sessionStorage.getItem("user"));

      if (!user || !user.username) {
        console.error("User information not available for archiving courses");
        alert("User information is required.");
        return; // Exit the function if user information is not available
      }

      console.log("User:", user.username);

      const url = `${apiUrl}/scrape?username=${encodeURIComponent(user.username)}`;

      const response = await fetchWithErrorHandler(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        credentials: 'include'
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
      console.log(fileKeyGlobal);
      const baseUrl = window.location.origin;
      const downloadUrl = `${apiUrl}/download/${encodeURIComponent(fileKeyGlobal)}`;
      const response = await fetchWithErrorHandler(downloadUrl, {
        credentials: 'include'
      });

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

  // Global variable to store the current directory name
  let currentDirectoryName = '/';

  const updateDirectoryList = async (path, directoryName = '/') => {
    try {
      const response = await fetchWithErrorHandler(`${apiUrl}/browse/${path}`, {
        credentials: 'include'
      });
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const { folders, files } = await response.json();
        $('#directoryList').empty();
        currentDirectoryName = directoryName;
        $('#path').text(currentDirectoryName);

        folders.forEach(folder => {
          const li = $('<li>');
          const link = $('<a>')
            .attr('href', '#')
            .html(`<i class="fa fa-folder"></i> ${folder[0]}`)
            .click(async (event) => {
              event.preventDefault();
              await updateDirectoryList(folder[2], folder[0]);
            });
          li.append(link);
          $('#directoryList').append(li);
        });

        files.forEach(file => {
          const li = $('<li>');
          const link = $('<a>')
            .attr('href', '#')
            .html(`<i class="fa fa-file"></i> ${file[0]}`)
            .click(async (event) => {
              event.preventDefault();
              await updateDirectoryList(file[2], file[0]);
            });
          li.append(link);
          $('#directoryList').append(li);
        });
      } else {
        const file = await response.blob();
        const url = URL.createObjectURL(file);
        window.location.href = url;
      }
    } catch (error) {
      console.error("Error updating directory list:", error);
      alert('Error updating directory list: ' + error.message);
    }
  };

  const onDirectoryChange = (newPath) => {
    currentPath = newPath;
    updateDirectoryList(newPath);
  };

  $('#back').on('click', function (event) {
    event.preventDefault();
    const pathSegments = currentPath.split('/').filter(Boolean);
    pathSegments.pop();
    onDirectoryChange(pathSegments.join('/'));
  });

  const init = () => {

    const logoutLink = document.querySelector('a[href="/logout"]');
    if (logoutLink) {
      logoutLink.addEventListener('click', (event) => {
        logoutUser();
      });
    }

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
    if (window.location.pathname === '/userpage') {
      updateDirectoryList('');
    }
    if (window.location.pathname === '/userpage') {
      checkLoginStatus();
    }

    hideLoadingScreen();
    updateDownloadButtonVisibility();
  };

  return { init, logoutUser };
})();

document.addEventListener("DOMContentLoaded", app.init);
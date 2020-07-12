const message = document.getElementById("message");
const clearButton = document.getElementById("clear");
const authenticateButton = document.getElementById("authenticate");

function showLogin() {
  message.innerText = "Please log in to use Linksaver.";
  clearButton.style.display = "none";
  authenticateButton.style.display = "inline-block";
}

function showLogout() {
  message.innerHTML = "You are logged in. &#x1f60a";
  clearButton.style.display = "inline-block";
  authenticateButton.style.display = "none";
}

chrome.storage.local.get(["token"], values => {
  if (values.token) {
    showLogout();
  } else {
    showLogin();
  }
});

clearButton.addEventListener("click", () => {
  chrome.storage.local.set({ token: null }, () => {
    showLogin();
  });
});

authenticateButton.addEventListener("click", () => {
  const redirectURL = encodeURIComponent(browser.identity.getRedirectURL());
  const clientId = encodeURIComponent("ff");
  const authURL = `http://localhost:8080/oauth?client_id=${clientId}&redirect_uri=${redirectURL}`;

  return chrome.identity.launchWebAuthFlow(
    {
      interactive: true,
      url: authURL
    },
    redirect => {
      const parsed = new URL(redirect);
      const token = parsed.searchParams.get("token");
      chrome.storage.local.set({ token }, () => {
        showLogout();
      });
    }
  );
});

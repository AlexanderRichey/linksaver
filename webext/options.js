const message = document.getElementById("message");
const clearButton = document.getElementById("clear");
const authenticateButton = document.getElementById("authenticate");
const endpointForm = document.getElementById("endpoint-form");
const endpointField = document.getElementById("endpoint");

let globalEndpoint = "";

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

function populateEndpointValue(val) {
  globalEndpoint = val;
  endpointField.value = val;
}

chrome.storage.local.get(["token", "endpoint"], (values) => {
  if (values.token) {
    showLogout();
  } else {
    showLogin();
  }

  if (values.endpoint) {
    populateEndpointValue(values.endpoint);
  }
});

endpointForm.addEventListener("submit", (e) => {
  e.preventDefault();

  const endpointVal = endpointField.value;

  try {
    new URL(endpointVal);
  } catch {
    alert("This doesn't look like a valid URL.");
    return;
  }

  chrome.storage.local.set({ endpoint: endpointVal }, () => {
    populateEndpointValue(endpointVal);

    alert("Saved endpoint as " + endpointVal);
  });
});

clearButton.addEventListener("click", (e) => {
  e.preventDefault();

  chrome.storage.local.set({ token: null }, () => {
    showLogin();
  });
});

authenticateButton.addEventListener("click", (e) => {
  e.preventDefault();

  if (!globalEndpoint) {
    alert("You need to set your endpoint first.");
    return;
  }

  const redirectURL = encodeURIComponent(chrome.identity.getRedirectURL());
  const authURL = `${globalEndpoint}oauth?redirect_uri=${redirectURL}`;

  return chrome.identity.launchWebAuthFlow(
    {
      interactive: true,
      url: authURL,
    },
    (redirect) => {
      const parsed = new URL(redirect);
      const token = parsed.searchParams.get("token");
      chrome.storage.local.set({ token }, () => {
        showLogout();
      });
    }
  );
});

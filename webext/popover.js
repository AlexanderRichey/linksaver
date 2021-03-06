const main = document.querySelector("main");

chrome.tabs.query({ active: true, lastFocusedWindow: true }, (tabs) => {
  const tab = tabs[0];

  chrome.storage.local.get(["token", "endpoint"], (store) => {
    if (!(store.token && store.endpoint)) {
      window.open(chrome.runtime.getURL("options.html"));
      main.innerHTML = "<p>You need to authenticate</p>";
      return;
    }

    fetch(`${store.endpoint}api/links`, {
      headers: new Headers({
        "Content-Type": "application/json",
        Authorization: `Bearer ${store.token}`,
      }),
      method: "POST",
      mode: "cors",
      body: JSON.stringify({
        title: tab.title,
        url: tab.url,
        favicon:
          tab.favIconUrl && tab.favIconUrl.startsWith("https")
            ? tab.favIconUrl
            : "",
      }),
    })
      .then((response) => {
        if (response.status == 201) {
          main.innerHTML = "<p>&#x2705</p>";
        } else {
          main.innerHTML = "<p>&#x1f61e</p>";
        }
      })
      .catch(() => {
        main.innerHTML = "<p>&#x1f4e0</p>";
      });
  });
});

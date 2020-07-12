const main = document.querySelector("main");

chrome.tabs.query({ active: true, lastFocusedWindow: true }, tabs => {
  const tab = tabs[0];

  chrome.storage.local.get(["token"], store => {
    if (!store.token) {
      window.open(chrome.runtime.getURL("options.html"));
      main.innerHTML = "<p>need to authenticate</p>";
      return;
    }

    fetch("http://localhost:8080/api/links", {
      headers: new Headers({
        "Content-Type": "application/json",
        Authorization: `Bearer ${store.token}`
      }),
      method: "POST",
      mode: "cors",
      body: JSON.stringify({
        title: tab.title,
        url: tab.url,
        favicon:
          tab.favIconUrl && tab.favIconUrl.startsWith("https")
            ? tab.favIconUrl
            : ""
      })
    })
      .then(response => {
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

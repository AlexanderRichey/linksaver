const main = document.querySelector("main");
const token = "pnc69Pm-7CEWmdoAwWG9oQ";

chrome.tabs.query({ active: true, lastFocusedWindow: true }, tabs => {
  const tab = tabs[0];

  fetch("http://localhost:8000/api/links", {
    headers: new Headers({
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    }),
    method: "POST",
    mode: "cors",
    body: JSON.stringify({
      title: tab.title,
      url: tab.url,
      favicon: tab.favIconUrl.startsWith("https") ? tab.favIconUrl : ""
    })
  })
    .then(response => {
      if (response.status == 201) {
        main.innerHTML = "<p>worked</p>";
      } else {
        main.innerHTML = "<p>nope</p>";
      }
    })
    .catch(error => {
      main.innerHTML = "<p>nope</p>";
    });
});

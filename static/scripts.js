(() => {
  const application = Stimulus.Application.start();

  application.register(
    "note",
    class extends Stimulus.Controller {
      static get targets() {
        return ["content", "chrome", "nameContainer"];
      }

      toggle() {
        this.contentTarget.classList.toggle("display-none");
        this.chromeTarget.classList.toggle("display-none");
        this.nameContainerTarget.classList.toggle("open");
      }
    }
  );

  application.register(
    "link",
    class extends Stimulus.Controller {
      static get targets() {
        return [
          "content",
          "chrome",
          "inlineLinkIcon",
          "nameContainer",
          "lineItem"
        ];
      }

      toggle() {
        this.contentTarget.classList.toggle("display-none");
        this.chromeTarget.classList.toggle("display-none");
        this.inlineLinkIconTarget.classList.toggle("display-none");
        this.nameContainerTarget.classList.toggle("open");
        this.lineItemTarget.classList.toggle("open");
      }
    }
  );

  application.register(
    "textarea",
    class extends Stimulus.Controller {
      static get targets() {
        return ["editor"];
      }

      connect() {
        this.simplemde = new SimpleMDE({
          element: this.editorTarget,
          autofocus: true,
          spellChecker: false,
          status: false,
          toolbar: [
            {
              name: "bold",
              action: SimpleMDE.toggleBold,
              className: "fa fa-bold",
              title: "Bold"
            },
            {
              name: "italic",
              action: SimpleMDE.toggleItalic,
              className: "fa fa-italic",
              title: "Italic"
            },
            {
              name: "quote",
              action: SimpleMDE.toggleBlockquote,
              className: "fa fa-quote-left",
              title: "Quote"
            },
            "|",
            {
              name: "link",
              action: SimpleMDE.drawLink,
              className: "fa fa-link",
              title: "Link"
            },
            "|",
            {
              name: "preview",
              action: SimpleMDE.togglePreview,
              className: "fa fa-eye no-disable",
              title: "Preview"
            }
          ]
        });
      }

      disconnect() {
        this.simplemde.toTextArea();
        this.simplemde = null;
      }
    }
  );

  application.register(
    "bullet",
    class extends Stimulus.Controller {
      static get targets() {
        return ["image", "container"];
      }

      connect() {
        if (this.imageTarget.tagName.toUpperCase() === "IMG") {
          this.imageTarget.addEventListener("error", () => {
            this.containerTarget.innerHTML = "<p>&#x1F30F</p>";
          });
        }
      }
    }
  );

  document.addEventListener("submit", e => {
    e.preventDefault();
    const xhr = new XMLHttpRequest();
    const fd = new FormData(e.target);
    if (e.target.method.toUpperCase() === "GET") {
      const query = new URLSearchParams(fd).toString();
      xhr.open(e.target.method, "/?" + query);
    } else {
      xhr.open(e.target.method, e.target.getAttribute("action"));
    }
    xhr.onload = e => {
      const domparser = new DOMParser();
      const doc = domparser.parseFromString(e.target.response, "text/html");
      if (e.currentTarget.status < 300) {
        window.history.pushState("", doc.title, "/");
        window.document.title = doc.title;
      }
      document.body = doc.body;
    };
    xhr.send(fd);
  });
})();

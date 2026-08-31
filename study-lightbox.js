(function () {
  const style = document.createElement("style");
  style.textContent = `
    .visual.photo img,
    .visual.logo img {
      cursor: zoom-in;
      transition: opacity 0.15s ease;
    }
    .visual.photo img:hover,
    .visual.logo img:hover {
      opacity: 0.92;
    }
    .study-lightbox {
      position: fixed;
      inset: 0;
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      background: rgba(8, 12, 20, 0.92);
      backdrop-filter: blur(6px);
    }
    .study-lightbox[hidden] {
      display: none;
    }
    .study-lightbox__panel {
      position: relative;
      max-width: min(96vw, 1200px);
      max-height: 92vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.75rem;
    }
    .study-lightbox__img {
      max-width: 100%;
      max-height: calc(92vh - 3rem);
      object-fit: contain;
      border-radius: 12px;
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
      background: #fff;
    }
    .study-lightbox__caption {
      margin: 0;
      color: #e2e8f0;
      font: 500 0.95rem/1.4 "Segoe UI", system-ui, sans-serif;
      text-align: center;
      max-width: 60ch;
    }
    .study-lightbox__close {
      position: fixed;
      top: 1rem;
      right: 1rem;
      border: 0;
      width: 2.75rem;
      height: 2.75rem;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.14);
      color: #fff;
      font-size: 1.6rem;
      line-height: 1;
      cursor: pointer;
    }
    .study-lightbox__close:hover {
      background: rgba(255, 255, 255, 0.24);
    }
    body.study-lightbox-open {
      overflow: hidden;
    }
  `;
  document.head.appendChild(style);

  const overlay = document.createElement("div");
  overlay.className = "study-lightbox";
  overlay.hidden = true;
  overlay.innerHTML = `
    <button class="study-lightbox__close" type="button" aria-label="Close image">&times;</button>
    <div class="study-lightbox__panel">
      <img class="study-lightbox__img" alt="">
      <p class="study-lightbox__caption"></p>
    </div>
  `;
  document.body.appendChild(overlay);

  const image = overlay.querySelector(".study-lightbox__img");
  const caption = overlay.querySelector(".study-lightbox__caption");
  const closeButton = overlay.querySelector(".study-lightbox__close");

  function openLightbox(source) {
    image.src = source.src;
    image.alt = source.alt || "";
    caption.textContent = source.alt || "";
    caption.hidden = !source.alt;
    overlay.hidden = false;
    document.body.classList.add("study-lightbox-open");
    closeButton.focus();
  }

  function closeLightbox() {
    overlay.hidden = true;
    image.removeAttribute("src");
    document.body.classList.remove("study-lightbox-open");
  }

  document.querySelectorAll(".visual.photo img, .visual.logo img").forEach((thumb) => {
    thumb.addEventListener("click", () => openLightbox(thumb));
  });

  closeButton.addEventListener("click", closeLightbox);
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) {
      closeLightbox();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !overlay.hidden) {
      closeLightbox();
    }
  });
})();

/* CodeHub — small progressive-enhancement helpers. */
(function () {
  "use strict";

  const toggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector("[data-nav]");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.classList.toggle("is-active", open);
    });

    nav.addEventListener("click", function (event) {
      if (event.target.tagName === "A" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.classList.remove("is-active");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  // Smooth scrolling for in-page anchors.
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (event) {
      const id = link.getAttribute("href");
      if (id.length < 2) return;
      const target = document.querySelector(id);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  // Animate elements into view.
  const reveal = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && reveal.length) {
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    reveal.forEach(function (el) { observer.observe(el); });
  } else {
    reveal.forEach(function (el) { el.classList.add("is-visible"); });
  }

  // Safety net: never leave content invisible if the observer does not fire.
  window.setTimeout(function () {
    reveal.forEach(function (el) { el.classList.add("is-visible"); });
  }, 1500);

  // Auto-hide flash messages.
  document.querySelectorAll(".alert").forEach(function (alert) {
    setTimeout(function () {
      alert.classList.add("alert--hidden");
    }, 6000);
  });

  const reduceMotion =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Анимированные цифры (только для чистых чисел; "24/7" и "1:1" не трогаем).
  const counters = document.querySelectorAll("[data-counter]");
  function animateCounter(el) {
    const raw = (el.getAttribute("data-counter") || el.textContent || "").trim();
    if (!/^\d+$/.test(raw)) return;
    const target = parseInt(raw, 10);
    const duration = 1100;
    const start = performance.now();
    function frame(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = String(Math.round(target * eased));
      if (progress < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  if (counters.length && !reduceMotion) {
    if ("IntersectionObserver" in window) {
      const counterObserver = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              animateCounter(entry.target);
              counterObserver.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.4 }
      );
      counters.forEach(function (el) { counterObserver.observe(el); });
    } else {
      counters.forEach(animateCounter);
    }
  }

  // Эффект печатной машинки для окна с кодом.
  const typing = document.querySelectorAll("[data-typing]");
  function typeCode(el) {
    const full = el.textContent;
    if (!full) return;
    el.textContent = "";
    el.classList.add("is-typing");
    let index = 0;
    (function tick() {
      el.textContent = full.slice(0, index);
      index += 1;
      if (index <= full.length) {
        window.setTimeout(tick, 16);
      } else {
        el.classList.remove("is-typing");
        el.textContent = full;
      }
    })();
  }
  if (typing.length && !reduceMotion) {
    if ("IntersectionObserver" in window) {
      const typingObserver = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              typeCode(entry.target);
              typingObserver.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.3 }
      );
      typing.forEach(function (el) { typingObserver.observe(el); });
    } else {
      typing.forEach(typeCode);
    }
  }
})();

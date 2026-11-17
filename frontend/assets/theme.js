// Streamlit v2 exposes current theme values on the component wrapper. Observe
// only this component's ancestors; never inspect or change React internals,
// browser storage, another widget, or Streamlit's own theme selection.
export default function ({ parentElement }) {
  const probe = parentElement.querySelector(".theme-probe");
  const apply = () => {
    const rgb = getComputedStyle(probe).color.match(/[\d.]+/g);
    if (!rgb || rgb.length < 3) return;
    const [r, g, b] = rgb.map(Number);
    const mode = (r * 299 + g * 587 + b * 114) / 1000 > 128 ? "light" : "dark";
    if (document.documentElement.dataset.fraudTheme !== mode) {
      document.documentElement.dataset.fraudTheme = mode;
    }
  };
  const observer = new MutationObserver(apply);
  // The theme wrapper uses Emotion classes for its CSS custom properties.
  // Include the component host and wrapper, not the app-wide document tree.
  let host = parentElement;
  for (let depth = 0; host && depth < 3; depth++, host = host.parentElement) {
    observer.observe(host, { attributes: true, attributeFilter: ["class", "style"] });
  }
  apply();
  return () => observer.disconnect();
}

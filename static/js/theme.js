// document.addEventListener("DOMContentLoaded", () => {
//   // 1) Server-provided theme from context/session
//   const serverTheme = document.documentElement.dataset.theme;
//   if (serverTheme) {
//     document.documentElement.setAttribute("data-theme", serverTheme);
//   }

//   // 2) Prefer stored theme for immediate UX continuity
//   try {
//     const storedTheme = localStorage.getItem("aura-theme");
//     if (storedTheme) {
//       document.documentElement.setAttribute("data-theme", storedTheme);
//     }
//   } catch (err) {
//     // Ignore storage errors (e.g., private mode)
//   }
// // });

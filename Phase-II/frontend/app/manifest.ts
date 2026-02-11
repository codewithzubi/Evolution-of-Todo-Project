export default function manifest() {
  return {
    name: "Phase II Todo - Never forget a task again",
    short_name: "Phase II Todo",
    description: "Simple. Powerful. Yours. Organize your tasks effortlessly.",
    start_url: "/",
    display: "standalone",
    background_color: "#09090b",
    theme_color: "#3b82f6",
    icons: [
      {
        src: "/icon-192.png",
        sizes: "192x192",
        type: "image/png",
      },
      {
        src: "/icon-512.png",
        sizes: "512x512",
        type: "image/png",
      },
    ],
  };
}

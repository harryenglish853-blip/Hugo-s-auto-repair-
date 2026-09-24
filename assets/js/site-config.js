/* ==========================================================================
   SITE CONFIGURATION: the owner-editable settings for the website.
   Edit the values below. No build step is needed for this file.
   ========================================================================== */
window.HUGOS_CONFIG = {
  /* Service request form endpoint.
     The form will NOT show a success message until this is set to a working
     endpoint that returns a 2xx response. Until then, visitors are asked to call.
     Example (Formspree): "https://formspree.io/f/abcdwxyz"
     Any service that accepts a multipart/form-data POST and answers with 2xx works. */
  formEndpoint: "",

  /* Real shop footage for the hero (optional). Leave blank to use the built-in
     illustrated scene. Keep clips short (6–12s), muted, and compressed:
     aim for under 3 MB at 1280px wide. Provide a poster frame from the same clip. */
  heroVideo: {
    webm: "",   // e.g. "assets/video/hero-1280.webm"
    mp4: "",    // e.g. "assets/video/hero-1280.mp4"
    poster: ""  // e.g. "assets/video/hero-poster.jpg"
  },

  /* Link for "Read More Reviews". */
  reviewsUrl: "https://www.yelp.com/biz/hugo-s-alignment-and-tire-shop-phoenix-5",

  /* GENUINE REVIEWS ONLY.
     Copy reviews word-for-word from the original source, and only ones the
     business has permission to display. Never edit their meaning, never pick
     star ratings that differ from the source, and never write reviews.
     Format:
       {
         name: "Maria G.",               // first name / initial as shown on the source
         rating: 5,                      // 1–5, exactly as on the source
         text: "Exact review text…",
         source: "Yelp",                 // or "Google", etc.
         url: "https://…",               // link to the review or listing
         date: "2026-03-14"              // optional, ISO date
       }
  */
  reviews: []
};

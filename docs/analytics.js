/* Google Analytics for the project page, loaded only after the visitor accepts.
   Nothing is requested from Google before that. The identifier page never loads this file. */
const MEASUREMENT_ID = "G-SLX4XHS15X";
const STORAGE_KEY = "analytics-consent";

function stored() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null; // private windows and blocked storage: ask again each visit
  }
}

function store(choice) {
  try {
    localStorage.setItem(STORAGE_KEY, choice);
  } catch {
    /* the choice then lasts for this page view only */
  }
}

let loaded = false;
function loadAnalytics() {
  if (loaded) return;
  loaded = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag() {
    window.dataLayer.push(arguments);
  };
  window.gtag("js", new Date());
  window.gtag("config", MEASUREMENT_ID);
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${MEASUREMENT_ID}`;
  document.head.append(script);
}

function clearAnalyticsCookies() {
  for (const cookie of document.cookie.split(";")) {
    const name = cookie.split("=")[0].trim();
    if (name === "_ga" || name.startsWith("_ga_")) {
      const host = location.hostname;
      for (const domain of [host, `.${host}`, `.${host.split(".").slice(-2).join(".")}`]) {
        document.cookie = `${name}=; Max-Age=0; path=/; domain=${domain}`;
      }
      document.cookie = `${name}=; Max-Age=0; path=/`;
    }
  }
}

const banner = document.getElementById("analytics-consent");

function decide(choice) {
  store(choice);
  banner.hidden = true;
  if (choice === "granted") {
    loadAnalytics();
  } else {
    clearAnalyticsCookies();
    // A script already loaded keeps running until the page is left; stop it sending.
    window[`ga-disable-${MEASUREMENT_ID}`] = true;
  }
}

document.getElementById("analytics-accept").addEventListener("click", () => decide("granted"));
document.getElementById("analytics-decline").addEventListener("click", () => decide("denied"));
document.getElementById("analytics-settings").addEventListener("click", () => {
  banner.hidden = false;
  document.getElementById("analytics-decline").focus();
});

const choice = stored();
if (choice === "granted") loadAnalytics();
else if (choice !== "denied") banner.hidden = false;

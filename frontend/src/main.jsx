/**
 * Django SSR sahifasiga React vidjetlarini o'rnatadi.
 *
 * Sahifa butunlay serverda render qilinadi. React faqat [data-react]
 * belgisi qo'yilgan bloklarni egallaydi — ular ichidagi HTML esa JS
 * ishlamagan holat uchun ishlaydigan zaxira bo'lib qoladi.
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./widgets.css";
import "./csrf.js"; // tokenni React renderdan oldin ushlab qoladi
import ComplianceCheck from "./ComplianceCheck.jsx";
import EnergyEstimator from "./EnergyEstimator.jsx";
import LeadForm from "./LeadForm.jsx";

function parseJson(raw, fallback) {
  if (!raw) return fallback;
  try {
    return JSON.parse(raw);
  } catch (error) {
    console.warn("[widgets] data-* JSON o'qilmadi", error);
    return fallback;
  }
}

const WIDGETS = {
  "compliance-check": (node) => (
    <ComplianceCheck
      endpoint={node.dataset.endpoint}
      requestUrl={node.dataset.requestUrl}
    />
  ),
  "energy-estimator": (node) => (
    <EnergyEstimator
      ladder={parseJson(node.dataset.ladder, [])}
      threshold={parseInt(node.dataset.threshold || "200", 10)}
      endpoint={node.dataset.endpoint}
    />
  ),
  "lead-form": (node) => (
    <LeadForm
      endpoint={node.dataset.endpoint}
      directions={parseJson(node.dataset.directions, [])}
      maxMb={parseInt(node.dataset.maxMb || "25", 10)}
    />
  ),
};

function mount() {
  document.querySelectorAll("[data-react]").forEach((node) => {
    const build = WIDGETS[node.dataset.react];
    if (!build) return;
    try {
      node.innerHTML = "";
      createRoot(node).render(<StrictMode>{build(node)}</StrictMode>);
    } catch (error) {
      console.error(`[widgets] "${node.dataset.react}" vidjeti ishga tushmadi`, error);
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mount);
} else {
  mount();
}

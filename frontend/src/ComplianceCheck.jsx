import { useState } from "react";
import { t } from "./i18n.js";

/**
 * Talab tekshiruvi — saytning asosiy foydali asbobi.
 *
 * Uch savol: obyekt turi, o'lchamlari, moliyalashtirish. Natijada
 * qaysi majburiyat tegishli ekani, muddati, asosi va mos xizmat
 * ko'rsatiladi. Qoidalar serverda (core/compliance.py) — bu yerda
 * faqat savol berish va natijani hujjat ko'rinishida chizish.
 */

const KINDS = () => [
  { key: "construction", title: t("cc.kind1Title"), note: t("cc.kind1Note") },
  { key: "building", title: t("cc.kind2Title"), note: t("cc.kind2Note") },
  { key: "industrial", title: t("cc.kind3Title"), note: t("cc.kind3Note") },
];

const FUNDING = () => [
  { key: "budget", title: t("cc.fundingBudget") },
  { key: "credit", title: t("cc.fundingCredit") },
  { key: "own", title: t("cc.fundingOwn") },
];

const SEVERITY = () => ({
  required: t("cc.severityRequired"),
  likely: t("cc.severityLikely"),
  optional: t("cc.severityOptional"),
});

export default function ComplianceCheck({ endpoint, requestUrl }) {
  const [step, setStep] = useState(0);
  const [kind, setKind] = useState("");
  const [area, setArea] = useState("");
  const [kwh, setKwh] = useState("");
  const [gas, setGas] = useState("");
  const [estimate, setEstimate] = useState("");
  const [funding, setFunding] = useState("");
  const [dispute, setDispute] = useState(false);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  const kinds = KINDS();
  const fundingOptions = FUNDING();
  const severity = SEVERITY();

  const needsEnergy = kind === "building" || kind === "industrial";
  const needsFunding = kind === "construction";

  async function check() {
    setBusy(true);
    setFailed(false);
    const params = new URLSearchParams({
      object_kind: kind,
      area_m2: area,
      annual_kwh: kwh,
      annual_gas_m3: gas,
      estimate_value: estimate,
      funding: funding,
      has_dispute: dispute ? "1" : "",
    });
    try {
      const response = await fetch(`${endpoint}?${params}`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!response.ok) throw new Error("bad response");
      setResult(await response.json());
      setStep(3);
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }

  function restart() {
    setStep(0); setKind(""); setArea(""); setKwh(""); setGas("");
    setEstimate(""); setFunding(""); setDispute(false);
    setResult(null); setFailed(false);
  }

  const canNext =
    (step === 0 && kind) ||
    (step === 1 && (needsEnergy ? area || kwh || gas : true)) ||
    (step === 2 && (needsFunding ? funding : true));

  const lastStep = 2;

  return (
    <div className="check">
      <div className="check__head">
        <span className="check__label">{t("cc.label")}</span>
        <span className="check__step">
          {step < 3 ? `${step + 1} / ${lastStep + 1}` : t("cc.result")}
        </span>
      </div>

      <div className="check__body">
        {step === 0 && (
          <>
            <p className="check__q">{t("cc.q0")}</p>
            <div className="check__opts">
              {kinds.map((option) => (
                <button
                  key={option.key}
                  type="button"
                  className={`check__opt${kind === option.key ? " is-on" : ""}`}
                  onClick={() => setKind(option.key)}
                >
                  <span className="check__opt-t">{option.title}</span>
                  <span className="check__opt-n">{option.note}</span>
                </button>
              ))}
            </div>
          </>
        )}

        {step === 1 && (
          <>
            <p className="check__q">
              {needsEnergy ? t("cc.q1Energy") : t("cc.q1Value")}
            </p>
            <div className="check__fields">
              {needsEnergy && (
                <>
                  <label className="field">
                    <span className="field__label">{t("common.fieldArea")}</span>
                    <input className="input" type="number" min="1" inputMode="numeric"
                           value={area} onChange={(e) => setArea(e.target.value)}
                           placeholder={t("common.placeholderArea")} />
                  </label>
                  <label className="field">
                    <span className="field__label">{t("cc.fieldKwh")}</span>
                    <input className="input" type="number" min="1" inputMode="numeric"
                           value={kwh} onChange={(e) => setKwh(e.target.value)}
                           placeholder={t("common.placeholderKwh")} />
                  </label>
                  {kind === "industrial" && (
                    <label className="field">
                      <span className="field__label">{t("cc.fieldGas")}</span>
                      <input className="input" type="number" min="1" inputMode="numeric"
                             value={gas} onChange={(e) => setGas(e.target.value)}
                             placeholder={t("cc.placeholderGas")} />
                    </label>
                  )}
                </>
              )}
              {!needsEnergy && (
                <label className="field">
                  <span className="field__label">{t("cc.fieldEstimate")}</span>
                  <input className="input" type="text" inputMode="numeric"
                         value={estimate} onChange={(e) => setEstimate(e.target.value)}
                         placeholder={t("cc.placeholderEstimate")} />
                </label>
              )}
            </div>
            <p className="check__hint">
              {t("cc.hintApprox")}
            </p>
          </>
        )}

        {step === 2 && (
          <>
            <p className="check__q">
              {needsFunding ? t("cc.q2Funding") : t("cc.q2Other")}
            </p>
            {needsFunding && (
              <div className="check__opts check__opts--row">
                {fundingOptions.map((option) => (
                  <button
                    key={option.key}
                    type="button"
                    className={`check__opt${funding === option.key ? " is-on" : ""}`}
                    onClick={() => setFunding(option.key)}
                  >
                    <span className="check__opt-t">{option.title}</span>
                  </button>
                ))}
              </div>
            )}
            <label className="check__toggle">
              <input type="checkbox" checked={dispute}
                     onChange={(e) => setDispute(e.target.checked)} />
              <span>{t("cc.disputeLabel")}</span>
            </label>
          </>
        )}

        {step === 3 && result && (
          <div className="check__result">
            {result.energy_category && (
              <div className="check__cat">
                <span className="check__cat-v">{result.energy_category}</span>
                <span className="check__cat-k">
                  {t("cc.resultCatLabel", { specific: result.specific_kwh })}
                </span>
              </div>
            )}

            {result.requirements.length > 0 && (
              <ol className="reqs">
                {result.requirements.map((item) => (
                  <li className="reqs__r" key={item.key}>
                    <div className="reqs__top">
                      <span className="reqs__t">{item.title}</span>
                      <span className={`reqs__sev reqs__sev--${item.severity}`}>
                        {severity[item.severity] || item.severity}
                      </span>
                    </div>
                    <p className="reqs__n">{item.note}</p>
                    <div className="reqs__meta">
                      <span><b>{t("cc.basisLabel")}</b> {item.basis}</span>
                      <span><b>{t("cc.deadlineLabel")}</b> {item.deadline}</span>
                      {item.service_url && (
                        <a href={item.service_url}>{item.service_title} &rarr;</a>
                      )}
                    </div>
                  </li>
                ))}
              </ol>
            )}

            {result.notes.map((note, index) => (
              <p className="check__hint" key={index}>{note}</p>
            ))}

            <p className="check__hint check__hint--legal">
              {t("cc.legalHint")}
            </p>
          </div>
        )}

        {failed && (
          <p className="check__hint check__hint--err">
            {t("cc.failed")}
          </p>
        )}
      </div>

      <div className="check__foot">
        {step > 0 && step < 3 && (
          <button type="button" className="check__back" onClick={() => setStep(step - 1)}>
            {t("common.back")}
          </button>
        )}
        {step < lastStep && (
          <button type="button" className="btn" disabled={!canNext}
                  onClick={() => setStep(step + 1)}>
            {t("cc.next")}
          </button>
        )}
        {step === lastStep && (
          <button type="button" className="btn" disabled={!canNext || busy} onClick={check}>
            {busy ? t("cc.checking") : t("cc.check")}
          </button>
        )}
        {step === 3 && (
          <>
            <button type="button" className="check__back" onClick={restart}>
              {t("cc.restart")}
            </button>
            <a className="btn" href={requestUrl}>{t("common.sendRequest")}</a>
          </>
        )}
      </div>
    </div>
  );
}

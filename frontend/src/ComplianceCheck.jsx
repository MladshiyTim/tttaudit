import { useState } from "react";

/**
 * Talab tekshiruvi — saytning asosiy foydali asbobi.
 *
 * Uch savol: obyekt turi, o'lchamlari, moliyalashtirish. Natijada
 * qaysi majburiyat tegishli ekani, muddati, asosi va mos xizmat
 * ko'rsatiladi. Qoidalar serverda (core/compliance.py) — bu yerda
 * faqat savol berish va natijani hujjat ko'rinishida chizish.
 */

const KINDS = [
  { key: "construction", title: "Qurilish obyekti",
    note: "Qurilayotgan yoki topshirilgan bino, yoʻl, tarmoq" },
  { key: "building", title: "Foydalanishdagi bino",
    note: "Maʼmuriy, tijorat, turar-joy yoki byudjet binosi" },
  { key: "industrial", title: "Sanoat korxonasi",
    note: "Ishlab chiqarish, energiya isteʼmoli katta obyekt" },
];

const FUNDING = [
  { key: "budget", title: "Byudjet mablagʻi" },
  { key: "credit", title: "Bank krediti" },
  { key: "own", title: "Oʻz mablagʻi" },
];

const SEVERITY = {
  required: "Majburiy",
  likely: "Odatda talab qilinadi",
  optional: "Ixtiyoriy",
};

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
        <span className="check__label">Talab tekshiruvi</span>
        <span className="check__step">
          {step < 3 ? `${step + 1} / ${lastStep + 1}` : "Natija"}
        </span>
      </div>

      <div className="check__body">
        {step === 0 && (
          <>
            <p className="check__q">Obyekt qanday?</p>
            <div className="check__opts">
              {KINDS.map((option) => (
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
              {needsEnergy ? "Oʻlcham va isteʼmol" : "Obyekt qiymati"}
            </p>
            <div className="check__fields">
              {needsEnergy && (
                <>
                  <label className="field">
                    <span className="field__label">Foydali maydon, m²</span>
                    <input className="input" type="number" min="1" inputMode="numeric"
                           value={area} onChange={(e) => setArea(e.target.value)}
                           placeholder="1 200" />
                  </label>
                  <label className="field">
                    <span className="field__label">Yillik elektr, kVt·soat</span>
                    <input className="input" type="number" min="1" inputMode="numeric"
                           value={kwh} onChange={(e) => setKwh(e.target.value)}
                           placeholder="140 000" />
                  </label>
                  {kind === "industrial" && (
                    <label className="field">
                      <span className="field__label">Yillik gaz, m³</span>
                      <input className="input" type="number" min="1" inputMode="numeric"
                             value={gas} onChange={(e) => setGas(e.target.value)}
                             placeholder="380 000" />
                    </label>
                  )}
                </>
              )}
              {!needsEnergy && (
                <label className="field">
                  <span className="field__label">Smeta qiymati, soʻm</span>
                  <input className="input" type="text" inputMode="numeric"
                         value={estimate} onChange={(e) => setEstimate(e.target.value)}
                         placeholder="12 400 000 000" />
                </label>
              )}
            </div>
            <p className="check__hint">
              Aniq raqam boʻlmasa taxminini kiriting — natija yoʻnaltiruvchi.
            </p>
          </>
        )}

        {step === 2 && (
          <>
            <p className="check__q">
              {needsFunding ? "Moliyalashtirish manbai" : "Qoʻshimcha holat"}
            </p>
            {needsFunding && (
              <div className="check__opts check__opts--row">
                {FUNDING.map((option) => (
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
              <span>Obyekt boʻyicha nizo bor yoki sudga chiqqan</span>
            </label>
          </>
        )}

        {step === 3 && result && (
          <div className="check__result">
            {result.energy_category && (
              <div className="check__cat">
                <span className="check__cat-v">{result.energy_category}</span>
                <span className="check__cat-k">
                  {result.specific_kwh} kVt·soat / m² · yil — dastlabki toifa
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
                        {SEVERITY[item.severity] || item.severity}
                      </span>
                    </div>
                    <p className="reqs__n">{item.note}</p>
                    <div className="reqs__meta">
                      <span><b>Asos:</b> {item.basis}</span>
                      <span><b>Muddat:</b> {item.deadline}</span>
                      {item.service_url && (
                        <a href={item.service_url}>{item.service_title} &rarr;</a>
                      )}
                    </div>
                  </li>
                ))}
              </ol>
            )}

            {result.estimated_fee && (
              <p className="check__hint">
                Nazorat oʻlchovi xizmat haqi chegarasi: <b>{result.estimated_fee} soʻm</b>
                {" "}(qurilish qiymatining 0,3%).
              </p>
            )}

            {result.notes.map((note, index) => (
              <p className="check__hint" key={index}>{note}</p>
            ))}

            <p className="check__hint check__hint--legal">
              Bu dastlabki yoʻnaltiruvchi baho. Rasmiy javob obyekt hujjatlari
              koʻrilgandan soʻng beriladi.
            </p>
          </div>
        )}

        {failed && (
          <p className="check__hint check__hint--err">
            Tekshiruv bajarilmadi. Internet aloqasini tekshiring yoki soʻrov qoldiring.
          </p>
        )}
      </div>

      <div className="check__foot">
        {step > 0 && step < 3 && (
          <button type="button" className="check__back" onClick={() => setStep(step - 1)}>
            &larr; Orqaga
          </button>
        )}
        {step < lastStep && (
          <button type="button" className="btn" disabled={!canNext}
                  onClick={() => setStep(step + 1)}>
            Keyingi
          </button>
        )}
        {step === lastStep && (
          <button type="button" className="btn" disabled={!canNext || busy} onClick={check}>
            {busy ? "Tekshirilmoqda…" : "Tekshirish"}
          </button>
        )}
        {step === 3 && (
          <>
            <button type="button" className="check__back" onClick={restart}>
              &larr; Qaytadan
            </button>
            <a className="btn" href={requestUrl}>Soʻrov yuborish</a>
          </>
        )}
      </div>
    </div>
  );
}

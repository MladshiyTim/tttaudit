import { useEffect, useState } from "react";
import { t } from "./i18n.js";

/**
 * Dastlabki baholash: maydon + yillik iste'mol -> A..G toifasi.
 *
 * Hisob serverda turadi (core/energy.py), chunki chegaralar me'yoriy
 * hujjatdan keladi va bitta manbada bo'lishi shart. Vidjet faqat
 * ko'rsatadi. JS o'chiq bo'lsa SSR dagi statik shkala joyida qoladi.
 */
export default function EnergyEstimator({ ladder, threshold, endpoint }) {
  const [area, setArea] = useState("");
  const [kwh, setKwh] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const areaNum = parseFloat(area);
  const kwhNum = parseFloat(kwh);
  const ready = areaNum > 0 && kwhNum > 0;

  useEffect(() => {
    if (!ready) {
      setResult(null);
      return undefined;
    }

    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setBusy(true);
      try {
        const url = `${endpoint}?area=${encodeURIComponent(areaNum)}&kwh=${encodeURIComponent(kwhNum)}`;
        const response = await fetch(url, {
          signal: controller.signal,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (!response.ok) throw new Error("bad response");
        setResult(await response.json());
      } catch (error) {
        if (error.name !== "AbortError") setResult(null);
      } finally {
        setBusy(false);
      }
    }, 250);

    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [areaNum, kwhNum, ready, endpoint]);

  // Natija yo'q ekan — shkala o'lik kulrang blok bo'lib qolmasligi uchun
  // o'rtacha toifa namuna sifatida yoritiladi.
  const active = result && result.ok ? result.category : "D";
  const isSample = !(result && result.ok);

  return (
    <>
      <div className="ladder">
        {ladder.map((band) => (
          <div
            key={band.letter}
            className={
              `ladder__row${band.letter === active ? " is-on" : ""}` +
              (isSample && band.letter === active ? " is-sample" : "")
            }
          >
            <span className="ladder__l">{band.letter}</span>
            <span className="ladder__bar" style={{ width: `${band.width}%` }} />
            <span className="ladder__kwh">{band.label}</span>
          </div>
        ))}
      </div>

      <div className="est">
        <div className="est__head">{t("ee.head")}</div>
        <div className="est__body">
          <div className="est__fields">
            <label className="field">
              <span className="field__label">{t("common.fieldArea")}</span>
              <input
                className="input"
                type="number"
                min="1"
                inputMode="numeric"
                value={area}
                onChange={(event) => setArea(event.target.value)}
                placeholder={t("common.placeholderArea")}
              />
            </label>
            <label className="field">
              <span className="field__label">{t("common.fieldKwhConsumption")}</span>
              <input
                className="input"
                type="number"
                min="1"
                inputMode="numeric"
                value={kwh}
                onChange={(event) => setKwh(event.target.value)}
                placeholder={t("common.placeholderKwh")}
              />
            </label>
          </div>

          {ready && result && result.ok ? (
            <div className="est__out">
              <span className="est__cat">{result.category}</span>
              <span className="est__val nums">
                {result.specific} {t("ee.unit")}
              </span>
            </div>
          ) : null}

          <p className={`est__note${result && result.passport_required ? " est__note--flag" : ""}`}>
            {busy
              ? t("ee.busy")
              : result && result.ok
                ? result.passport_required
                  ? t("ee.aboveThreshold", { threshold })
                  : t("ee.belowThreshold", { threshold })
                : t("ee.fallback")}
          </p>
        </div>
      </div>
    </>
  );
}

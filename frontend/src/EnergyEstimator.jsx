import { useEffect, useState } from "react";

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
        <div className="est__head">Dastlabki baholash</div>
        <div className="est__body">
          <div className="est__fields">
            <label className="field">
              <span className="field__label">Foydali maydon, m²</span>
              <input
                className="input"
                type="number"
                min="1"
                inputMode="numeric"
                value={area}
                onChange={(event) => setArea(event.target.value)}
                placeholder="1 200"
              />
            </label>
            <label className="field">
              <span className="field__label">Yillik isteʼmol, kVt·soat</span>
              <input
                className="input"
                type="number"
                min="1"
                inputMode="numeric"
                value={kwh}
                onChange={(event) => setKwh(event.target.value)}
                placeholder="140 000"
              />
            </label>
          </div>

          {ready && result && result.ok ? (
            <div className="est__out">
              <span className="est__cat">{result.category}</span>
              <span className="est__val nums">
                {result.specific} kVt·soat / m² · yil
              </span>
            </div>
          ) : null}

          <p className={`est__note${result && result.passport_required ? " est__note--flag" : ""}`}>
            {busy
              ? "Hisoblanmoqda…"
              : result && result.ok
                ? result.passport_required
                  ? `Foydali maydon ${threshold} m² dan katta — binoga energopasport talab qilinadi.`
                  : `Foydali maydon ${threshold} m² dan kichik — energopasport talabi tegishli emas.`
                : "Ikki qiymatni kiriting — toifa darhol koʻrsatiladi. Bu dastlabki baho, rasmiy energopasport toʻliq audit natijasida beriladi."}
          </p>
        </div>
      </div>
    </>
  );
}

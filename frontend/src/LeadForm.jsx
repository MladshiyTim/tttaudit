import { useMemo, useState } from "react";
import { csrfToken } from "./csrf.js";

const REGIONS = [
  "Toshkent shahri",
  "Toshkent viloyati",
  "Andijon",
  "Buxoro",
  "Fargʻona",
  "Jizzax",
  "Xorazm",
  "Namangan",
  "Navoiy",
  "Qashqadaryo",
  "Qoraqalpogʻiston",
  "Samarqand",
  "Sirdaryo",
  "Surxondaryo",
];

const ALLOWED = [
  ".pdf", ".xlsx", ".xls", ".docx", ".doc",
  ".dwg", ".zip", ".rar", ".jpg", ".jpeg", ".png",
];

const EMPTY = {
  direction: "",
  object_type: "",
  region: "",
  area_m2: "",
  annual_kwh: "",
  estimate_value: "",
  urgency: "planned",
  name: "",
  phone: "",
  email: "",
  note: "",
};

/**
 * So'rov formasi. Yo'nalishga qarab maydonlar o'zgaradi:
 * energoaudit -> maydon va yillik iste'mol, o'lchov auditi -> smeta qiymati.
 */
export default function LeadForm({ endpoint, directions, maxMb }) {
  const [values, setValues] = useState(EMPTY);
  const [file, setFile] = useState(null);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(null);

  const accent = useMemo(() => {
    const found = directions.find((d) => String(d.id) === String(values.direction));
    return found ? found.accent : null;
  }, [directions, values.direction]);

  function set(field, value) {
    setValues((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function onFile(event) {
    const picked = event.target.files && event.target.files[0];
    if (!picked) {
      setFile(null);
      return;
    }
    const extension = picked.name.slice(picked.name.lastIndexOf(".")).toLowerCase();
    if (!ALLOWED.includes(extension)) {
      setErrors((prev) => ({
        ...prev,
        attachment: [`Bu fayl turi qabul qilinmaydi. Ruxsat etilgan: ${ALLOWED.join(", ")}`],
      }));
      event.target.value = "";
      setFile(null);
      return;
    }
    if (picked.size > maxMb * 1024 * 1024) {
      setErrors((prev) => ({
        ...prev,
        attachment: [`Fayl hajmi ${maxMb} MB dan oshmasligi kerak.`],
      }));
      event.target.value = "";
      setFile(null);
      return;
    }
    setErrors((prev) => {
      const next = { ...prev };
      delete next.attachment;
      return next;
    });
    setFile(picked);
  }

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setFormError("");

    const payload = new FormData();
    Object.entries(values).forEach(([key, value]) => {
      if (value !== "" && value !== null) payload.append(key, value);
    });
    if (file) payload.append("attachment", file);

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        body: payload,
        headers: {
          "X-CSRFToken": csrfToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
      });
      const data = await response.json();
      if (data.ok) {
        setDone(data.message);
      } else {
        setErrors(data.errors || {});
        setFormError(data.error || "Formada xatolik bor — belgilangan maydonlarni tekshiring.");
      }
    } catch (error) {
      setFormError(
        "Soʻrov yuborilmadi. Internet aloqasini tekshiring yoki telefon orqali bogʻlaning."
      );
    } finally {
      setBusy(false);
    }
  }

  if (done) {
    return (
      <div className="form-done">
        <span className="form-done__t">Soʻrov qabul qilindi</span>
        <p className="form-done__d">{done}</p>
      </div>
    );
  }

  const err = (field) => (errors[field] ? <span className="field__err">{errors[field][0]}</span> : null);

  return (
    <form className="form" onSubmit={onSubmit} noValidate>
      {formError ? <div className="form-error">{formError}</div> : null}

      <label className="field">
        <span className="field__label">Yoʻnalish</span>
        <select
          className="select"
          value={values.direction}
          onChange={(event) => set("direction", event.target.value)}
        >
          <option value="">Tanlang</option>
          {directions.map((direction) => (
            <option key={direction.id} value={direction.id}>
              {direction.title}
            </option>
          ))}
        </select>
        {err("direction")}
      </label>

      <label className="field">
        <span className="field__label">Obyekt turi</span>
        <input
          className="input"
          type="text"
          value={values.object_type}
          onChange={(event) => set("object_type", event.target.value)}
          placeholder="Maʼmuriy bino, sex, maktab…"
        />
        {err("object_type")}
      </label>

      <label className="field">
        <span className="field__label">Viloyat</span>
        <select
          className="select"
          value={values.region}
          onChange={(event) => set("region", event.target.value)}
        >
          <option value="">Tanlang</option>
          {REGIONS.map((region) => (
            <option key={region} value={region}>{region}</option>
          ))}
        </select>
        {err("region")}
      </label>

      {accent === "amber" ? (
        <>
          <label className="field">
            <span className="field__label">Foydali maydon, m²</span>
            <input
              className="input"
              type="number"
              min="1"
              inputMode="numeric"
              value={values.area_m2}
              onChange={(event) => set("area_m2", event.target.value)}
              placeholder="1 200"
            />
            {err("area_m2")}
          </label>
          <label className="field">
            <span className="field__label">Yillik isteʼmol, kVt·soat</span>
            <input
              className="input"
              type="number"
              min="1"
              inputMode="numeric"
              value={values.annual_kwh}
              onChange={(event) => set("annual_kwh", event.target.value)}
              placeholder="140 000"
            />
            {err("annual_kwh")}
          </label>
        </>
      ) : null}

      {accent === "steel" ? (
        <label className="field">
          <span className="field__label">Smeta qiymati</span>
          <input
            className="input"
            type="text"
            value={values.estimate_value}
            onChange={(event) => set("estimate_value", event.target.value)}
            placeholder="12,4 mlrd soʻm"
          />
          {err("estimate_value")}
        </label>
      ) : null}

      <div className="field form__full">
        <span className="field__label">Muddat</span>
        <div className="radios">
          <label>
            <input
              type="radio"
              name="urgency"
              value="planned"
              checked={values.urgency === "planned"}
              onChange={(event) => set("urgency", event.target.value)}
            />
            Rejali
          </label>
          <label>
            <input
              type="radio"
              name="urgency"
              value="urgent"
              checked={values.urgency === "urgent"}
              onChange={(event) => set("urgency", event.target.value)}
            />
            Shoshilinch
          </label>
        </div>
      </div>

      <label className="field">
        <span className="field__label">
          Ism <span className="field__req">*</span>
        </span>
        <input
          className="input"
          type="text"
          required
          value={values.name}
          onChange={(event) => set("name", event.target.value)}
        />
        {err("name")}
      </label>

      <label className="field">
        <span className="field__label">
          Telefon <span className="field__req">*</span>
        </span>
        <input
          className="input"
          type="tel"
          required
          value={values.phone}
          onChange={(event) => set("phone", event.target.value)}
          placeholder="+998 90 000 00 00"
        />
        {err("phone")}
      </label>

      <label className="field">
        <span className="field__label">E-pochta</span>
        <input
          className="input"
          type="email"
          value={values.email}
          onChange={(event) => set("email", event.target.value)}
        />
        {err("email")}
      </label>

      <div className="field form__full">
        <span className="field__label">Hujjat biriktirish</span>
        <div className="file">
          <input type="file" onChange={onFile} accept={ALLOWED.join(",")} />
          <span className="file__hint">
            {file ? file.name : `SMETA · f-2 · ENERGIYA HISOBI · ${maxMb} MB GACHA`}
          </span>
        </div>
        {err("attachment")}
      </div>

      <label className="field form__full">
        <span className="field__label">Izoh</span>
        <textarea
          className="textarea"
          value={values.note}
          onChange={(event) => set("note", event.target.value)}
          placeholder="Obyekt holati, muddat, nizo bormi…"
        />
        {err("note")}
      </label>

      <div className="form__foot">
        <button className="btn" type="submit" disabled={busy}>
          {busy ? "Yuborilmoqda…" : "Soʻrov yuborish"}
        </button>
        <p className="form__privacy">
          Yuborilgan hujjatlar uchinchi shaxsga berilmaydi. Bir ish kuni ichida
          muhandis bogʻlanadi, dastlabki baholash bepul.
        </p>
      </div>
    </form>
  );
}

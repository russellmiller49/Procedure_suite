export type Ymd = {
  year: number;
  month: number;
  day: number;
};

const ISO_YMD_RE = /^(\d{4})-(\d{2})-(\d{2})$/;
const MS_PER_DAY = 24 * 60 * 60 * 1000;

export function parseIsoYmd(value: string | null | undefined): Ymd | null {
  const raw = String(value ?? "").trim();
  const m = ISO_YMD_RE.exec(raw);
  if (!m) return null;
  const ymd = { year: Number(m[1]), month: Number(m[2]), day: Number(m[3]) };
  const ms = Date.UTC(ymd.year, ymd.month - 1, ymd.day, 12, 0, 0, 0);
  const d = new Date(ms);
  if (
    d.getUTCFullYear() !== ymd.year ||
    d.getUTCMonth() !== ymd.month - 1 ||
    d.getUTCDate() !== ymd.day
  ) {
    return null;
  }
  return ymd;
}

function utcNoonMs(ymd: Ymd): number {
  return Date.UTC(ymd.year, ymd.month - 1, ymd.day, 12, 0, 0, 0);
}

export function calculateDayOffset(
  indexDate: string | null | undefined,
  eventDate: string | null | undefined,
): number | null {
  const indexYmd = parseIsoYmd(indexDate);
  const eventYmd = parseIsoYmd(eventDate);
  if (!indexYmd || !eventYmd) return null;
  return Math.round((utcNoonMs(eventYmd) - utcNoonMs(indexYmd)) / MS_PER_DAY);
}


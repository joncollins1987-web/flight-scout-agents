export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
}

export function formatMinutes(value: number): string {
  const hours = Math.floor(value / 60);
  const minutes = value % 60;
  return `${hours}h ${minutes}m`;
}

export function formatDateTime(value: string): string {
  return new Date(value).toLocaleString();
}

export function formatDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

export function formatMonthLabel(monthKey: string): string {
  const [year, month] = monthKey.split("-").map(Number);
  return new Date(year, month - 1, 1).toLocaleDateString("en-US", {
    month: "short",
    year: "numeric",
  });
}

export function formatDayChip(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-US", {
    weekday: "short",
    day: "numeric",
  });
}

export function listSummary(values: string[], fallback = "Not set"): string {
  return values.length ? values.join(", ") : fallback;
}

export function readableTime(value: string): string {
  if (!value) return "Any";
  const [hours, minutes] = value.split(":");
  const parsedHours = Number(hours);
  const suffix = parsedHours >= 12 ? "PM" : "AM";
  const displayHour = parsedHours % 12 || 12;
  return `${displayHour}:${minutes} ${suffix}`;
}

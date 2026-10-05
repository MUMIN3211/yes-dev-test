// Must stay in sync with supabase/schema.sql (CHECK) and backend/app/schemas/product.py (Category)
export const CATEGORIES = ["Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen", "Mask"];

export const PLACEHOLDER_IMAGE = "/placeholder-product.svg";

const formatOptions = { style: "currency", currency: "THB" };
const wholeFormatter = new Intl.NumberFormat("th-TH", { ...formatOptions, maximumFractionDigits: 0 });
const decimalFormatter = new Intl.NumberFormat("th-TH", { ...formatOptions, minimumFractionDigits: 2 });

// ฿390 for whole prices, ฿890.50 otherwise
export function formatPrice(value) {
  const n = Number(value);
  return (Number.isInteger(n) ? wholeFormatter : decimalFormatter).format(n);
}

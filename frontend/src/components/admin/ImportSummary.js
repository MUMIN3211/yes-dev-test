import { formatPrice } from "@/lib/constants";
import styles from "./admin.module.css";
import productStyles from "./products.module.css";

const ACTION_LABELS = {
  create: { label: "เพิ่มใหม่", className: styles.badge },
  update: { label: "อัปเดต", className: styles.badgeAccent },
  unchanged: { label: "ไม่เปลี่ยนแปลง", className: styles.badgeMuted },
};

function formatValue(field, value) {
  if (value === null || value === undefined || value === "") return "(ว่าง)";
  return field === "price" ? formatPrice(value) : String(value);
}

function IssueTable({ issues, isError }) {
  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>แถว</th>
            <th>SKU</th>
            <th>{isError ? "เหตุผลที่ไม่นำเข้า" : "สิ่งที่ระบบปรับให้"}</th>
          </tr>
        </thead>
        <tbody>
          {issues.map((issue) => (
            <tr key={issue.row}>
              <td>{issue.row}</td>
              <td className={productStyles.mono}>{issue.sku ?? "—"}</td>
              <td>
                {issue.messages.map((m) => (
                  <div key={m} className={isError ? productStyles.errorText : undefined}>
                    {m}
                  </div>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Shows the backend's ImportResult: counts, rejected rows, auto-fixes and per-row changes.
export default function ImportSummary({ result }) {
  const stats = [
    { label: "แถวข้อมูล", value: result.total_rows },
    { label: "เพิ่มใหม่", value: result.created },
    { label: "อัปเดต", value: result.updated },
    { label: "ไม่เปลี่ยนแปลง", value: result.unchanged },
    { label: "ข้อมูลไม่ถูกต้อง", value: result.failed, danger: result.failed > 0 },
  ];

  return (
    <div className={productStyles.summary}>
      <p className={styles.subtle}>
        {result.dry_run ? "ตัวอย่าง (ยังไม่บันทึก)" : "ผลการนำเข้า"}: <strong>{result.file_name}</strong>
      </p>

      <div className={productStyles.stats}>
        {stats.map((s) => (
          <div key={s.label} className={s.danger ? productStyles.statDanger : productStyles.stat}>
            <span className={productStyles.statValue}>{s.value}</span>
            <span className={productStyles.statLabel}>{s.label}</span>
          </div>
        ))}
      </div>

      {result.errors.length > 0 && (
        <div>
          <h3 className={productStyles.subheading}>
            แถวที่ข้อมูลไม่ถูกต้อง ({result.errors.length}) จะไม่ถูกนำเข้า กรุณาแก้ในไฟล์แล้วนำเข้าใหม่
          </h3>
          <IssueTable issues={result.errors} isError />
        </div>
      )}

      {result.warnings.length > 0 && (
        <div>
          <h3 className={productStyles.subheading}>แถวที่ระบบปรับข้อมูลให้อัตโนมัติ ({result.warnings.length})</h3>
          <IssueTable issues={result.warnings} />
        </div>
      )}

      {result.rows.length > 0 && (
        <div>
          <h3 className={productStyles.subheading}>แถวที่ถูกต้อง ({result.rows.length})</h3>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>แถว</th>
                  <th>SKU</th>
                  <th>ชื่อสินค้า</th>
                  <th>ผลลัพธ์</th>
                  <th>สิ่งที่เปลี่ยน</th>
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row) => {
                  const action = ACTION_LABELS[row.action];
                  return (
                    <tr key={row.row}>
                      <td>{row.row}</td>
                      <td className={productStyles.mono}>{row.sku}</td>
                      <td>{row.name}</td>
                      <td>
                        <span className={action.className}>{action.label}</span>
                      </td>
                      <td className={productStyles.changes}>
                        {row.changes.length === 0
                          ? "—"
                          : row.changes.map((c) => (
                              <div key={c.field}>
                                <strong>{c.field}</strong>: {formatValue(c.field, c.old)} →{" "}
                                {formatValue(c.field, c.new)}
                              </div>
                            ))}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

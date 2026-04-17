import { useState, useMemo, type ReactNode } from 'react';
import { Inbox } from 'lucide-react';
import styles from './DataTable.module.css';

// ───────────────── Types ─────────────────

export interface Column<T> {
  /** Object key or unique identifier */
  key: string;
  /** Display label in header */
  label: string;
  /** Text alignment */
  align?: 'left' | 'center' | 'right';
  /** Whether column is sortable (default: false) */
  sortable?: boolean;
  /** Custom cell renderer — if omitted, the raw value is displayed */
  render?: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  /** Column definitions */
  columns: Column<T>[];
  /** Row data */
  data: T[];
  /** Unique key extractor per row */
  rowKey: (row: T) => string | number;
  /** Optional card title */
  title?: string;
  /** Optional subtitle */
  subtitle?: string;
  /** Text shown when data is empty */
  emptyText?: string;
  /** Additional className for root container */
  className?: string;
}

// ───────────────── Helpers ─────────────────

type SortDirection = 'asc' | 'desc';

function getNestedValue<T>(row: T, key: string): unknown {
  // handles flat keys like "name" and dot-paths like "evaluation.score"
  return key.split('.').reduce<unknown>((acc, part) => {
    if (acc && typeof acc === 'object') return (acc as Record<string, unknown>)[part];
    return undefined;
  }, row);
}

function compare(a: unknown, b: unknown, dir: SortDirection): number {
  const mult = dir === 'asc' ? 1 : -1;
  if (a == null && b == null) return 0;
  if (a == null) return mult;
  if (b == null) return -mult;
  if (typeof a === 'number' && typeof b === 'number') return (a - b) * mult;
  return String(a).localeCompare(String(b)) * mult;
}

// ───────────────── Component ─────────────────

export function DataTable<T>({
  columns,
  data,
  rowKey,
  title,
  subtitle,
  emptyText = 'No data available.',
  className = '',
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDirection>('asc');

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) =>
      compare(getNestedValue(a, sortKey), getNestedValue(b, sortKey), sortDir)
    );
  }, [data, sortKey, sortDir]);

  const alignClass = (align?: string) => {
    if (align === 'center') return styles.alignCenter;
    if (align === 'right') return styles.alignRight;
    return '';
  };

  return (
    <div className={`${styles.tableContainer} ${className}`}>
      {(title || subtitle) && (
        <div className={styles.header}>
          <div>
            {title && <h3 className={styles.title}>{title}</h3>}
            {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
          </div>
        </div>
      )}

      {data.length === 0 ? (
        <div className={styles.emptyState}>
          <Inbox className={styles.emptyIcon} size={40} />
          <p className={styles.emptyText}>{emptyText}</p>
        </div>
      ) : (
        <div className={styles.scrollWrap}>
          <table className={styles.table}>
            <thead className={styles.thead}>
              <tr>
                {columns.map((col) => {
                  const isSorted = sortKey === col.key;
                  const thClasses = [
                    styles.th,
                    alignClass(col.align),
                    col.sortable ? styles.thSortable : '',
                    isSorted ? styles.thSortActive : '',
                  ]
                    .filter(Boolean)
                    .join(' ');

                  return (
                    <th
                      key={col.key}
                      className={thClasses}
                      onClick={col.sortable ? () => handleSort(col.key) : undefined}
                    >
                      {col.label}
                      {col.sortable && (
                        <span className={styles.sortIcon}>
                          {isSorted ? (sortDir === 'asc' ? '▲' : '▼') : '⇅'}
                        </span>
                      )}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody className={styles.tbody}>
              {sortedData.map((row) => (
                <tr key={rowKey(row)}>
                  {columns.map((col) => (
                    <td key={col.key} className={`${styles.td} ${alignClass(col.align)}`}>
                      {col.render
                        ? col.render(row)
                        : String(getNestedValue(row, col.key) ?? '-')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

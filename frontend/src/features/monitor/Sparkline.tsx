const WIDTH = 100;
const HEIGHT = 40;

/** Линия последних показаний, растянутая по ширине контейнера. */
export function Sparkline({ values }: { values: number[] }) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = WIDTH / Math.max(1, values.length - 1);
  const points = values
    .map((value, index) => `${index * step},${HEIGHT - ((value - min) / range) * HEIGHT}`)
    .join(' ');

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      preserveAspectRatio="none"
      width="100%"
      height={64}
      role="img"
      aria-label="График показаний"
    >
      <polyline
        points={points}
        fill="none"
        stroke="currentColor"
        strokeWidth={1.5}
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

export function escapeJsonPointerSegment(segment: string): string {
  return segment.replace(/~/g, "~0").replace(/\//g, "~1");
}

export function joinJsonPointer(basePointer: string, segment: string): string {
  const base = basePointer === "" ? "" : basePointer;
  return `${base}/${escapeJsonPointerSegment(segment)}`;
}


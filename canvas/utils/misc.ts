export function countWords(text: string) {
  let count = 0;
  const regex = /\b\w+\b/g;
  while (regex.exec(text)) {
    count++;
  }
  return count;
}

export function snakeCaseTitleCase(str: string): string {
  return str.replace(/^_*(.)|_+(.)/g, (_, c, d) =>
    c ? c.toUpperCase() : " " + d.toUpperCase(),
  );
}

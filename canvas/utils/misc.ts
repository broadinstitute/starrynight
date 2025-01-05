export function countWords(text: string) {
  let count = 0;
  const regex = /\b\w+\b/g;
  while (regex.exec(text)) {
    count++;
  }
  return count;
}

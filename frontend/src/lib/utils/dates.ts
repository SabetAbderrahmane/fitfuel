export function formatDate(value: string | Date) {
  return new Date(value).toLocaleDateString();
}

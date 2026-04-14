export function EmptyState({ message = "Nothing here yet." }: { message?: string }) {
  return <div className="text-sm text-white/60">{message}</div>;
}

export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return <div className="text-sm text-white/70">{label}</div>;
}

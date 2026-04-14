export function ErrorState({ message = "Something went wrong." }: { message?: string }) {
  return <div className="text-sm text-red-300">{message}</div>;
}

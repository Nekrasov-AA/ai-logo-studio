export default function GenerateLayout({ children }: { children: React.ReactNode }) {
  return (
    <section style={{ padding: 24, maxWidth: 720, margin: '0 auto' }}>
      {children}
    </section>
  );
}

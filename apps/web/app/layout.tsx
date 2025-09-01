import '../styles/globals.css'
import Nav from "../components/Nav"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <main className="max-w-6xl mx-auto p-6">
          <Nav />
          {children}
        </main>
      </body>
    </html>
  );
}

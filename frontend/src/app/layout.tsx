import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Kantata Reddit Intelligence',
  description: 'Find ICP-fit companies and buyer signals from Reddit data',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50 text-gray-900 antialiased`}>
        <header className="border-b bg-white px-6 py-4">
          <div className="mx-auto flex max-w-7xl items-center justify-between">
            <div>
              <span className="text-xs font-semibold uppercase tracking-widest text-indigo-600">
                Kantata
              </span>
              <h1 className="text-lg font-bold leading-tight">Reddit Intelligence</h1>
            </div>
            <nav className="flex gap-6 text-sm font-medium text-gray-500">
              <a href="/" className="hover:text-gray-900">
                Dashboard
              </a>
              <a href="/import" className="hover:text-gray-900">
                Import
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  )
}

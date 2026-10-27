import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'Legal Metrology AI Compliance Platform | SIH26034',
  description: 'AI-Powered Legal Metrology Compliance & Inspection Platform for Packaged Commodities Rules 2011',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#f6f5f4] text-[#000000] flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="bg-white border-t border-[#e6e6e6] py-6 text-center text-xs text-[#615d59]">
          <p>© 2026 Department of Consumer Affairs • Legal Metrology Division • SIH26034 Platform</p>
        </footer>
      </body>
    </html>
  );
}

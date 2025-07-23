// --- START OF FILE src/app/layout.tsx ---
import type { Metadata } from "next";
import { inter, cormorant } from "./fonts";
import "./globals.css";
import Footer from "@/components/Footer"; // Summoning the Footer component we just built.

export const metadata: Metadata = {
  title: "Saga - The Oracle of Strategy",
  description: "Strategy is an Art. I am its Master.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${cormorant.variable}`}>
        {/* 
          We wrap the main content and the footer in a flex container
          that ensures the footer is always at the bottom of the content,
          or at the bottom of the screen on short pages.
        */}
        <div className="flex flex-col min-h-screen">
          <main className="flex-grow">
            {children}
          </main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
// --- END OF FILE src/app/layout.tsx ---
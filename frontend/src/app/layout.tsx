import type { Metadata } from "next";
import { inter, cormorant } from "./fonts";
import "./globals.css";

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
        {children}
      </body>
    </html>
  );
}
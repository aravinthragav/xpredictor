import "./globals.css";
import React from "react";

export const metadata = {
  title: "XPredictor - Shazam for Candlesticks",
  description: "Vectorized Price-Action Search Engine & Hybrid Reality Cone Terminal",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-gray-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}

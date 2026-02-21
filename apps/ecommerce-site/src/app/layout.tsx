import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "GeekendZone — Your Trusted Tech Partner",
    template: "%s | GeekendZone",
  },
  description: "Premium computer hardware, cutting-edge components, and IT consulting services.",
  keywords: ["computer hardware", "gaming PC", "laptops", "GPU", "IT consulting"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#030712] text-white min-h-screen`}>
        {children}
      </body>
    </html>
  );
}

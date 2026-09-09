import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Banking AI Prototype Lab | Evidence before action",
  description:
    "A fictional, synthetic banking operations AI lab. Evidence-grounded answers, controlled tools, and visible human review boundaries. No real bank affiliation.",
  robots: { index: false, follow: false },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

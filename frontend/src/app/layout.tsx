import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Clinical Document Compliance & CTD Drafting Agent",
  description:
    "Automated cross-document consistency auditing (Protocol vs Investigator's Brochure vs CTD) and citation-backed CTD drafting.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}

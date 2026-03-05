import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google"; // Modern, geometric, premium
import "./globals.css";

const font = Plus_Jakarta_Sans({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "NexusFlow AI",
  description: "Advanced Content Curation Engine",
};

import { GrandmaProvider, ToastProvider } from "@repo/ui";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={font.className}>
        <ToastProvider>
          <GrandmaProvider>{children}</GrandmaProvider>
        </ToastProvider>
      </body>
    </html>
  );
}

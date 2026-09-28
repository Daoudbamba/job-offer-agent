import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent de candidature",
  description:
    "Agent IA qui analyse une offre d'emploi, la compare à mon profil et rédige une candidature adaptée.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-ink text-paper min-h-screen">{children}</body>
    </html>
  );
}

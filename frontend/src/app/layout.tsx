import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "NirikshaID Bench — Synthetic Document Intelligence Evaluation",
  description: "A reproducible synthetic benchmark for extraction, tamper detection, and VLM robustness.",
};

const links = [
  ["/", "Home"],
  ["/demo", "Interactive Demo"],
  ["/results", "Results"],
  ["/methodology", "Methodology"],
  ["/about", "About"],
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="notice">RESEARCH DEMO — NOT A PRODUCTION KYC SYSTEM</div>
        <header>
          <Link className="brand" href="/"><span className="brandMark">N</span>NirikshaID <b>Bench</b></Link>
          <nav aria-label="Primary navigation">
            {links.map(([href, label]) => <Link key={href} href={href}>{label}</Link>)}
          </nav>
        </header>
        <main>{children}</main>
        <footer>
          <div><strong>NirikshaID Bench</strong><p>Built as a research-engineering demonstration by Ninad Naik.</p></div>
          <div className="footerLinks">
            <a href="https://github.com/ninadnaik03">GitHub</a>
            <a href="https://www.linkedin.com/in/ninad-naik-274883262/">LinkedIn</a>
            <Link href="/methodology">Methodology</Link>
          </div>
          <p className="muted">Every displayed metric is loaded from a locally generated evaluation artifact.</p>
        </footer>
      </body>
    </html>
  );
}

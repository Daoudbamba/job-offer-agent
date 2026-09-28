"use client";

import { useState } from "react";
import { analyzeOffer, AgentResult } from "../lib/api";
import TraceView from "../components/TraceView";

const EXAMPLE_OFFER = `Alternant(e) Data Analyst — Pilotage & Reporting
Entreprise : Chronopost

Nous recherchons un alternant Data Analyst pour rejoindre notre équipe performance.
Compétences recherchées : Python, SQL, PostgreSQL, Power BI, Docker, capacité
d'analyse et de synthèse. Une appétence pour le machine learning est un plus.`;

export default function Home() {
  const [offerText, setOfferText] = useState(EXAMPLE_OFFER);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AgentResult | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeOffer(offerText);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const scorePct = result?.score_adequation != null ? Math.round(result.score_adequation * 100) : null;

  return (
    <main className="max-w-4xl mx-auto px-6 py-16">
      <header className="mb-12">
        <p className="text-accent text-xs uppercase tracking-widest mb-3">Agent IA — Function calling multi-étapes</p>
        <h1 className="text-4xl sm:text-5xl font-semibold text-paper mb-4">Agent de candidature</h1>
        <p className="text-muted max-w-2xl leading-relaxed text-sm">
          Colle une offre d&apos;emploi : l&apos;agent lit mon profil, compare les compétences
          demandées aux miennes, cherche l&apos;entreprise, puis rédige un message de
          candidature — en enchaînant lui-même les outils nécessaires.
        </p>
      </header>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4 mb-12">
        <textarea
          value={offerText}
          onChange={(e) => setOfferText(e.target.value)}
          rows={8}
          className="w-full bg-surface border border-white/10 p-4 text-sm text-paper focus:outline-none focus:border-accent resize-y"
          placeholder="Colle le texte de l'offre ici..."
        />
        <button
          type="submit"
          disabled={loading}
          className="self-start bg-accent text-ink font-semibold px-7 py-3 text-sm transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_12px_40px_-12px_rgba(45,212,167,0.4)] disabled:opacity-50"
        >
          {loading ? "L'agent analyse l'offre..." : "Lancer l'agent →"}
        </button>
      </form>

      {error && (
        <div className="border border-danger/40 text-danger text-sm p-4 mb-8">{error}</div>
      )}

      {result && (
        <div className="flex flex-col gap-8">
          <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="border border-white/10 p-6">
              <p className="text-[11px] uppercase tracking-widest text-dim mb-2">Offre analysée</p>
              <p className="text-paper font-semibold">{result.poste || "—"}</p>
              <p className="text-muted text-sm">{result.entreprise || "—"}</p>
            </div>
            <div className="border border-white/10 p-6">
              <p className="text-[11px] uppercase tracking-widest text-dim mb-2">Adéquation</p>
              <p className={`text-3xl font-semibold ${scorePct !== null && scorePct >= 60 ? "text-accent" : "text-danger"}`}>
                {scorePct !== null ? `${scorePct}%` : "—"}
              </p>
            </div>
            <div className="border border-white/10 p-6">
              <p className="text-[11px] uppercase tracking-widest text-dim mb-2">Compétences manquantes</p>
              <p className="text-paper font-semibold">{result.competences_manquantes.length}</p>
            </div>
          </section>

          <section>
            <p className="text-[11px] uppercase tracking-widest text-dim mb-3">Compétences</p>
            <div className="flex flex-wrap gap-2">
              {result.competences_correspondantes.map((c) => (
                <span key={c} className="border border-accent/40 text-accent text-xs px-3 py-1.5">
                  {c}
                </span>
              ))}
              {result.competences_manquantes.map((c) => (
                <span key={c} className="border border-white/10 text-dim text-xs px-3 py-1.5 line-through">
                  {c}
                </span>
              ))}
            </div>
          </section>

          <section>
            <p className="text-[11px] uppercase tracking-widest text-dim mb-3">Message de candidature généré</p>
            <div className="border border-white/10 p-6 font-serif text-paper leading-relaxed whitespace-pre-wrap">
              {result.message_candidature}
            </div>
          </section>

          <TraceView trace={result.trace} />
        </div>
      )}

      <footer className="mt-24 pt-8 border-t border-white/10 text-xs text-dim">
        Agent function-calling (Gemini) — outils : lecture de profil, matching de compétences,
        recherche entreprise, rédaction. Par Daouda Bamba.
      </footer>
    </main>
  );
}

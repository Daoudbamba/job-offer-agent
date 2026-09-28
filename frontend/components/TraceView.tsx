"use client";

import { useState } from "react";
import type { TraceStep } from "../lib/api";

const TOOL_LABELS: Record<string, string> = {
  get_candidate_profile: "Lecture du profil candidat",
  match_skills: "Comparaison des compétences",
  search_company_info: "Recherche sur l'entreprise",
  finalize: "Rédaction du message final",
  reponse_directe: "Réponse directe (sans outil)",
};

function StepDetail({ step }: { step: TraceStep }) {
  if (step.contenu) return <p className="text-muted text-sm">{step.contenu}</p>;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
      {step.arguments && Object.keys(step.arguments).length > 0 && (
        <div>
          <p className="text-dim uppercase tracking-widest mb-1">Arguments</p>
          <pre className="text-muted whitespace-pre-wrap break-words">
            {JSON.stringify(step.arguments, null, 2)}
          </pre>
        </div>
      )}
      {step.resultat !== undefined && (
        <div>
          <p className="text-dim uppercase tracking-widest mb-1">Résultat</p>
          <pre className="text-muted whitespace-pre-wrap break-words">
            {JSON.stringify(step.resultat, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default function TraceView({ trace }: { trace: TraceStep[] }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-white/10">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-6 py-4 text-left"
      >
        <span className="font-mono text-xs uppercase tracking-widest text-accent">
          Raisonnement de l&apos;agent ({trace.length} étape{trace.length > 1 ? "s" : ""})
        </span>
        <span className="text-dim text-xs">{open ? "▲ masquer" : "▼ afficher"}</span>
      </button>

      {open && (
        <div className="px-6 pb-6 flex flex-col gap-4">
          {trace.map((step, i) => (
            <div key={i} className="border-l-2 border-accent/40 pl-4 py-1">
              <p className="font-mono text-xs text-paper mb-2">
                {i + 1}. {TOOL_LABELS[step.etape] || step.etape}
              </p>
              <StepDetail step={step} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

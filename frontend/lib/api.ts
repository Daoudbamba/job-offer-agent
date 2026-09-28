const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8030";

export type TraceStep = {
  etape: string;
  arguments?: Record<string, unknown>;
  resultat?: unknown;
  contenu?: string;
};

export type AgentResult = {
  trace: TraceStep[];
  poste: string | null;
  entreprise: string | null;
  message_candidature: string | null;
  score_adequation: number | null;
  competences_correspondantes: string[];
  competences_manquantes: string[];
};

export async function analyzeOffer(offerText: string): Promise<AgentResult> {
  const res = await fetch(`${API_URL}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ offer_text: offerText }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.detail?.message || body?.detail || `Erreur API (${res.status})`);
  }
  return res.json();
}

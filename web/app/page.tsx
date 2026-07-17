"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";



// descreve o formato de cada empresa que vem da API (você já conhece "type" do TS)
type Empresa = {
  nome: string;
  setor: string | null;
  classificacao: string | null;
  score: number | null;
  notas: Record<string, number> | null;
};

type Detalhe = {
  briefing: string | null;
  recomendacao: { tecnologias?: string[]; evidencias?: string[] } | null;
};


const EIXOS = [
  { key: "ai_native", label: "AI-Native" },
  { key: "nvidia_fit", label: "NVIDIA-Fit" },
  { key: "tracao", label: "Tração" },
  { key: "time_ia", label: "Time de IA" },
];

function compor(
  notas: Record<string, number> | null,
  pesos: Record<string, number>
): number | null {
  if (!notas) return null; // empresa sem dados -> sem score
  const chaves = ["ai_native", "nvidia_fit", "tracao", "time_ia"];
  let totalPeso = 0;
  let soma = 0;
  for (const k of chaves) {
    totalPeso += pesos[k] ?? 0;
    soma += (pesos[k] ?? 0) * (notas[k] ?? 0);
  }
  if (totalPeso == 0) return 0;
  return Math.round((soma / totalPeso) * 100) / 100; // arredonda a 2 casas
}

function Badge({ classificacao }: { classificacao: string | null }) {
  const cores: Record<string, string> = {
    "ai-native": "text-nvidia border-nvidia",
    "ai-enabled": "text-amber-400 border-amber-400",
  };
  const cor = cores[classificacao ?? ""] ?? "text-zinc-500 border-zinc-600";
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full border text-xs ${cor}`}>
      {classificacao ?? "—"}
    </span>
  );
}


export default function Home() {
  const [empresas, setEmpresas] = useState<Empresa[]>([]);

  const [pesos, setPesos] = useState<Record<string, number>>({
    ai_native: 0.3, nvidia_fit: 0.3, tracao: 0.2, time_ia: 0.2,
  });

  const [selecionada, setSelecionada] = useState<string | null>(null);

  const [detalhe, setDetalhe] = useState<Detalhe | null>(null);

  const [nova, setNova] = useState(""); // o texto digitado

  const [analisando, setAnalisando] = useState(false); // está rodando?



  const carregarEmpresas = () => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/empresas`)
      .then((res) => res.json())
      .then((data) => setEmpresas(data));
  };

  useEffect(() => {
    carregarEmpresas();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  useEffect(() => {
    if (!selecionada) {
      setDetalhe(null);
      return;
    }
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/empresas/${selecionada}`)
      .then((res) => res.json())
      .then((data) => setDetalhe(data));
  }, [selecionada]);


  const ranked = [...empresas].sort((a, b) => (compor(b.notas, pesos) ?? -1) - (compor(a.notas, pesos) ?? -1));

  const empresaSelecionada = empresas.find((x) => x.nome === selecionada);

  const analisar = () => {
    if (!nova.trim()) return;
    setAnalisando(true);
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/analisar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ consulta: nova }),
    })
      .then((res) => res.json())
      .then(() => {
        setNova("");
        carregarEmpresas(); // recarrega a lista já com a nova empresa
      })
      .finally(() => setAnalisando(false));
  };



  return (
    <main className="p-8">
      <header className="flex items-center gap-3 mb-8">
        <div className="w-1.5 h-12 bg-nvidia rounded" />
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            <span className="text-nvidia">NVIDIA</span> Startup AI Radar
          </h1>
          <p className="text-sm text-zinc-500">
            Inteligência de mercado — startups de IA × portfólio NVIDIA
          </p>
        </div>
      </header>
      <div className="mb-6 flex gap-2">
        <input
          type="text"
          placeholder="Empresa ou consulta…"
          value={nova}
          onChange={(e) => setNova(e.target.value)}
          className="border border-zinc-700 rounded px-3 py-1 bg-transparent"
        />
        <button
          onClick={analisar}
          disabled={analisando}
          className="px-4 py-1 rounded bg-zinc-700 disabled:opacity-50"
        >
          {analisando ? "Analisando…" : "Analisar"}
        </button>
      </div>

      <div className="mb-6">
        <h2 className="font-semibold mb-2">Pesos do score</h2>
        {EIXOS.map((eixo) => (
          <div key={eixo.key} className="flex items-center gap-3 mb-1">
            <label className="w-28">{eixo.label}</label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={pesos[eixo.key]}
              onChange={(e) => setPesos({ ...pesos, [eixo.key]: Number(e.target.value) })}
            />
            <span className="w-10 text-right">{pesos[eixo.key]}</span>
          </div>
        ))}
      </div>
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-zinc-700 text-zinc-400">
            <th className="py-2">Empresa</th>
            <th>Setor</th>
            <th>Classificação</th>
            <th className="text-right">Score</th>
          </tr>
        </thead>
        <tbody>
          {ranked.map((empresa) => (
            <tr
              key={empresa.nome}
              onClick={() => setSelecionada(empresa.nome)}
              className="border-b border-zinc-800 cursor-pointer hover:bg-zinc-900"
            >
              <td className="py-2">{empresa.nome}</td>
              <td className="text-zinc-400">{empresa.setor ?? "—"}</td>
              <td><Badge classificacao={empresa.classificacao} /></td>
              <td className="text-right font-semibold text-nvidia">{compor(empresa.notas, pesos) ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {empresaSelecionada && (
        <div className="mt-8 p-4 border border-zinc-700 rounded-lg">
          <h2 className="text-xl font-bold mb-1">{empresaSelecionada.nome}</h2>
          <p className="text-zinc-400 mb-3">
            {empresaSelecionada.setor ?? "—"} · <Badge classificacao={empresaSelecionada.classificacao} />
          </p>
          {empresaSelecionada.notas && (
            <ul className="text-sm space-y-1">
              <li>AI-Native: {empresaSelecionada.notas.ai_native}</li>
              <li>NVIDIA-Fit: {empresaSelecionada.notas.nvidia_fit}</li>
              <li>Tração: {empresaSelecionada.notas.tracao}</li>
              <li>Time de IA: {empresaSelecionada.notas.time_ia}</li>
            </ul>
          )}
          {detalhe?.briefing && (
            <div className="mt-4 pt-4 border-t border-zinc-700">
              <h3 className="font-semibold mb-2">Briefing executivo</h3>
              <div className="prose prose-invert prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{detalhe.briefing}</ReactMarkdown>
              </div>

            </div>
          )}

        </div>
      )}

    </main>
  );
}


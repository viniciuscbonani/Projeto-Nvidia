"use client";

// Aba Descoberta: fecha o ciclo "encontrar -> analisar -> rankear" na UI.
// DESCOBRIR só acha NOMES (busca web + LLM, via POST /descobrir); é o
// ANALISAR de cada item que roda o pipeline completo (POST /analisar,
// o mesmo do Ranking) e coloca a empresa no banco.

import { useState } from "react";
import Link from "next/link";
import {
  ArrowSquareOutIcon,
  CompassIcon,
  TerminalWindowIcon,
} from "@phosphor-icons/react";
import TabsRadar from "../TabsRadar";

type StatusItem = "novo" | "analisando" | "analisada";
type ItemDescoberto = { nome: string; status: StatusItem };

const API = process.env.NEXT_PUBLIC_API_URL;

export default function DescobertaPage() {
  const [tema, setTema] = useState("");
  const [descobrindo, setDescobrindo] = useState(false);
  const [buscou, setBuscou] = useState(false); // já rodou ao menos 1 descoberta?
  const [erroApi, setErroApi] = useState(false);
  const [itens, setItens] = useState<ItemDescoberto[]>([]);

  const descobrir = async () => {
    if (!tema.trim() || descobrindo) return;
    setDescobrindo(true);
    setErroApi(false);
    try {
      // dispara a descoberta e, em paralelo, busca quem JÁ está no banco
      // para marcar "já no radar" (Promise.all espera as duas)
      const [resDescobrir, resEmpresas] = await Promise.all([
        fetch(`${API}/descobrir`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tema }),
        }),
        fetch(`${API}/empresas`),
      ]);
      if (!resDescobrir.ok || !resEmpresas.ok) throw new Error();
      const { nomes } = (await resDescobrir.json()) as { nomes: string[] };
      const existentes = new Set(
        ((await resEmpresas.json()) as { nome: string }[]).map((e) =>
          e.nome.trim().toLowerCase()
        )
      );
      setItens(
        nomes.map((nome) => ({
          nome,
          status: existentes.has(nome.trim().toLowerCase())
            ? "analisada"
            : "novo",
        }))
      );
      setBuscou(true);
    } catch {
      setErroApi(true);
    } finally {
      setDescobrindo(false);
    }
  };

  const trocarStatus = (nome: string, status: StatusItem) =>
    setItens((atual) =>
      atual.map((i) => (i.nome === nome ? { ...i, status } : i))
    );

  const analisarItem = async (nome: string) => {
    trocarStatus(nome, "analisando");
    try {
      const res = await fetch(`${API}/analisar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ consulta: nome }),
      });
      if (!res.ok) throw new Error();
      trocarStatus(nome, "analisada");
    } catch {
      trocarStatus(nome, "novo"); // volta ao estado inicial para tentar de novo
      setErroApi(true);
    }
  };

  const analisandoAlgum = itens.some((i) => i.status === "analisando");

  return (
    <main className="mx-auto w-full max-w-[1400px] px-6 py-8">
      <TabsRadar />

      {/* ── Tema + Descobrir ──────────────────────────────────────── */}
      <div className="mt-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Descoberta</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Do tema aos nomes: a busca encontra startups; o Analisar roda o
            pipeline completo.
          </p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            descobrir();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Tema, ex.: IA em saúde"
            aria-label="Tema da descoberta"
            value={tema}
            onChange={(e) => setTema(e.target.value)}
            className="w-64 rounded-lg border border-line bg-[#0C0C0C] px-3 py-2 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted/70 focus:border-nvidia/60 sm:w-80"
          />
          <button
            type="submit"
            disabled={descobrindo}
            className="rounded-lg bg-nvidia px-4 py-2 text-sm font-semibold text-black transition-colors hover:bg-nvidia-bright active:translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
          >
            {descobrindo ? "Descobrindo..." : "Descobrir"}
          </button>
        </form>
      </div>
      {descobrindo && (
        <p className="mt-2 text-right text-xs text-ink-muted">
          Buscando e lendo listas na web; isso pode levar um tempo.
        </p>
      )}

      {/* ── Resultado ─────────────────────────────────────────────── */}
      <div className="mt-8">
        {erroApi ? (
          <div className="rounded-xl border border-line bg-[#0C0C0C] px-6 py-10 text-center">
            <TerminalWindowIcon
              size={28}
              className="mx-auto text-ink-muted"
              aria-hidden
            />
            <p className="mt-3 text-sm text-ink-muted">
              A API está fora do ar. Suba o backend:
            </p>
            <code className="mt-3 inline-block rounded-lg bg-surface-2 px-3 py-1.5 font-mono text-xs text-ink">
              uvicorn app.api:app --reload
            </code>
          </div>
        ) : descobrindo ? (
          // skeleton com a forma dos cards que vão chegar
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="animate-pulse rounded-xl border border-line bg-[#0C0C0C] p-5 motion-reduce:animate-none"
              >
                <div className="h-4 w-32 rounded bg-surface-2" />
                <div className="mt-4 h-8 w-24 rounded-lg bg-surface-2" />
              </div>
            ))}
          </div>
        ) : !buscou ? (
          // estado inicial: explica o que a aba faz
          <div className="rounded-xl border border-line bg-[#0C0C0C] px-6 py-12 text-center">
            <CompassIcon size={32} className="mx-auto text-nvidia" aria-hidden />
            <h2 className="mt-4 font-semibold">Descubra startups por tema</h2>
            <p className="mx-auto mt-2 max-w-md text-sm text-ink-muted">
              Digite um tema (ex.: "startups brasileiras de IA em saúde") e o
              pipeline busca listas e notícias na web e extrai os nomes. Depois,
              analise as que interessarem para entrarem no ranking.
            </p>
          </div>
        ) : itens.length === 0 ? (
          <div className="rounded-xl border border-line bg-[#0C0C0C] px-6 py-10 text-center">
            <p className="text-sm text-ink-muted">
              Nenhum nome encontrado para esse tema. Tente um tema mais amplo,
              como "IA em agro" ou "fintechs de IA".
            </p>
          </div>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {itens.map((item) => (
                <div
                  key={item.nome}
                  className="flex flex-col justify-between gap-4 rounded-xl border border-line bg-[#0C0C0C] p-5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="font-medium">{item.nome}</h3>
                    {item.status === "analisada" && (
                      <span className="shrink-0 rounded-full border border-nvidia/50 px-2.5 py-0.5 text-xs text-nvidia">
                        já no radar
                      </span>
                    )}
                  </div>

                  {item.status === "analisada" ? (
                    <Link
                      href={`/radar/${encodeURIComponent(item.nome)}`}
                      className="inline-flex w-fit items-center gap-1.5 rounded-lg border border-nvidia/70 px-3 py-2 text-sm font-medium text-ink transition-colors hover:border-nvidia hover:bg-nvidia/10 active:translate-y-px"
                    >
                      <ArrowSquareOutIcon
                        size={15}
                        className="text-nvidia"
                        aria-hidden
                      />
                      Ver no radar
                    </Link>
                  ) : (
                    <button
                      onClick={() => analisarItem(item.nome)}
                      disabled={item.status === "analisando"}
                      className="w-fit rounded-lg border border-nvidia/70 px-3 py-2 text-sm font-medium text-ink transition-colors hover:border-nvidia hover:bg-nvidia/10 active:translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {item.status === "analisando"
                        ? "Analisando..."
                        : "Analisar"}
                    </button>
                  )}
                </div>
              ))}
            </div>
            {analisandoAlgum && (
              <p className="mt-4 text-xs text-ink-muted">
                O pipeline completo roda para cada análise; pode levar alguns
                minutos por empresa.
              </p>
            )}
          </>
        )}
      </div>
    </main>
  );
}

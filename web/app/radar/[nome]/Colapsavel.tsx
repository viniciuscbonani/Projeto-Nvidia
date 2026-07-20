"use client";

// Colapsável com animação. O <details> nativo não anima e o hover só pinta a
// faixa com o mouse em cima; por isso controlamos o "aberto" em estado.
//
// Animação: um grid que transiciona de grid-rows-[0fr] para [1fr]. Isso expande
// a altura de forma suave SEM precisar medir o texto, e é só CSS. Com "reduzir
// movimento" ativo, motion-reduce:transition-none corta a transição.

import { useState } from "react";
import { CaretDownIcon } from "@phosphor-icons/react";

export default function Colapsavel({
  titulo,
  texto,
}: {
  titulo: string;
  texto: string;
}) {
  const [aberto, setAberto] = useState(false);

  return (
    <div className="overflow-hidden rounded-lg border border-line">
      <button
        type="button"
        onClick={() => setAberto((v) => !v)}
        aria-expanded={aberto}
        className={`flex w-full cursor-pointer items-center justify-between px-4 py-3 text-left text-sm font-medium transition-colors ${
          aberto ? "bg-surface-2" : "hover:bg-surface-2"
        }`}
      >
        {titulo}
        <CaretDownIcon
          size={14}
          className={`shrink-0 text-nvidia transition-transform duration-300 motion-reduce:transition-none ${
            aberto ? "rotate-180" : ""
          }`}
          aria-hidden
        />
      </button>

      <div
        className={`grid transition-[grid-template-rows] duration-300 ease-out motion-reduce:transition-none ${
          aberto ? "grid-rows-[1fr]" : "grid-rows-[0fr]"
        }`}
      >
        {/* o overflow-hidden esconde o texto enquanto a linha do grid tem 0fr */}
        <div className="overflow-hidden">
          <p className="max-w-[75ch] border-t border-line px-4 py-3 text-sm leading-relaxed">
            {texto}
          </p>
        </div>
      </div>
    </div>
  );
}

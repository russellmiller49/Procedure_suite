import {useEffect, useRef} from "react";
import type {DocumentMeta, SourceDocument, Span} from "./types";
import {segments} from "./review";

type Props = {
  documents: DocumentMeta[];
  document: SourceDocument | null;
  onSelect: (id: string) => void;
  spans: [number, number][];
  focus: Span | null;
};

export function SourceView({documents, document, onSelect, spans, focus}: Props) {
  const marked = useRef<HTMLElement | null>(null);
  const focusRange = focus && document && focus.document_id === document.id ? ([focus.start, focus.end] as [number, number]) : null;
  useEffect(() => {
    marked.current?.scrollIntoView({block: "center", behavior: "smooth"});
  }, [focus, document?.id]);
  return (
    <section className="source">
      <div className="tabs" role="tablist" aria-label="Source documents">
        {documents.map((d, i) => (
          <button
            key={d.id}
            role="tab"
            aria-selected={document?.id === d.id}
            className={document?.id === d.id ? "tab active" : "tab"}
            onClick={() => onSelect(d.id)}
          >
            {d.kind} {i + 1}
            <small>{d.variant || "text"} · {d.characters.toLocaleString()} chars</small>
          </button>
        ))}
      </div>
      {document?.exposure && document.exposure !== "development" && (
        <p className="notice" role="note">This document belongs to an exposed evaluation split; viewing it is recorded.</p>
      )}
      {document ? (
        <pre className="source-text" aria-label="Source text">
          {segments(document.text, spans, focusRange).map(seg =>
            seg.mark === "none" ? (
              <span key={seg.start}>{seg.text}</span>
            ) : (
              <mark
                key={seg.start}
                className={seg.mark}
                ref={seg.mark === "focus" ? el => { if (el) marked.current = el; } : undefined}
              >
                {seg.text}
              </mark>
            ),
          )}
        </pre>
      ) : (
        <p className="subtle">Select a document.</p>
      )}
    </section>
  );
}

'use client';

import React, { useState } from 'react';
import { api } from '@/lib/api';
import { BookOpen, Send, X, Sparkles, BookMarked, HelpCircle, FileText } from 'lucide-react';

interface AskRuleBookDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AskRuleBookDrawer({ isOpen, onClose }: AskRuleBookDrawerProps) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<{
    answer: string;
    citations: Array<{ source: string; page: number; text_snippet: string }>;
  } | null>(null);

  const sampleQuestions = [
    "What are mandatory declarations on retail packages under Rule 6?",
    "What is the exemption limit for small packages?",
    "How should Maximum Retail Price (MRP) be declared?",
    "What are the rules for Unit Sale Price (USP)?"
  ];

  const handleAsk = async (qText?: string) => {
    const questionToSend = qText || query;
    if (!questionToSend.trim()) return;

    setLoading(true);
    try {
      const data = await api.askRuleBook(questionToSend);
      setResponse({
        answer: data.answer,
        citations: data.citations || []
      });
    } catch (e) {
      console.error(e);
      setResponse({
        answer: "Failed to retrieve rulebook citation. Please ensure backend is running.",
        citations: []
      });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white border-l border-[#e6e6e6] shadow-2xl flex flex-col">
      {/* Header */}
      <div className="px-5 py-4 border-b border-[#e6e6e6] bg-[#f6f5f4] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-[#0075de]" />
          <div>
            <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider">
              Legal Metrology RAG Assistant
            </h3>
            <p className="text-[11px] text-[#615d59]">Packaged Commodities Rules, 2011 & Official FAQs</p>
          </div>
        </div>
        <button onClick={onClose} className="p-1 rounded-md text-[#615d59] hover:bg-[#e6e6e6]">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {/* Suggested Queries */}
        <div>
          <p className="text-[11px] font-semibold text-[#615d59] mb-2 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-[#0075de]" />
            <span>Frequently Asked Statutory Questions:</span>
          </p>
          <div className="space-y-1.5">
            {sampleQuestions.map((sq, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQuery(sq);
                  handleAsk(sq);
                }}
                className="w-full text-left p-2 rounded-lg bg-[#f6f5f4] hover:bg-blue-50 hover:text-[#0075de] text-[11px] text-[#31302e] border border-[#e6e6e6] transition-colors"
              >
                {sq}
              </button>
            ))}
          </div>
        </div>

        {/* Answer Output */}
        {loading && (
          <div className="p-6 text-center text-[#615d59]">
            <div className="w-6 h-6 border-2 border-[#0075de] border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            <p className="text-xs">Searching Legal Metrology Gazette & Rulebooks...</p>
          </div>
        )}

        {response && !loading && (
          <div className="space-y-3">
            <div className="p-3.5 rounded-xl bg-blue-50/70 border border-blue-200">
              <p className="text-[11px] font-bold text-[#213183] uppercase tracking-wider mb-1 flex items-center gap-1">
                <BookMarked className="w-3.5 h-3.5" />
                Statutory Ruling & Interpretation:
              </p>
              <div className="text-xs text-[#1e293b] whitespace-pre-wrap leading-relaxed">
                {response.answer}
              </div>
            </div>

            {/* Citations */}
            {response.citations.length > 0 && (
              <div>
                <p className="text-[11px] font-bold text-[#615d59] uppercase mb-1.5">
                  Official Gazette Citations:
                </p>
                <div className="space-y-1.5">
                  {response.citations.map((c, i) => (
                    <div key={i} className="p-2 bg-[#f6f5f4] rounded-lg border border-[#e6e6e6] text-[11px]">
                      <span className="font-bold text-[#0075de]">{c.source} (Page {c.page})</span>
                      <p className="text-[#31302e] text-[10px] mt-0.5 italic">{c.text_snippet}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleAsk();
        }}
        className="p-3 border-t border-[#e6e6e6] bg-[#f6f5f4] flex items-center gap-2"
      >
        <input
          type="text"
          placeholder="Ask any legal metrology rule, schedule, exemption..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 px-3 py-2 border border-[#e6e6e6] rounded-md text-xs focus:outline-none focus:border-[#0075de] bg-white"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="p-2 rounded-md bg-[#0075de] text-white hover:bg-[#005bab] disabled:opacity-40 shadow-xs"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}

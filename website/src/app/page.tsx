"use client";

import { motion } from "framer-motion";
import { Terminal, ShieldCheck, Search, Scale, BrainCircuit, GitBranch, ChevronRight, Copy, Check } from "lucide-react";
import { useState } from "react";

export default function Home() {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText("pip install intent-completeness-checker");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const features = [
    {
      title: "Investigator",
      description: "Analyzes the original intent or git diff and breaks it down into a strict list of testable assertions.",
      icon: <ShieldCheck className="w-6 h-6 text-purple-400" />,
    },
    {
      title: "Searcher",
      description: "Autonomously navigates the codebase using ripgrep to hunt for missed code, docs, or config files.",
      icon: <Search className="w-6 h-6 text-blue-400" />,
    },
    {
      title: "Judge",
      description: "Examines the Searcher's findings to filter out false positives and determine if a true violation occurred.",
      icon: <Scale className="w-6 h-6 text-emerald-400" />,
    },
    {
      title: "Orchestrator",
      description: "Manages concurrency, coordinates the agents, and generates a structured, actionable final report.",
      icon: <BrainCircuit className="w-6 h-6 text-pink-400" />,
    },
  ];

  return (
    <div className="min-h-screen bg-black text-white selection:bg-purple-500/30 overflow-hidden relative">
      {/* Background Grid */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:32px_32px]" />
      
      {/* Glowing Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-purple-600/20 blur-[120px] mix-blend-screen pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/20 blur-[120px] mix-blend-screen pointer-events-none" />

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <Terminal className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight">IntentCheck</span>
        </div>
        <div className="flex items-center gap-6">
          <a href="#how-it-works" className="text-sm text-gray-400 hover:text-white transition-colors">How it works</a>
          <a href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">Features</a>
          <a href="/documentation" className="text-sm text-gray-400 hover:text-white transition-colors">Documentation</a>
          <a 
            href="https://github.com/userdeter1/Intent-Completeness-Checker" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm font-medium bg-white/10 hover:bg-white/20 border border-white/10 px-4 py-2 rounded-full transition-all"
          >
            <GitBranch className="w-4 h-4" />
            GitHub
          </a>
        </div>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-24 pb-32">
        {/* Hero Section */}
        <section className="text-center max-w-4xl mx-auto mb-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-block py-1 px-3 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-sm font-medium mb-6">
              Powered by Agno Framework
            </span>
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-500">
              Ensure your AI coding assistants finish what they started.
            </h1>
            <p className="text-lg md:text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
              AI agents are great at writing code, but they suffer from tunnel vision. They forget docs, tests, and configs. IntentCheck is an independent, multi-agent reviewer that hunts for missed updates.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button 
                onClick={copyToClipboard}
                className="group flex items-center justify-between w-full sm:w-auto min-w-[300px] bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-4 rounded-xl font-mono text-sm text-gray-300 transition-all backdrop-blur-sm"
              >
                <span>$ pip install intent-completeness-checker</span>
                {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-gray-500 group-hover:text-gray-300 transition-colors" />}
              </button>
              <a 
                href="/documentation" 
                className="flex items-center justify-center gap-2 w-full sm:w-auto bg-white text-black px-8 py-4 rounded-xl font-medium hover:bg-gray-200 transition-colors"
              >
                View Documentation <ChevronRight className="w-4 h-4" />
              </a>
            </div>
          </motion.div>
        </section>

        {/* Terminal Demo Section */}
        <section id="how-it-works" className="mb-32">
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="rounded-2xl border border-white/10 bg-black/50 backdrop-blur-xl overflow-hidden shadow-2xl shadow-purple-900/20"
          >
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/10 bg-white/5">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <div className="mx-auto text-xs font-mono text-gray-500 flex-1 text-center pr-10">
                intentcheck investigate --full-pipeline
              </div>
            </div>
            <div className="p-6 overflow-x-auto font-mono text-sm leading-relaxed text-gray-300">
              <div className="text-gray-500 mb-2">$ intentcheck investigate --intent "Rename OLD_API_KEY to NEW_API_KEY everywhere"</div>
              <div className="text-purple-400 mb-4">╭─────────────────────  Intent Completeness Report ──────────────────────╮</div>
              <div className="mb-4">
                <span className="text-emerald-400">✅ Assertions satisfied</span><br/>
                <span className="text-gray-400">│ A1 │ OLD_API_KEY should no longer be used. │ Found 0 occurrences. ✅ │</span>
              </div>
              <div className="mb-4">
                <span className="text-red-400">❌ Assertions violated</span><br/>
                <span className="text-gray-400">│ A2 │ NEW_API_KEY must replace the old one in auth.py │</span><br/>
                <span className="text-red-300 ml-4">↳ auth.py:42: return OLD_API_KEY # forgot to update!</span>
              </div>
              <div className="text-purple-400 mt-6">╰──────────────────────────────────────────────────────────────────────────╯</div>
              <div className="mt-2 text-red-400 font-bold">❌ 1 blocking issue(s) detected. Exit code 1.</div>
            </div>
          </motion.div>
        </section>

        {/* Features Section */}
        <section id="features" className="mb-32">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">A Multi-Agent AI Pipeline</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">Four specialized AI agents work in parallel to guarantee your code changes are exhaustive and complete.</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="group p-8 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all duration-300 cursor-default"
              >
                <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-gray-400 leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Pre-commit Banner */}
        <section className="mb-16">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="rounded-3xl bg-gradient-to-br from-purple-900/40 to-blue-900/40 border border-white/10 p-10 md:p-16 text-center relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:32px_32px]" />
            <div className="relative z-10">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">Blocks incomplete commits instantly.</h2>
              <p className="text-lg text-gray-300 mb-8 max-w-2xl mx-auto">
                Integrates natively as a git pre-commit hook. If the AI detects a half-finished refactor, the commit is blocked before it ever reaches your repository.
              </p>
              <div className="inline-block bg-black/50 border border-white/10 rounded-xl px-6 py-4 font-mono text-sm text-left backdrop-blur-md overflow-x-auto w-full max-w-2xl">
                <div className="text-gray-400">repos:</div>
                <div className="text-gray-400">- repo: <span className="text-purple-300">https://github.com/userdeter1/Intent-Completeness-Checker</span></div>
                <div className="text-gray-400 ml-2">rev: <span className="text-blue-300">main</span></div>
                <div className="text-gray-400 ml-2">hooks:</div>
                <div className="text-gray-400 ml-2">- id: <span className="text-green-300">intentcheck</span></div>
              </div>
            </div>
          </motion.div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 text-center text-gray-500 text-sm">
        <p className="mb-4">An open source solution for code verification.</p>
        <div className="flex items-center justify-center gap-6">
          <a href="https://github.com/userdeter1/Intent-Completeness-Checker" className="hover:text-white transition-colors">GitHub</a>
          <a href="https://github.com/userdeter1/Intent-Completeness-Checker/blob/main/LICENSE" className="hover:text-white transition-colors">MIT License</a>
        </div>
      </footer>
    </div>
  );
}

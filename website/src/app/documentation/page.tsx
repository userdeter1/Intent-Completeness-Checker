import { Terminal, GitBranch, ChevronRight, Copy, BookOpen, Key, Rocket } from "lucide-react";

export default function Documentation() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-purple-500/30 overflow-hidden relative">
      {/* Background */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:32px_32px] pointer-events-none" />
      <div className="absolute top-0 left-0 w-full h-96 bg-gradient-to-b from-purple-900/20 to-black pointer-events-none" />

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 max-w-7xl mx-auto border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <Terminal className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight">IntentCheck</span>
        </div>
        <div className="flex items-center gap-6">
          <a href="/" className="text-sm text-gray-400 hover:text-white transition-colors">Home</a>
          <a href="#" className="text-sm text-white font-medium border-b-2 border-purple-500 pb-1">Documentation</a>
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

      {/* Content */}
      <main className="relative z-10 max-w-4xl mx-auto px-6 pt-16 pb-32">
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">Documentation</h1>
            <span className="inline-block py-1 px-3 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-bold tracking-wider uppercase">
              Powered by Agno
            </span>
          </div>
          <p className="text-lg text-gray-400">Everything you need to integrate IntentCheck into your workflow.</p>
        </div>

        <div className="space-y-16">
          {/* Quick Start Section */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
                <Rocket className="w-5 h-5 text-purple-400" />
              </div>
              <h2 className="text-2xl font-bold">Quick Start</h2>
            </div>
            
            <p className="text-gray-300 leading-relaxed mb-6">
              IntentCheck is a fully autonomous AI pipeline that analyzes your codebase to ensure you haven't forgotten any edge cases, documentation, or configurations when making changes. Here is how to get it running in under 2 minutes.
            </p>

            <div className="space-y-8">
              {/* Step 1 */}
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-sm">1</span>
                  Installation
                </h3>
                <p className="text-gray-400 mb-4 text-sm">Install the CLI tool globally or in your current virtual environment using pip.</p>
                <div className="bg-black/50 border border-white/10 rounded-xl p-4 font-mono text-sm text-purple-300">
                  pip install intent-completeness-checker
                </div>
              </div>

              {/* Step 2 */}
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-sm">2</span>
                  Configuration
                </h3>
                <p className="text-gray-400 mb-4 text-sm">IntentCheck requires API keys to orchestrate its AI agents. You can use Groq (Fast & Free) or OpenAI.</p>
                <div className="bg-black/50 border border-white/10 rounded-xl p-4 font-mono text-sm text-gray-300 mb-4">
                  <div className="text-gray-500 mb-1"># Export your API key in your terminal</div>
                  <div>export GROQ_API_KEY="gsk_your_api_key_here"</div>
                  <div className="text-gray-500 mt-2 mb-1"># Or if you prefer OpenAI:</div>
                  <div>export OPENAI_API_KEY="sk-your_api_key_here"</div>
                </div>
                <div className="flex items-start gap-3 p-4 rounded-xl bg-purple-900/20 border border-purple-500/20">
                  <Key className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
                  <p className="text-sm text-purple-200">
                    <strong>Tip:</strong> We highly recommend using Groq with the <code className="text-white bg-black/30 px-1 rounded">llama-3.3-70b-versatile</code> model for near-instantaneous multi-agent processing.
                  </p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-sm">3</span>
                  Run your first scan
                </h3>
                <p className="text-gray-400 mb-4 text-sm">Navigate to your project folder and run the investigator. Tell it exactly what you were trying to achieve.</p>
                <div className="bg-black/50 border border-white/10 rounded-xl p-4 font-mono text-sm text-gray-300">
                  <div className="text-gray-500 mb-1"># Let the AI verify if you forgot to update anything</div>
                  <div className="text-emerald-300">intentcheck investigate --intent "Rename OLD_API_KEY to NEW_API_KEY everywhere"</div>
                </div>
              </div>
            </div>
          </section>

          {/* Advanced Usage Section */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold">Pre-commit Integration</h2>
            </div>
            
            <p className="text-gray-300 leading-relaxed mb-6">
              You can integrate IntentCheck directly into your git workflow. It will automatically read your staged files, infer your intent, and block the commit if your refactoring is incomplete.
            </p>

            <div className="bg-black/50 border border-white/10 rounded-xl p-6 font-mono text-sm text-gray-300">
              <div className="text-gray-500 mb-2"># Add this to your .pre-commit-config.yaml</div>
              <div className="text-purple-300">repos:</div>
              <div className="text-purple-300">  - repo: <span className="text-blue-300">https://github.com/userdeter1/Intent-Completeness-Checker</span></div>
              <div className="text-blue-300">    rev: main</div>
              <div className="text-purple-300">    hooks:</div>
              <div className="text-purple-300">      - id: <span className="text-green-300">intentcheck</span></div>
            </div>
          </section>

        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 text-center text-gray-500 text-sm relative z-10">
        <p className="mb-4">An open source solution for code verification.</p>
      </footer>
    </div>
  );
}

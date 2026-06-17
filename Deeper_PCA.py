import tkinter as tk
from tkinter import messagebox
import numpy as np
import yfinance as yf

BG = "#0f0f1a"
PANEL = "#1a1a2e"
ACCENT = "#4a9eff"
TEXT = "#e8e8f0"
MUTED = "#666688"
SUCCESS = "#4ade80"
ERROR = "#f87171"
AMBER = "#fbbf24"
ENTRY_BG = "#252540"
BORDER = "#2a2a4a"

class PortfolioRiskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Portfolio Risk Manager")
        self.root.geometry("1100x720")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=30, pady=(20, 0))
        tk.Label(header, text="Portfolio Risk Manager",
                 font=("Courier", 22, "bold"), bg=BG, fg="#4a9eff").pack(anchor="w")
        tk.Label(header, text="linear algebra · probability · risk metrics · by Santi",
                 font=("Courier", 10), bg=BG, fg=MUTED).pack(anchor="w", pady=(2, 0))
        tk.Frame(self.root, bg="#4a9eff", height=1).pack(fill="x", padx=30, pady=10)

        # Input row
        input_frame = tk.Frame(self.root, bg=BG)
        input_frame.pack(fill="x", padx=30, pady=(0, 10))

        tk.Label(input_frame, text="Tickers:", font=("Courier", 11), bg=BG, fg=TEXT).pack(side="left")
        self.tickers_entry = tk.Entry(input_frame, width=35, font=("Courier", 11),
                                      bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT, bd=0, relief="flat")
        self.tickers_entry.insert(0, "MU, NBIS, TSEM, AMD, INTC, GOOG")
        self.tickers_entry.pack(side="left", padx=(8, 20), ipady=6)

        tk.Label(input_frame, text="Start:", font=("Courier", 11), bg=BG, fg=TEXT).pack(side="left")
        self.start_entry = tk.Entry(input_frame, width=12, font=("Courier", 11),
                                    bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT, bd=0, relief="flat")
        self.start_entry.insert(0, "2022-01-01")
        self.start_entry.pack(side="left", padx=(8, 20), ipady=6)

        tk.Label(input_frame, text="Rf (annual %):", font=("Courier", 11), bg=BG, fg=TEXT).pack(side="left")
        self.rf_entry = tk.Entry(input_frame, width=6, font=("Courier", 11),
                                 bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT, bd=0, relief="flat")
        self.rf_entry.insert(0, "3.5")
        self.rf_entry.pack(side="left", padx=(8, 20), ipady=6)

        tk.Button(input_frame, text="Analyse →", font=("Courier", 11, "bold"),
                  bg="#4ade80", fg=BG, bd=0, padx=16, pady=6, cursor="hand2",
                  command=self._run_analysis).pack(side="left")

        # Tab bar
        self.tab_frame = tk.Frame(self.root, bg=BG)
        self.tab_frame.pack(fill="x", padx=30)

        self.tabs = {}
        self.active_tab = tk.StringVar(value="risk")
        for name, key in [("Risk Metrics", "risk"), ("Diversification", "div"), ("Summary", "summary")]:
            btn = tk.Button(self.tab_frame, text=name, font=("Courier", 10),
                           bg=PANEL, fg=MUTED, bd=0, padx=16, pady=6, cursor="hand2",
                           command=lambda k=key: self._switch_tab(k))
            btn.pack(side="left", padx=(0, 2))
            self.tabs[key] = btn

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(4, 0))

        # Content area
        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=10)

        self._show_welcome()

    def _switch_tab(self, key):
        self.active_tab.set(key)
        for k, btn in self.tabs.items():
            btn.configure(fg="#4a9eff" if k == key else MUTED,
                         bg="#1a1a2e" if k == key else PANEL)
        if hasattr(self, '_results') and self._results:
            self._render_tab(key)

    def _show_welcome(self):
        for w in self.content.winfo_children():
            w.destroy()
        tk.Label(self.content,
                 text="Enter your tickers and click Analyse →",
                 font=("Courier", 14), bg=BG, fg=MUTED).pack(expand=True)

    def _show_error(self, msg):
        for w in self.content.winfo_children():
            w.destroy()
        tk.Label(self.content, text=f"Error: {msg}",
                 font=("Courier", 12), bg=BG, fg=ERROR).pack(expand=True)

    def _run_analysis(self):
        raw = self.tickers_entry.get().strip()
        tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
        start = self.start_entry.get().strip()

        try:
            rf_pct = float(self.rf_entry.get().strip()) / 100
        except ValueError:
            self._show_error("Invalid Rf value")
            return

        if len(tickers) < 2:
            self._show_error("Enter at least 2 tickers")
            return

        for w in self.content.winfo_children():
            w.destroy()
        tk.Label(self.content, text="Downloading data...",
                 font=("Courier", 12), bg=BG, fg=MUTED).pack(expand=True)
        self.root.update()

        try:
            data = yf.download(tickers, start=start, auto_adjust=True, progress=False)["Close"]
            if data.empty:
                self._show_error("No data returned — check tickers")
                return

            returns = data.pct_change(fill_method=None).dropna()
            returns_np = returns.values
            n = returns_np.shape[0]

            # ── RISK METRICS ─────────────────────────────────────────
            mean_d = np.mean(returns_np, axis=0)
            std_d = np.std(returns_np, ddof=1, axis=0)
            mean_a = mean_d * 252
            std_a = std_d * np.sqrt(252)
            var_95 = mean_d - 1.645 * std_d
            var_99 = mean_d - 2.326 * std_d
            rf_d = rf_pct / 252
            sharpe = (mean_d - rf_d) / std_d * np.sqrt(252)

            cvar_list = []
            for i in range(returns_np.shape[1]):
                col = returns_np[:, i]
                tail = col[col < var_95[i]]
                cvar_list.append(np.mean(tail) if len(tail) > 0 else np.nan)
            cvar_95 = np.array(cvar_list)

            # ── DIVERSIFICATION ───────────────────────────────────────
            cov = np.cov(returns_np.T)
            eigenvalues, eigenvectors = np.linalg.eigh(cov)
            eigenvalues_sorted = eigenvalues[::-1]
            eigenvectors_sorted = eigenvectors[:, ::-1]
            total_var = np.sum(eigenvalues_sorted)
            pct = (eigenvalues_sorted / total_var) * 100
            cum_pct = np.cumsum(pct)
            n_factors_80 = np.argmax(cum_pct >= 80) + 1
            dominant_vec = eigenvectors_sorted[:, 0]
            corr = np.corrcoef(returns_np.T)

            self._results = {
                "tickers": list(returns.columns),
                "mean_d": mean_d, "std_d": std_d,
                "mean_a": mean_a, "std_a": std_a,
                "var_95": var_95, "var_99": var_99,
                "cvar_95": cvar_95, "sharpe": sharpe,
                "eigenvalues": eigenvalues_sorted, "pct": pct,
                "cum_pct": cum_pct, "n_factors_80": n_factors_80,
                "dominant_vec": dominant_vec, "corr": corr,
                "n_days": n, "rf_pct": rf_pct,
            }

            self._switch_tab("risk")

        except Exception as e:
            self._show_error(str(e))

    def _render_tab(self, key):
        for w in self.content.winfo_children():
            w.destroy()

        r = self._results
        tickers = r["tickers"]

        if key == "risk":
            self._render_risk(r, tickers)
        elif key == "div":
            self._render_div(r, tickers)
        elif key == "summary":
            self._render_summary(r, tickers)

    def _table(self, parent, headers, rows, col_w=None):
        f = tk.Frame(parent, bg=BG)
        if col_w is None:
            col_w = [120] * len(headers)
        for j, h in enumerate(headers):
            tk.Label(f, text=h, font=("Courier", 9, "bold"),
                     bg=PANEL, fg="#4a9eff", width=col_w[j]//8,
                     relief="flat", pady=4).grid(row=0, column=j, padx=1, pady=1, sticky="ew")
        for i, row in enumerate(rows):
            bg = BG if i % 2 == 0 else "#151528"
            for j, val in enumerate(row):
                tk.Label(f, text=val, font=("Courier", 9),
                         bg=bg, fg=TEXT, width=col_w[j]//8,
                         pady=3).grid(row=i+1, column=j, padx=1, pady=0, sticky="ew")
        return f

    def _section(self, parent, title):
        tk.Label(parent, text=title, font=("Courier", 10, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(12, 4))
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=(0, 6))

    def _render_risk(self, r, tickers):
        canvas = tk.Canvas(self.content, bg=BG, bd=0, highlightthickness=0)
        scroll = tk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=BG)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self._section(frame, "INDIVIDUAL RISK METRICS")

        headers = ["Ticker", "Daily Return", "Annual Return", "Daily Vol", "Annual Vol", "Sharpe"]
        rows = []
        for i, t in enumerate(tickers):
            rows.append([
                t,
                f"{r['mean_d'][i]*100:+.3f}%",
                f"{r['mean_a'][i]*100:+.1f}%",
                f"{r['std_d'][i]*100:.3f}%",
                f"{r['std_a'][i]*100:.1f}%",
                f"{r['sharpe'][i]:.2f}",
            ])
        self._table(frame, headers, rows, [80,110,110,100,100,90]).pack(anchor="w")

        self._section(frame, "VALUE AT RISK & CVAR")

        headers2 = ["Ticker", "VaR 95%", "VaR 99%", "CVaR 95%", "Interpretation"]
        rows2 = []
        for i, t in enumerate(tickers):
            v95 = r['var_95'][i]
            v99 = r['var_99'][i]
            cv = r['cvar_95'][i]
            interp = "High risk" if v95 < -0.05 else "Moderate" if v95 < -0.03 else "Low risk"
            rows2.append([
                t,
                f"{v95*100:.2f}%",
                f"{v99*100:.2f}%",
                f"{cv*100:.2f}%" if not np.isnan(cv) else "n/a",
                interp,
            ])
        self._table(frame, headers2, rows2, [80,90,90,90,120]).pack(anchor="w")

        self._section(frame, "RISK SUMMARY")
        best_sharpe = tickers[np.argmax(r['sharpe'])]
        worst_var = tickers[np.argmin(r['var_95'])]
        best_var = tickers[np.argmax(r['var_95'])]

        for line in [
            f"Best risk-adjusted return (Sharpe):  {best_sharpe}  —  {np.max(r['sharpe']):.2f}",
            f"Highest daily risk (worst VaR 95%):  {worst_var}  —  {np.min(r['var_95'])*100:.2f}%",
            f"Lowest daily risk (best VaR 95%):    {best_var}  —  {np.max(r['var_95'])*100:.2f}%",
            f"Risk-free rate used:                 {r['rf_pct']*100:.1f}% annual",
            f"Data points:                         {r['n_days']} trading days",
        ]:
            tk.Label(frame, text=line, font=("Courier", 10), bg=BG, fg=TEXT).pack(anchor="w", pady=1)

    def _render_div(self, r, tickers):
        canvas = tk.Canvas(self.content, bg=BG, bd=0, highlightthickness=0)
        scroll = tk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=BG)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self._section(frame, "PCA — RISK FACTORS")

        headers = ["Factor", "Eigenvalue", "% of Risk", "Cumulative %", "Real factor?"]
        rows = []
        for i in range(len(r['eigenvalues'])):
            real = "YES" if r['pct'][i] >= 10 else "borderline" if r['pct'][i] >= 5 else "noise"
            rows.append([
                f"Factor {i+1}",
                f"{r['eigenvalues'][i]:.6f}",
                f"{r['pct'][i]:.1f}%",
                f"{r['cum_pct'][i]:.1f}%",
                real,
            ])
        self._table(frame, headers, rows, [80,110,90,110,100]).pack(anchor="w")

        self._section(frame, "DOMINANT RISK FACTOR — LOADINGS")
        tk.Label(frame, text="How much each asset drives the main risk factor:",
                 font=("Courier", 9), bg=BG, fg=MUTED).pack(anchor="w", pady=(0,6))

        headers2 = ["Ticker", "Loading", "Abs Loading", "Role"]
        rows2 = []
        for i, t in enumerate(tickers):
            load = r['dominant_vec'][i]
            role = "Strong driver" if abs(load) > 0.5 else "Moderate" if abs(load) > 0.25 else "Independent"
            rows2.append([t, f"{load:.4f}", f"{abs(load):.4f}", role])
        self._table(frame, headers2, rows2, [80,100,100,120]).pack(anchor="w")

        self._section(frame, "DIVERSIFICATION ASSESSMENT")
        n = r['n_factors_80']
        dom_pct = r['pct'][0]
        assessment = "Well diversified" if dom_pct < 40 else "Moderately concentrated" if dom_pct < 60 else "Highly concentrated"

        for line in [
            f"Dominant factor explains:    {dom_pct:.1f}% of total risk",
            f"Factors needed for 80%:      {n} out of {len(tickers)}",
            f"Diversification assessment:  {assessment}",
            f"Effective risk dimensions:   {n} independent bets",
        ]:
            tk.Label(frame, text=line, font=("Courier", 10), bg=BG, fg=TEXT).pack(anchor="w", pady=1)

        self._section(frame, "CORRELATION MATRIX")
        corr_headers = [""] + tickers
        corr_rows = []
        for i, t in enumerate(tickers):
            row = [t]
            for j in range(len(tickers)):
                v = r['corr'][i][j]
                row.append(f"{v:.2f}")
            corr_rows.append(row)
        self._table(frame, corr_headers, corr_rows).pack(anchor="w")

    def _render_summary(self, r, tickers):
        frame = tk.Frame(self.content, bg=BG)
        frame.pack(fill="both", expand=True)

        self._section(frame, "PORTFOLIO SUMMARY")

        best_sharpe_idx = np.argmax(r['sharpe'])
        worst_var_idx = np.argmin(r['var_95'])
        dom_pct = r['pct'][0]
        n_factors = r['n_factors_80']
        assessment = "Well diversified" if dom_pct < 40 else "Moderately concentrated" if dom_pct < 60 else "Highly concentrated"

        lines = [
            ("Assets analysed", f"{len(tickers)}  —  {', '.join(tickers)}"),
            ("Best Sharpe", f"{tickers[best_sharpe_idx]}  —  {r['sharpe'][best_sharpe_idx]:.2f}"),
            ("Highest risk asset", f"{tickers[worst_var_idx]}  —  VaR {r['var_95'][worst_var_idx]*100:.2f}%/day"),
            ("Dominant risk factor", f"{dom_pct:.1f}% of total portfolio risk"),
            ("Real risk dimensions", f"{n_factors} independent factors (80% threshold)"),
            ("Diversification", assessment),
            ("Risk-free rate", f"{r['rf_pct']*100:.1f}% annual"),
            ("Data points", f"{r['n_days']} trading days"),
        ]

        for label, value in lines:
            row = tk.Frame(frame, bg=BG)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{label}:", font=("Courier", 10),
                     bg=BG, fg=MUTED, width=25, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Courier", 10, "bold"),
                     bg=BG, fg=TEXT, anchor="w").pack(side="left")

        self._section(frame, "INTERPRETATION")

        avg_sharpe = np.mean(r['sharpe'])
        if avg_sharpe > 1.5:
            sharpe_text = "Strong risk-adjusted returns across the portfolio."
        elif avg_sharpe > 1.0:
            sharpe_text = "Acceptable risk-adjusted returns — room for improvement."
        else:
            sharpe_text = "Weak risk-adjusted returns — consider rebalancing."

        dominant_ticker = tickers[np.argmax(np.abs(r['dominant_vec']))]

        for line in [
            sharpe_text,
            f"The dominant risk factor is driven primarily by {dominant_ticker}.",
            f"With {n_factors} real risk dimensions, your portfolio is {assessment.lower()}.",
            "Use VaR and CVaR to set position size limits and stop losses.",
        ]:
            tk.Label(frame, text=f"→  {line}", font=("Courier", 10),
                     bg=BG, fg=TEXT, wraplength=900, justify="left").pack(anchor="w", pady=2)


if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioRiskManager(root)
    root.mainloop()
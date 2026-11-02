import calendar
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Conversation, Message, Usage, FallbackEvent, HandoffEvent, Tenant
from app.core.logging import logger


class AnalyticsService:
    @classmethod
    def calculate_kpis(
        cls,
        total_conversations: int,
        total_messages: int,
        total_tokens: int,
        avg_latency_ms: float,
        total_fallbacks: int,
        total_handoffs: int,
    ) -> Dict[str, Any]:
        """Pure business logic calculation for AI KPIs."""
        if total_conversations > 0:
            fallback_rate = round((total_fallbacks / total_conversations) * 100, 1)
            handoff_rate = round((total_handoffs / total_conversations) * 100, 1)
            resolution_rate = round(max(0.0, 100.0 - fallback_rate), 1)
        else:
            fallback_rate = 0.0
            handoff_rate = 0.0
            resolution_rate = 100.0

        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "avg_latency_ms": round(avg_latency_ms, 1),
            "resolution_rate_percent": resolution_rate,
            "handoff_rate_percent": handoff_rate,
            "fallback_rate_percent": fallback_rate,
        }

    @classmethod
    def _render_quota_rows(cls, quotas_list: List[Dict[str, Any]]) -> str:
        if not quotas_list:
            return '<tr><td colspan="7" class="py-8 text-center text-slate-400">Belum ada tenant yang terdaftar di database.</td></tr>'

        # Hitung siklus masa berlaku bulan berjalan
        now = datetime.now()
        _, last_day = calendar.monthrange(now.year, now.month)
        cycle_end = datetime(now.year, now.month, last_day)
        reset_date = cycle_end + timedelta(days=1)
        days_left = max(0, (cycle_end.date() - now.date()).days)
        months_id = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        cycle_end_str = f"{last_day} {months_id[now.month]} {now.year}"
        reset_date_str = f"1 {months_id[reset_date.month]} {reset_date.year}"

        rows = []
        for t in quotas_list:
            tier = (t.get("package_tier") or "pixel").lower()
            used = t.get("used_messages", 0)
            limit = t.get("monthly_quota", 500)
            remaining = t.get("remaining_messages", max(0, limit - used))
            pct = t.get("percentage_used", round((used / limit) * 100, 1) if limit > 0 else 0)
            name = t.get("name", t.get("tenant_id", "Unknown"))
            t_id = t.get("tenant_id", "")

            # Tier styling (Light theme friendly)
            if tier == "infinity":
                tier_badge = '<span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200">INFINITY</span>'
            elif tier == "nexus":
                tier_badge = '<span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">NEXUS</span>'
            elif tier == "pulse":
                tier_badge = '<span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-sky-50 text-sky-700 border border-sky-200">PULSE</span>'
            else:
                tier_badge = '<span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-300">PIXEL</span>'

            # Status classification
            if pct >= 100 or t.get("is_quota_exhausted"):
                status_cat = "blocked"
                status_badge = '<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 inline-flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span> Habis (Blocked)</span>'
                bar_color = "bg-rose-500"
                pct_color = "text-rose-600 font-bold"
            elif pct >= 80:
                status_cat = "warning"
                status_badge = '<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-800 border border-amber-200 inline-flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Waspada (≥80%)</span>'
                bar_color = "bg-amber-500"
                pct_color = "text-amber-700 font-bold"
            else:
                status_cat = "normal"
                status_badge = '<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 inline-flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Aman</span>'
                bar_color = "bg-emerald-500"
                pct_color = "text-emerald-700 font-semibold"

            bar_width = min(100.0, float(pct))

            rows.append(f"""
            <tr class="tenant-row hover:bg-slate-50 transition border-b border-slate-200/80" data-name="{name.lower()}" data-id="{t_id.lower()}" data-status="{status_cat}">
                <td class="py-3.5 px-5">
                    <div class="font-semibold text-slate-900">{name}</div>
                    <div class="text-xs text-slate-500 font-mono mt-0.5">{t_id}</div>
                </td>
                <td class="py-3.5 px-5">{tier_badge}</td>
                <td class="py-3.5 px-5 font-mono text-sm text-slate-800">
                    <span class="font-bold text-slate-900">{used:,}</span> <span class="text-slate-500 text-xs font-normal">/ {limit:,}</span>
                </td>
                <td class="py-3.5 px-5 font-mono text-sm font-semibold text-slate-700">
                    {remaining:,}
                </td>
                <td class="py-3.5 px-5">
                    <div class="flex items-center gap-3">
                        <div class="w-28 bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
                            <div class="{bar_color} h-2 rounded-full transition-all duration-500" style="width: {bar_width}%;"></div>
                        </div>
                        <span class="text-xs {pct_color} font-mono">{pct}%</span>
                    </div>
                </td>
                <td class="py-3.5 px-5">
                    <div class="text-xs font-semibold text-slate-900">s/d {cycle_end_str}</div>
                    <div class="text-[11px] text-indigo-600 font-mono mt-0.5">Reset {reset_date_str} ({days_left} hr lagi)</div>
                </td>
                <td class="py-3.5 px-5">{status_badge}</td>
            </tr>
            """)
        return "".join(rows)

    @classmethod
    def render_dashboard_html(cls, data: Dict[str, Any], days: int = 30) -> str:
        """Menghasilkan template HTML visual modern ala SaaS Admin Dashboard (Tema Terang / Light Mode)."""
        kpis = data.get("kpis", {})
        layers = data.get("layer_breakdown", {})
        top_q = data.get("top_questions", [])
        unanswered = data.get("unanswered_queries", [])
        tenant_quotas = data.get("tenant_quotas", [])

        quota_rows_html = cls._render_quota_rows(tenant_quotas)
        total_tenants = len(tenant_quotas)
        blocked_tenants = sum(1 for t in tenant_quotas if t.get("percentage_used", 0) >= 100 or t.get("is_quota_exhausted"))
        warning_tenants = sum(1 for t in tenant_quotas if 80 <= t.get("percentage_used", 0) < 100)

        # Tanggal siklus saat ini
        now = datetime.now()
        _, last_day = calendar.monthrange(now.year, now.month)
        months_id = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        current_cycle_label = f"{months_id[now.month]} {now.year}"
        reset_label = f"1 {months_id[now.month % 12 + 1]} {now.year + (1 if now.month == 12 else 0)}"

        return f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Engine Intelligence Dashboard — PakDe Group</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'monospace'],
                    }}
                }}
            }}
        }}
    </script>
    <style>
        html {{
            scroll-behavior: smooth;
        }}
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #f8fafc;
        }}
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: #f1f5f9;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #cbd5e1;
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #94a3b8;
        }}
    </style>
</head>
<body class="text-slate-800 bg-slate-50 min-h-screen flex antialiased selection:bg-indigo-600 selection:text-white">

    <!-- Left Sidebar (Fixed on Desktop) -->
    <aside class="w-64 bg-white border-r border-slate-200/90 flex flex-col justify-between fixed inset-y-0 left-0 z-40 hidden md:flex shadow-sm">
        <div>
            <!-- Brand Logo Header -->
            <div class="h-16 px-6 flex items-center gap-3 border-b border-slate-200 bg-white">
                <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 via-indigo-600 to-sky-500 flex items-center justify-center text-white font-black text-lg shadow-md shadow-indigo-500/20">
                    ✦
                </div>
                <div>
                    <div class="font-extrabold text-sm tracking-tight text-slate-900 flex items-center gap-1.5">
                        PAKDE AI
                        <span class="text-[10px] font-bold px-1.5 py-0.2 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">CORE</span>
                    </div>
                    <div class="text-[11px] text-slate-500">Intelligence Platform</div>
                </div>
            </div>

            <!-- Navigation Links -->
            <nav class="p-4 space-y-1 text-sm font-medium" id="sidebarNav">
                <div class="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">Main Menu</div>
                
                <a href="#overview" data-target="overview" class="nav-link flex items-center justify-between px-3 py-2.5 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200/80 font-bold transition shadow-xs">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                        <span>Overview & KPI</span>
                    </div>
                </a>

                <a href="#layers" data-target="layers" class="nav-link flex items-center justify-between px-3 py-2.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition font-medium">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                        <span>Multi-Tier Routing</span>
                    </div>
                </a>

                <a href="#tenants" data-target="tenants" class="nav-link flex items-center justify-between px-3 py-2.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition font-medium">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                        <span>Kuota Klien (L4)</span>
                    </div>
                    <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-mono border border-slate-200">{total_tenants}</span>
                </a>

                <a href="#questions" data-target="questions" class="nav-link flex items-center justify-between px-3 py-2.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition font-medium">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"></path></svg>
                        <span>Pertanyaan Populer</span>
                    </div>
                </a>

                <a href="#insights" data-target="insights" class="nav-link flex items-center justify-between px-3 py-2.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition font-medium">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>
                        <span>Insight Pelanggan</span>
                    </div>
                </a>

                <div class="pt-4 px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">External Links</div>

                <a href="/docs" target="_blank" class="flex items-center justify-between px-3 py-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition">
                    <span class="flex items-center gap-3">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
                        <span>Swagger Docs</span>
                    </span>
                    <span class="text-xs text-slate-400 font-mono">↗</span>
                </a>

                <a href="/widget/index.html" target="_blank" class="flex items-center justify-between px-3 py-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition">
                    <span class="flex items-center gap-3">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
                        <span>Test Chatbot</span>
                    </span>
                    <span class="text-xs text-slate-400 font-mono">↗</span>
                </a>
            </nav>
        </div>

        <!-- Sidebar System Environment Card -->
        <div class="p-4 border-t border-slate-200">
            <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                <div class="flex items-center justify-between text-xs mb-1.5">
                    <span class="font-bold text-slate-800">Engine Node</span>
                    <span class="inline-flex items-center gap-1.5 text-[11px] text-emerald-700 font-bold bg-emerald-100/80 px-2 py-0.5 rounded-full">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        Online
                    </span>
                </div>
                <div class="text-[11px] text-slate-600 font-mono truncate">AI-Assistant-DKreasi</div>
                <div class="text-[10px] text-slate-500 font-mono mt-0.5">Siklus: {current_cycle_label}</div>
            </div>
        </div>
    </aside>

    <!-- Main Content Canvas -->
    <div class="flex-1 md:ml-64 flex flex-col min-w-0">
        
        <!-- Sticky Top App Bar -->
        <header class="h-16 px-6 lg:px-10 border-b border-slate-200 bg-white/90 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between gap-4">
            <div class="flex items-center gap-3">
                <div class="md:hidden w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm">
                    ✦
                </div>
                <div>
                    <h1 class="text-sm font-bold text-slate-900 tracking-tight">AI Engine Intelligence Dashboard</h1>
                    <div class="text-[11px] text-slate-500 hidden sm:block">Monitoring Performa Percakapan & Insight Pelanggan (D-Kreasi, Webia, D-Karsa)</div>
                </div>
            </div>

            <!-- Top Actions -->
            <div class="flex items-center gap-2 sm:gap-3">
                <!-- Days Period Selector -->
                <div class="flex items-center bg-slate-100 border border-slate-200 rounded-lg p-0.5 text-xs font-semibold">
                    <a href="?days=7" class="px-2.5 py-1 rounded-md {'bg-indigo-600 text-white shadow-xs' if days == 7 else 'text-slate-600 hover:text-slate-900 transition'}">7H</a>
                    <a href="?days=30" class="px-2.5 py-1 rounded-md {'bg-indigo-600 text-white shadow-xs' if days == 30 else 'text-slate-600 hover:text-slate-900 transition'}">30H</a>
                    <a href="?days=90" class="px-2.5 py-1 rounded-md {'bg-indigo-600 text-white shadow-xs' if days == 90 else 'text-slate-600 hover:text-slate-900 transition'}">90H</a>
                </div>

                <a href="/api/v1/analytics/overview?days={days}" target="_blank" class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 shadow-xs transition">
                    <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    <span>Raw JSON</span>
                </a>

                <button onclick="window.location.reload()" class="p-1.5 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 text-slate-600 hover:text-slate-900 shadow-xs transition" title="Refresh Data">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                </button>
            </div>
        </header>

        <!-- Main Body Dashboard Sections -->
        <main class="p-6 lg:p-10 space-y-8 flex-1">

            <!-- SECTION 1: EXECUTIVE KPI BENTO GRID -->
            <section id="overview" class="scroll-mt-24 space-y-4 rounded-2xl transition-all duration-300">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-base font-bold text-slate-900 tracking-tight">Key Performance Indicators</h2>
                        <p class="text-xs text-slate-500">Performa penyelesaian pertanyaan dan efisiensi model AI</p>
                    </div>
                    <span class="text-xs text-slate-500 font-mono">Periode {days} Hari Terakhir</span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <!-- KPI 1 -->
                    <div class="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-slate-300 transition relative overflow-hidden group">
                        <div class="flex items-center justify-between text-slate-500 mb-3">
                            <span class="text-xs font-bold uppercase tracking-wider">Total Obrolan</span>
                            <div class="w-8 h-8 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center font-bold text-sm border border-sky-100">
                                💬
                            </div>
                        </div>
                        <div class="text-3xl font-extrabold text-slate-900 tracking-tight">{kpis.get('total_conversations', 0):,}</div>
                        <div class="mt-2 text-xs text-slate-500 flex items-center gap-1.5">
                            <span class="text-emerald-600 font-bold">{kpis.get('total_messages', 0):,}</span> total pesan dipertukarkan
                        </div>
                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-sky-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition"></div>
                    </div>

                    <!-- KPI 2 -->
                    <div class="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-slate-300 transition relative overflow-hidden group">
                        <div class="flex items-center justify-between text-slate-500 mb-3">
                            <span class="text-xs font-bold uppercase tracking-wider">Resolution Rate</span>
                            <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-sm border border-emerald-100">
                                ⚡
                            </div>
                        </div>
                        <div class="text-3xl font-extrabold text-emerald-600 tracking-tight">{kpis.get('resolution_rate_percent', 100.0)}%</div>
                        <div class="mt-2 text-xs text-slate-500">
                            Terjawab mandiri oleh AI tanpa eskalasi
                        </div>
                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 to-teal-500 opacity-0 group-hover:opacity-100 transition"></div>
                    </div>

                    <!-- KPI 3 -->
                    <div class="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-slate-300 transition relative overflow-hidden group">
                        <div class="flex items-center justify-between text-slate-500 mb-3">
                            <span class="text-xs font-bold uppercase tracking-wider">Handoff WhatsApp</span>
                            <div class="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-sm border border-amber-100">
                                📲
                            </div>
                        </div>
                        <div class="text-3xl font-extrabold text-amber-600 tracking-tight">{kpis.get('handoff_rate_percent', 0.0)}%</div>
                        <div class="mt-2 text-xs text-slate-500">
                            Prospek matang diarahkan ke CS/Sales
                        </div>
                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 to-rose-500 opacity-0 group-hover:opacity-100 transition"></div>
                    </div>

                    <!-- KPI 4 -->
                    <div class="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-slate-300 transition relative overflow-hidden group">
                        <div class="flex items-center justify-between text-slate-500 mb-3">
                            <span class="text-xs font-bold uppercase tracking-wider">Rata-rata Latensi</span>
                            <div class="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-sm border border-indigo-100">
                                ⏱️
                            </div>
                        </div>
                        <div class="text-3xl font-extrabold text-indigo-600 tracking-tight font-mono">{kpis.get('avg_latency_ms', 0)} <span class="text-sm font-sans font-normal text-slate-500">ms</span></div>
                        <div class="mt-2 text-xs text-slate-500 font-mono">
                            Konsumsi {kpis.get('total_tokens', 0):,} token LLM
                        </div>
                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition"></div>
                    </div>
                </div>
            </section>

            <!-- SECTION 2: MULTI-TIER LAYER ARCHITECTURE -->
            <section id="layers" class="scroll-mt-24 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4 transition-all duration-300">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                        <h2 class="text-base font-bold text-slate-900 flex items-center gap-2">
                            <span>Distribusi Beban per Layer Layanan</span>
                            <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">Multi-Tier Architecture</span>
                        </h2>
                        <p class="text-xs text-slate-500 mt-0.5">Pemecahan lalu lintas pertanyaan berdasarkan arsitektur 4 layer PakDe Group</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <!-- Layer 1 -->
                    <div class="p-4 rounded-xl bg-sky-50/50 border border-sky-100 hover:border-sky-300 transition">
                        <div class="flex items-center justify-between">
                            <div class="text-xs font-bold text-sky-700">L1 · D-Kreasi Concierge</div>
                            <span class="text-[10px] px-1.5 py-0.2 rounded bg-sky-100 text-sky-800 font-mono font-semibold">Router</span>
                        </div>
                        <div class="text-2xl font-extrabold mt-2 text-slate-900 font-mono">{layers.get('l1', {}).get('messages', 0)} <span class="text-xs font-sans text-slate-500 font-normal">pesan</span></div>
                        <div class="text-xs text-slate-500 mt-1 font-mono">{layers.get('l1', {}).get('tokens', 0):,} tokens</div>
                    </div>

                    <!-- Layer 2 -->
                    <div class="p-4 rounded-xl bg-rose-50/50 border border-rose-100 hover:border-rose-300 transition">
                        <div class="flex items-center justify-between">
                            <div class="text-xs font-bold text-rose-700">L2 · D-Karsa Undangan</div>
                            <span class="text-[10px] px-1.5 py-0.2 rounded bg-rose-100 text-rose-800 font-mono font-semibold">Undangan</span>
                        </div>
                        <div class="text-2xl font-extrabold mt-2 text-slate-900 font-mono">{layers.get('l2', {}).get('messages', 0)} <span class="text-xs font-sans text-slate-500 font-normal">pesan</span></div>
                        <div class="text-xs text-slate-500 mt-1 font-mono">{layers.get('l2', {}).get('tokens', 0):,} tokens</div>
                    </div>

                    <!-- Layer 3 -->
                    <div class="p-4 rounded-xl bg-amber-50/50 border border-amber-100 hover:border-amber-300 transition">
                        <div class="flex items-center justify-between">
                            <div class="text-xs font-bold text-amber-700">L3 · Webia Sales AI</div>
                            <span class="text-[10px] px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 font-mono font-semibold">Konsultan</span>
                        </div>
                        <div class="text-2xl font-extrabold mt-2 text-slate-900 font-mono">{layers.get('l3', {}).get('messages', 0)} <span class="text-xs font-sans text-slate-500 font-normal">pesan</span></div>
                        <div class="text-xs text-slate-500 mt-1 font-mono">{layers.get('l3', {}).get('tokens', 0):,} tokens</div>
                    </div>

                    <!-- Layer 4 -->
                    <div class="p-4 rounded-xl bg-emerald-50/50 border border-emerald-100 hover:border-emerald-300 transition">
                        <div class="flex items-center justify-between">
                            <div class="text-xs font-bold text-emerald-700">L4 · Business Chatbot</div>
                            <span class="text-[10px] px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 font-mono font-semibold">Tenants</span>
                        </div>
                        <div class="text-2xl font-extrabold mt-2 text-slate-900 font-mono">{layers.get('l4', {}).get('messages', 0)} <span class="text-xs font-sans text-slate-500 font-normal">pesan</span></div>
                        <div class="text-xs text-slate-500 mt-1 font-mono">{layers.get('l4', {}).get('tokens', 0):,} tokens</div>
                    </div>
                </div>
            </section>

            <!-- SECTION 3: TENANT QUOTA ENFORCEMENT TABLE -->
            <section id="tenants" class="scroll-mt-24 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4 transition-all duration-300">
                <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <h2 class="text-base font-bold text-slate-900">Monitoring Kuota Klien (Tenant Quota Enforcement)</h2>
                            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono">Layer 4 Tenants</span>
                        </div>
                        <p class="text-xs text-slate-500 mt-0.5">Pemantauan konsumsi pesan bulanan klien Webia terhadap limit paket langganan</p>
                    </div>

                    <!-- Interactive Controls: Search & Status Filters -->
                    <div class="flex flex-wrap items-center gap-2">
                        <!-- Search Box -->
                        <div class="relative">
                            <input type="text" id="tenantSearchInput" placeholder="Cari nama / ID..." class="w-48 sm:w-56 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:bg-white transition shadow-2xs">
                        </div>

                        <!-- Status Filter Buttons -->
                        <div class="flex items-center bg-slate-100 border border-slate-200 rounded-lg p-0.5 text-xs font-medium">
                            <button onclick="filterTenants('all')" class="filter-btn px-2.5 py-1 rounded-md bg-white text-slate-900 font-bold shadow-2xs transition" data-filter="all">Semua ({total_tenants})</button>
                            <button onclick="filterTenants('blocked')" class="filter-btn px-2.5 py-1 rounded-md text-rose-700 hover:text-slate-900 transition font-medium" data-filter="blocked">Habis ({blocked_tenants})</button>
                            <button onclick="filterTenants('warning')" class="filter-btn px-2.5 py-1 rounded-md text-amber-700 hover:text-slate-900 transition font-medium" data-filter="warning">Waspada ({warning_tenants})</button>
                            <button onclick="filterTenants('normal')" class="filter-btn px-2.5 py-1 rounded-md text-emerald-700 hover:text-slate-900 transition font-medium" data-filter="normal">Aman</button>
                        </div>
                    </div>
                </div>

                <!-- Data Table -->
                <div class="overflow-x-auto rounded-xl border border-slate-200 bg-white">
                    <table class="w-full text-left text-sm text-slate-700">
                        <thead class="text-xs uppercase bg-slate-50 text-slate-600 border-b border-slate-200 font-bold tracking-wider">
                            <tr>
                                <th class="py-3.5 px-5">Nama Klien / Bisnis</th>
                                <th class="py-3.5 px-5">Paket Tier</th>
                                <th class="py-3.5 px-5">Pemakaian Pesan</th>
                                <th class="py-3.5 px-5">Sisa Pesan</th>
                                <th class="py-3.5 px-5">Persentase</th>
                                <th class="py-3.5 px-5">Masa Berlaku / Reset</th>
                                <th class="py-3.5 px-5">Status Kuota</th>
                            </tr>
                        </thead>
                        <tbody id="tenantTableBody" class="divide-y divide-slate-100">
                            {quota_rows_html}
                        </tbody>
                    </table>
                </div>

                <div class="flex flex-col sm:flex-row sm:items-center justify-between text-xs text-slate-500 pt-1">
                    <span>Menampilkan seluruh tenant aktif di database SQLite PakDe Group.</span>
                    <span class="font-mono text-slate-600">Siklus Kuota: Bulanan · Reset Otomatis Setiap <strong>{reset_label}</strong></span>
                </div>
            </section>

            <!-- SECTION 4: SPLIT 2 COLUMN (TOP QUESTIONS & UNANSWERED QUERIES) -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

                <!-- Left: Top Frequent Questions -->
                <section id="questions" class="scroll-mt-24 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4 transition-all duration-300">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="text-base font-bold text-slate-900 flex items-center gap-2">🔥 Pertanyaan Paling Populer</span>
                        </div>
                        <span class="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono border border-slate-200">Top Inquiries</span>
                    </div>

                    <div class="space-y-2.5">
                        {"".join([f'''
                        <div class="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 hover:bg-slate-100/70 transition group">
                            <div class="flex items-center gap-3 pr-4 truncate">
                                <span class="w-6 h-6 rounded-full bg-white border border-slate-200 text-slate-600 text-[11px] font-mono font-bold flex items-center justify-center shrink-0 shadow-2xs">#{idx+1}</span>
                                <span class="text-sm text-slate-800 truncate group-hover:text-slate-900 transition font-medium">"{q.get('query', '')}"</span>
                            </div>
                            <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 shrink-0 font-mono">
                                {q.get('count', 0)}x ditanya
                            </span>
                        </div>
                        ''' for idx, q in enumerate(top_q)]) if top_q else '<p class="text-sm text-slate-400 py-8 text-center">Belum ada rekaman riwayat pertanyaan pengunjung.</p>'}
                    </div>
                </section>

                <!-- Right: Unanswered Queries & Product Insights -->
                <section id="insights" class="scroll-mt-24 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4 transition-all duration-300">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="text-base font-bold text-slate-900 flex items-center gap-2">💡 Insight Kebutuhan Pelanggan Baru</span>
                        </div>
                        <span class="text-xs font-bold text-rose-700 px-2 py-0.5 rounded bg-rose-50 border border-rose-200 font-mono">Unanswered Queries</span>
                    </div>

                    <div class="space-y-2.5">
                        {"".join([f'''
                        <div class="p-3.5 rounded-xl bg-rose-50/50 border border-rose-200/80 hover:bg-rose-50 transition">
                            <div class="flex items-center justify-between text-xs text-slate-500 mb-1.5 font-mono">
                                <span class="uppercase tracking-wider font-bold text-rose-700">Layer {u.get('layer', 'N/A')}</span>
                                <span>{u.get('timestamp', '')}</span>
                            </div>
                            <p class="text-sm text-slate-800 font-medium">"{u.get('query', '')}"</p>
                        </div>
                        ''' for u in unanswered]) if unanswered else '<p class="text-sm text-slate-400 py-8 text-center">Tidak ada pertanyaan yang gagal dijawab (Akurasi 100%).</p>'}
                    </div>
                </section>

            </div>

        </main>

        <!-- Footer -->
        <footer class="h-14 px-6 lg:px-10 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 bg-white">
            <div>AI Engine by PakDe Group · D-Kreasi Central Ecosystem · Diperbarui otomatis setiap permintaan</div>
            <div class="font-mono text-[11px] text-emerald-700 font-semibold hidden sm:flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                Status: Healthy (200 OK)
            </div>
        </footer>

    </div>

    <!-- Client-side Interactive Filter & Dynamic Sidebar Navigation -->
    <script>
        // 1. Sidebar Active State & Smooth Navigation
        const navLinks = document.querySelectorAll('.nav-link');

        function setActiveMenu(targetId) {{
            navLinks.forEach(link => {{
                const target = link.getAttribute('data-target');
                const svg = link.querySelector('svg');
                if (target === targetId) {{
                    link.className = 'nav-link flex items-center justify-between px-3 py-2.5 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200/80 font-bold transition shadow-xs';
                    if (svg) svg.className = 'w-4 h-4 text-indigo-600';
                }} else {{
                    link.className = 'nav-link flex items-center justify-between px-3 py-2.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition font-medium';
                    if (svg) svg.className = 'w-4 h-4 text-slate-400';
                }}
            }});
        }}

        navLinks.forEach(link => {{
            link.addEventListener('click', function(e) {{
                const targetId = this.getAttribute('data-target');
                const targetElement = document.getElementById(targetId);
                if (targetElement) {{
                    e.preventDefault();
                    setActiveMenu(targetId);

                    const headerOffset = 80;
                    const elementPosition = targetElement.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                    window.scrollTo({{
                        top: offsetPosition,
                        behavior: 'smooth'
                    }});

                    history.pushState(null, null, '#' + targetId);

                    // Berikan efek highlight halus ke section target
                    targetElement.classList.add('ring-2', 'ring-indigo-500/40');
                    setTimeout(() => {{
                        targetElement.classList.remove('ring-2', 'ring-indigo-500/40');
                    }}, 1200);
                }}
            }});
        }});

        // 2. Auto sync sidebar active item saat user scroll halaman
        const sections = document.querySelectorAll('section[id]');
        window.addEventListener('scroll', () => {{
            let current = 'overview';
            sections.forEach(section => {{
                const sectionTop = section.offsetTop - 120;
                if (window.pageYOffset >= sectionTop) {{
                    current = section.getAttribute('id');
                }}
            }});
            setActiveMenu(current);
        }}, {{ passive: true }});

        // 3. Search & Status Filter untuk Tabel Kuota Tenant
        const searchInput = document.getElementById('tenantSearchInput');
        const rows = document.querySelectorAll('.tenant-row');
        let currentFilter = 'all';

        function applyFilters() {{
            const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
            rows.forEach(row => {{
                const name = row.getAttribute('data-name') || '';
                const id = row.getAttribute('data-id') || '';
                const status = row.getAttribute('data-status') || '';

                const matchesSearch = !query || name.includes(query) || id.includes(query);
                const matchesStatus = (currentFilter === 'all') || (status === currentFilter);

                if (matchesSearch && matchesStatus) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}

        if (searchInput) {{
            searchInput.addEventListener('input', applyFilters);
        }}

        function filterTenants(type) {{
            currentFilter = type;
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                if (btn.getAttribute('data-filter') === type) {{
                    btn.className = 'filter-btn px-2.5 py-1 rounded-md bg-white text-slate-900 font-bold shadow-2xs transition';
                }} else {{
                    btn.className = 'filter-btn px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 transition font-medium';
                }}
            }});
            applyFilters();
        }}
    </script>
</body>
</html>
"""

    @classmethod
    async def get_overview_metrics(cls, db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """Menghitung metrik performa AI secara menyeluruh dalam periode N hari terakhir."""
        since_date = datetime.now() - timedelta(days=days)

        try:
            # 1. Total Percakapan (Conversations)
            total_conv_stmt = select(func.count(Conversation.id)).where(Conversation.created_at >= since_date)
            total_conv = (await db.execute(total_conv_stmt)).scalar() or 0

            # 2. Total Pesan (Messages)
            total_msg_stmt = select(func.count(Message.id)).where(Message.created_at >= since_date)
            total_msg = (await db.execute(total_msg_stmt)).scalar() or 0

            # 3. Total Tokens & Rata-rata Latensi
            usage_agg_stmt = select(
                func.sum(Usage.total_tokens),
                func.avg(Usage.latency_ms),
                func.count(Usage.id)
            ).where(Usage.created_at >= since_date)
            usage_agg = (await db.execute(usage_agg_stmt)).first()
            total_tokens = usage_agg[0] or 0
            avg_latency = float(usage_agg[1] or 0.0)

            # 4. Total Fallback & Handoff Events
            fallback_cnt_stmt = select(func.count(FallbackEvent.id)).where(FallbackEvent.created_at >= since_date)
            total_fallbacks = (await db.execute(fallback_cnt_stmt)).scalar() or 0

            handoff_cnt_stmt = select(func.count(HandoffEvent.id)).where(HandoffEvent.created_at >= since_date)
            total_handoffs = (await db.execute(handoff_cnt_stmt)).scalar() or 0

            # 5. Hitung KPI Ringkasan
            kpis = cls.calculate_kpis(
                total_conversations=total_conv,
                total_messages=total_msg,
                total_tokens=total_tokens,
                avg_latency_ms=avg_latency,
                total_fallbacks=total_fallbacks,
                total_handoffs=total_handoffs,
            )

            # 6. Distribusi Beban per Layer (L1, L2, L3, L4)
            layer_breakdown = {}
            for layer_name in ["l1", "l2", "l3", "l4"]:
                stmt = select(
                    func.count(Usage.id),
                    func.sum(Usage.total_tokens)
                ).where(Usage.layer == layer_name, Usage.created_at >= since_date)
                row = (await db.execute(stmt)).first()
                layer_breakdown[layer_name] = {
                    "messages": row[0] or 0,
                    "tokens": row[1] or 0,
                }

            # 7. Pertanyaan Paling Sering Diajukan (Top Inquiries)
            top_q_stmt = select(
                Message.content,
                func.count(Message.id).label("freq")
            ).where(
                Message.role == "user",
                Message.created_at >= since_date
            ).group_by(Message.content).order_by(desc("freq")).limit(5)
            top_q_rows = (await db.execute(top_q_stmt)).all()
            top_questions = [{"query": r[0], "count": r[1]} for r in top_q_rows]

            # 8. Unanswered / Fallback Queries (Insight Produk)
            fallback_q_stmt = select(
                Message.content,
                Usage.layer,
                Usage.created_at
            ).join(
                Conversation, Conversation.id == Message.conversation_id
            ).join(
                Usage, Usage.session_id == Conversation.session_id
            ).where(
                Message.role == "user",
                Usage.is_fallback == True,
                Usage.created_at >= since_date
            ).order_by(desc(Usage.created_at)).limit(6)
            fallback_q_rows = (await db.execute(fallback_q_stmt)).all()
            unanswered_queries = [
                {"query": r[0], "layer": r[1], "timestamp": r[2].strftime("%d %b %H:%M") if r[2] else ""}
                for r in fallback_q_rows
            ]

            # 9. Aktivitas Percakapan Terbaru (Recent Activity)
            recent_conv_stmt = select(
                Conversation.session_id,
                Conversation.layer,
                Conversation.tenant_id,
                Conversation.created_at
            ).order_by(desc(Conversation.created_at)).limit(6)
            recent_rows = (await db.execute(recent_conv_stmt)).all()
            recent_activity = [
                {
                    "session_id": r[0],
                    "layer": r[1],
                    "tenant_id": r[2],
                    "time": r[3].strftime("%d %b %H:%M") if r[3] else "",
                }
                for r in recent_rows
            ]

            # 10. Status Kuota Tiap Klien (Tenant Quota Overview)
            from app.services.usage_service import UsageService
            tenant_stmt = select(Tenant).order_by(Tenant.name)
            tenant_rows = (await db.execute(tenant_stmt)).scalars().all()
            tenant_quotas = []
            for t in tenant_rows:
                stats = await UsageService.get_tenant_usage_stats(db=db, tenant_id=t.id)
                stats["name"] = t.name or t.id.replace("_", " ").title()
                tenant_quotas.append(stats)

            return {
                "period_days": days,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "kpis": kpis,
                "layer_breakdown": layer_breakdown,
                "tenant_quotas": tenant_quotas,
                "top_questions": top_questions,
                "unanswered_queries": unanswered_queries,
                "recent_activity": recent_activity,
            }
        except Exception as e:
            logger.error(f"Error computing analytics metrics: {e}")
            return {
                "period_days": days,
                "error": str(e),
                "kpis": cls.calculate_kpis(0, 0, 0, 0.0, 0, 0),
                "layer_breakdown": {},
                "tenant_quotas": [],
                "top_questions": [],
                "unanswered_queries": [],
                "recent_activity": [],
            }

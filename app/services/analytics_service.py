import html
import json
import os
import re
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
    def _get_tenant_detail_info(cls, tenant_id: str) -> Dict[str, Any]:
        """Ekstrak informasi lengkap profil bisnis dan kelengkapan knowledge base tenant."""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base", "l4_tenant", tenant_id))

        info = {
            "whatsapp": "-",
            "address": "-",
            "operating_hours": "-",
            "description": "-",
            "greeting": "-",
            "instagram": "-",
            "has_profil": False,
            "has_layanan": False,
            "has_kebijakan": False,
            "has_faq": False,
        }

        if not os.path.exists(base_dir):
            return info

        info["has_profil"] = os.path.exists(os.path.join(base_dir, "profil.md"))
        info["has_layanan"] = os.path.exists(os.path.join(base_dir, "layanan.md"))
        info["has_kebijakan"] = os.path.exists(os.path.join(base_dir, "kebijakan.md"))
        info["has_faq"] = os.path.exists(os.path.join(base_dir, "faq.md"))

        profil_path = os.path.join(base_dir, "profil.md")
        if os.path.exists(profil_path):
            try:
                with open(profil_path, "r", encoding="utf-8") as f:
                    text = f.read()

                wa_m = re.search(r"-\s+\*\*(?:WhatsApp(?:[^\*]+)?|Kontak|Hotline)\*\*:\s*(.*)", text, re.IGNORECASE)
                if wa_m:
                    info["whatsapp"] = wa_m.group(1).strip()

                addr_m = re.search(r"-\s+\*\*Alamat\*\*:\s*(.*)", text, re.IGNORECASE)
                if addr_m:
                    info["address"] = addr_m.group(1).strip()

                hours_m = re.search(r"-\s+\*\*Jam Operasional\*\*:\s*([\s\S]*?)(?=\n-|\n##|$)", text, re.IGNORECASE)
                if hours_m:
                    clean_h = " ".join([line.strip().lstrip("-* ") for line in hours_m.group(1).splitlines() if line.strip()])
                    info["operating_hours"] = clean_h or "-"

                desc_m = re.search(r"-\s+\*\*Deskripsi\*\*:\s*(.*)", text, re.IGNORECASE)
                if desc_m:
                    info["description"] = desc_m.group(1).strip()

                greet_m = re.search(r"-\s+\*\*Sapaan\*\*:\s*(.*)", text, re.IGNORECASE)
                if greet_m:
                    info["greeting"] = greet_m.group(1).strip()

                ig_m = re.search(r"-\s+\*\*Instagram\*\*:\s*(.*)", text, re.IGNORECASE)
                if ig_m:
                    info["instagram"] = ig_m.group(1).strip()
            except Exception:
                pass

        return info

    @classmethod
    def _render_quota_rows(cls, quotas_list: List[Dict[str, Any]]) -> str:
        if not quotas_list:
            return '<tr><td colspan="7" class="py-8 text-center text-slate-400">Belum ada tenant yang terdaftar di database.</td></tr>'

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
            category = t.get("category", "Bisnis")

            kb_info = t if "whatsapp" in t else cls._get_tenant_detail_info(t_id)

            if tier == "infinity":
                tier_badge = '<span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200">INFINITY</span>'
            elif tier == "nexus":
                tier_badge = '<span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">NEXUS</span>'
            elif tier == "pulse":
                tier_badge = '<span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-sky-50 text-sky-700 border border-sky-200">PULSE</span>'
            else:
                tier_badge = '<span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-300">PIXEL</span>'

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

            modal_data = {
                "tenant_id": t_id,
                "name": name,
                "category": category,
                "tier": tier.upper(),
                "used": f"{used:,}",
                "limit": f"{limit:,}",
                "remaining": f"{remaining:,}",
                "pct": f"{pct}%",
                "bar_width": bar_width,
                "status_cat": status_cat,
                "status_badge": status_badge,
                "cycle_end": cycle_end_str,
                "reset_date": reset_date_str,
                "days_left": days_left,
                "whatsapp": kb_info.get("whatsapp", "-"),
                "address": kb_info.get("address", "-"),
                "operating_hours": kb_info.get("operating_hours", "-"),
                "description": kb_info.get("description", "-"),
                "greeting": kb_info.get("greeting", "-"),
                "has_profil": kb_info.get("has_profil", False),
                "has_layanan": kb_info.get("has_layanan", False),
                "has_kebijakan": kb_info.get("has_kebijakan", False),
                "has_faq": kb_info.get("has_faq", False),
            }
            modal_json = html.escape(json.dumps(modal_data), quote=True)

            rows.append(f"""
            <tr class="tenant-row hover:bg-slate-50 transition border-b border-slate-200/80" data-name="{name.lower()}" data-id="{t_id.lower()}" data-status="{status_cat}">
                <td class="py-3.5 px-5">
                    <button type="button" 
                            onclick="openTenantModal(this)"
                            data-tenant="{modal_json}"
                            title="Klik untuk melihat detail & mengedit konfigurasi AI {name}"
                            class="text-left group/btn focus:outline-none cursor-pointer block">
                        <div class="font-bold text-slate-900 group-hover/btn:text-indigo-600 transition flex items-center gap-1.5">
                            <span class="tenant-name-span underline decoration-slate-300 group-hover/btn:decoration-indigo-500 decoration-1 underline-offset-3">{name}</span>
                            <span class="inline-flex items-center justify-center w-4.5 h-4.5 rounded-md bg-indigo-50 text-indigo-600 opacity-60 group-hover/btn:opacity-100 group-hover/btn:bg-indigo-600 group-hover/btn:text-white transition shadow-2xs text-[10px]" title="Detail & Edit AI Klien">
                                ✏️
                            </span>
                        </div>
                        <div class="text-xs text-slate-500 font-mono mt-0.5 group-hover/btn:text-indigo-500 transition">{t_id}</div>
                    </button>
                </td>
                <td class="tenant-tier-td py-3.5 px-5">{tier_badge}</td>
                <td class="py-3.5 px-5 font-mono text-sm text-slate-800">
                    <span class="tenant-quota-used font-bold text-slate-900">{used:,}</span> <span class="text-slate-500 text-xs font-normal">/ <span class="tenant-quota-limit">{limit:,}</span></span>
                </td>
                <td class="py-3.5 px-5 font-mono text-sm font-semibold text-slate-700">
                    <span class="tenant-remaining">{remaining:,}</span>
                </td>
                <td class="py-3.5 px-5">
                    <div class="flex items-center gap-3">
                        <div class="w-28 bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
                            <div class="tenant-pbar {bar_color} h-2 rounded-full transition-all duration-500" style="width: {bar_width}%;"></div>
                        </div>
                        <span class="tenant-pct-span text-xs {pct_color} font-mono">{pct}%</span>
                    </div>
                </td>
                <td class="py-3.5 px-5">
                    <div class="text-xs font-semibold text-slate-900">s/d {cycle_end_str}</div>
                    <div class="text-[11px] text-indigo-600 font-mono mt-0.5">Reset {reset_date_str} ({days_left} hr lagi)</div>
                </td>
                <td class="tenant-status-td py-3.5 px-5">{status_badge}</td>
            </tr>
            """)
        return "".join(rows)

    @classmethod
    def _render_hourly_chart(cls, traffic_input: Any, days: int = 30) -> str:
        """Menghasilkan Line/Area Chart SVG animasi modern dengan kurva halus, hover tooltip, dan sumbu X dinamis."""
        traffic_points = []
        x_ticks = []
        max_val = 0

        if isinstance(traffic_input, dict):
            traffic_points = traffic_input.get("traffic_points") or traffic_input.get("hourly_traffic") or []
            x_ticks = traffic_input.get("x_ticks") or []
            max_val = traffic_input.get("max_count", 0)
            days = traffic_input.get("period_days", days)
        elif isinstance(traffic_input, list):
            traffic_points = traffic_input
            max_val = max([item.get("count", 0) for item in traffic_points] or [0])

        if not traffic_points:
            traffic_points = [
                {"label": f"{h:02d}:00", "tooltip_title": f"⏰ {h:02d}:00 WIB", "count": 0, "tenants": []}
                for h in range(24)
            ]

        N = len(traffic_points)
        if max_val == 0:
            max_val = 10

        points = []
        for i, item in enumerate(traffic_points):
            count = item.get("count", 0)
            if N > 1:
                x = round(40 + (i * 920 / (N - 1)), 1)
            else:
                x = 500.0
            y = 150 - int(round((count / max_val) * 120))
            points.append((x, y))

        if N == 1:
            line_path = f"M 40,{points[0][1]} L 960,{points[0][1]}"
        else:
            line_path = f"M {points[0][0]},{points[0][1]}"
            for i in range(len(points) - 1):
                p0 = points[i - 1] if i > 0 else points[i]
                p1 = points[i]
                p2 = points[i + 1]
                p3 = points[i + 2] if i + 2 < len(points) else p2
                cp1x = round(p1[0] + (p2[0] - p0[0]) / 6, 1)
                cp1y = round(p1[1] + (p2[1] - p0[1]) / 6, 1)
                cp2x = round(p2[0] - (p3[0] - p1[0]) / 6, 1)
                cp2y = round(p2[1] - (p3[1] - p1[1]) / 6, 1)
                line_path += f" C {cp1x},{cp1y} {cp2x},{cp2y} {p2[0]},{p2[1]}"

        area_path = f"{line_path} L {points[-1][0]},155 L {points[0][0]},155 Z"

        # Generate interactive hover slices
        interactive_slices = []
        for i, item in enumerate(traffic_points):
            count = item.get("count", 0)
            tooltip_title = item.get("tooltip_title") or item.get("hour") or item.get("label") or f"Point {i+1}"
            tenants = item.get("tenants", [])
            x, y = points[i]

            top5 = tenants[:5]
            if top5:
                tenant_rows = []
                for idx, t in enumerate(top5):
                    t_name = t.get("name", "Unknown")
                    t_cnt = t.get("count", 0)
                    tenant_rows.append(f'''
                    <div class="flex items-center justify-between gap-3 text-[11px] py-0.5">
                        <span class="text-slate-200 truncate max-w-[145px]">{idx+1}. {t_name}</span>
                        <span class="font-mono font-bold text-indigo-300 shrink-0">{t_cnt} chat</span>
                    </div>
                    ''')
                tenants_html = "".join(tenant_rows)
            else:
                tenants_html = '<div class="text-[11px] text-slate-400 italic py-0.5">Tidak ada aktivitas chat</div>'

            align_class = "left-0" if i <= max(1, N // 6) else ("right-0" if i >= N - max(2, N // 6) else "left-1/2 -translate-x-1/2")
            y_pct = round((y / 180) * 100, 1)
            peak_badge = ' <span class="text-[9px] bg-indigo-500/30 text-indigo-200 px-1 py-0.2 rounded font-sans">puncak</span>' if (count == max_val and max_val > 0) else ''

            interactive_slices.append(f'''
            <div class="flex-1 h-full flex flex-col items-center justify-end relative group cursor-pointer">
                <!-- Hover Vertical Crosshair Line -->
                <div class="absolute inset-y-0 w-px bg-indigo-500/40 hidden group-hover:block pointer-events-none"></div>

                <!-- Hover Point Dot on the curve with smooth scale animation -->
                <div class="absolute w-3 h-3 rounded-full bg-white border-2 border-indigo-600 shadow-md ring-4 ring-indigo-500/20 hidden group-hover:block pointer-events-none transition-transform group-hover:scale-125 z-20"
                     style="top: calc({y_pct}% - 6px);"></div>

                <!-- Floating Dark Tooltip -->
                <div class="absolute bottom-full {align_class} mb-4 hidden group-hover:flex flex-col w-64 p-3 bg-slate-900/95 backdrop-blur-xs text-white rounded-xl shadow-2xl border border-slate-700/80 z-30 pointer-events-none transition-all">
                    <div class="flex items-center justify-between border-b border-slate-700/80 pb-1.5 mb-1.5">
                        <span class="font-bold text-xs text-white flex items-center gap-1.5 truncate">
                            <span class="w-2 h-2 rounded-full bg-indigo-400 shrink-0"></span>
                            <span class="truncate">{tooltip_title}</span>
                        </span>
                        <span class="font-mono text-xs font-extrabold text-indigo-400 bg-indigo-950/80 px-2 py-0.5 rounded border border-indigo-700/50 shrink-0">{count} chat{peak_badge}</span>
                    </div>
                    <div class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Rincian Top Tenant (Maks 5):</div>
                    <div class="space-y-0.5">
                        {tenants_html}
                    </div>
                </div>
            </div>
            ''')

        slices_html = "".join(interactive_slices)

        # Dynamic X-Axis Ticks Generation
        if x_ticks:
            tick_spans = "".join([f'<span class="truncate px-1">{"Hari Ini" if t.get("label") == "Hari Ini" else t.get("label", "")}</span>' for t in x_ticks])
        elif days == 7:
            tick_spans = "".join([f'<span class="truncate px-1">{p.get("label", "")}</span>' for p in traffic_points])
        elif days == 30:
            tick_spans = "".join([f'<span class="truncate px-1">{traffic_points[idx].get("label", "")}</span>' for idx in [0, 5, 10, 15, 20, 25, len(traffic_points)-1] if idx < len(traffic_points)])
        else:
            tick_spans = """
            <span>00:00</span>
            <span>03:00</span>
            <span>06:00</span>
            <span>09:00</span>
            <span>12:00</span>
            <span>15:00</span>
            <span>18:00</span>
            <span>21:00</span>
            <span>23:00</span>
            """

        svg_html = f'''
        <div class="relative w-full h-36">
            <!-- Background Grid Lines -->
            <div class="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-30 py-2">
                <div class="border-b border-dashed border-slate-400 w-full"></div>
                <div class="border-b border-dashed border-slate-400 w-full"></div>
                <div class="border-b border-slate-300 w-full"></div>
            </div>

            <!-- SVG Smooth Area Curve with Animation -->
            <svg class="absolute inset-0 w-full h-full overflow-visible" viewBox="0 0 1000 180" preserveAspectRatio="none">
                <defs>
                    <linearGradient id="trafficAreaGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#6366f1" stop-opacity="0.32"/>
                        <stop offset="100%" stop-color="#6366f1" stop-opacity="0.0"/>
                    </linearGradient>
                    <style>
                        @keyframes chartDrawLine {{
                            0% {{
                                stroke-dashoffset: 2500;
                            }}
                            100% {{
                                stroke-dashoffset: 0;
                            }}
                        }}
                        @keyframes chartFadeArea {{
                            0% {{
                                opacity: 0;
                                transform: translateY(6px);
                            }}
                            100% {{
                                opacity: 1;
                                transform: translateY(0);
                            }}
                        }}
                        .animate-chart-line {{
                            stroke-dasharray: 2500;
                            stroke-dashoffset: 2500;
                            animation: chartDrawLine 1.1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                        }}
                        .animate-chart-area {{
                            animation: chartFadeArea 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                        }}
                    </style>
                </defs>
                <!-- Area Fill with Fade Animation -->
                <path class="animate-chart-area" d="{area_path}" fill="url(#trafficAreaGradient)"/>
                <!-- Line Stroke with Smooth Draw Animation -->
                <path class="animate-chart-line" d="{line_path}" fill="none" stroke="#6366f1" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>

            <!-- Interactive Hover Slices Overlay -->
            <div class="absolute inset-0 flex items-stretch px-1 z-10">
                {slices_html}
            </div>
        </div>

        <!-- Dynamic X-Axis Labels (Jam untuk Hari Ini, Tanggal/Hari untuk 7 Hari & 30 Hari) -->
        <div class="flex items-center justify-between text-[11px] text-slate-500 font-medium mt-2.5 px-2">
            {tick_spans}
        </div>
        '''
        return svg_html

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

        now = datetime.now()
        _, last_day = calendar.monthrange(now.year, now.month)
        months_id = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        current_cycle_label = f"{months_id[now.month]} {now.year}"
        reset_label = f"1 {months_id[now.month % 12 + 1]} {now.year + (1 if now.month == 12 else 0)}"

        # Compute traffic metrics for initial render
        traffic_trend = data.get('traffic_trend') or {}
        traffic_points = traffic_trend.get("traffic_points") or data.get('hourly_traffic', [])
        traffic_badge = traffic_trend.get("badge_text", "Continuous 24 Jam" if days == 1 else f"Tren {days} Hari (Harian)")
        traffic_subtitle = traffic_trend.get("subtitle", "Kurva Throughput Beban Chat per Jam (00:00 - 23:00 WIB)" if days == 1 else f"Kurva Throughput Beban Chat Harian ({days} Hari Terakhir)")
        peak_unit = traffic_trend.get("peak_unit", "chat/jam" if days == 1 else "chat/hari")
        max_traffic_count = traffic_trend.get("max_count") or max([item.get("count", 0) for item in traffic_points] or [0])

        return f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Engine Intelligence Dashboard — D-Kreasi</title>
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
                    }},
                }}
            }}
        }}
    </script>
    <style>
        html {{ scroll-behavior: smooth; }}
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8fafc; }}
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #f1f5f9; }}
        ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #94a3b8; }}
    </style>
</head>
<body class="text-slate-800 bg-slate-50 min-h-screen flex antialiased selection:bg-indigo-600 selection:text-white">

    <!-- Left Sidebar (Fixed on Desktop) -->
    <aside class="w-64 bg-white border-r border-slate-200/90 flex flex-col justify-between fixed inset-y-0 left-0 z-40 hidden md:flex shadow-sm">
        <div>
            <!-- Brand Logo Header -->
            <div class="h-16 px-6 flex items-center gap-3 border-b border-slate-200 bg-white">
                <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 via-indigo-600 to-sky-500 flex items-center justify-center text-white font-black text-lg shadow-md shadow-indigo-500/20">
                    ⚡
                </div>
                <div>
                    <div class="font-extrabold text-sm tracking-tight text-slate-900 flex items-center gap-1.5">
                        D-KREASI AI
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
                        <span>Overview &amp; KPI</span>
                    </div>
                </a>

                <a href="#layers" data-target="layers" class="nav-link flex items-center justify-between px-3 py-2.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition font-medium">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                        <span>Multi-Tier Routing</span>
                    </div>
                </a>

                <a href="#traffic" data-target="traffic" class="nav-link flex items-center justify-between px-3 py-2.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition font-medium">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                        <span>Peak Hours Traffic</span>
                    </div>
                    <span class="text-[10px] font-bold px-1.5 py-0.2 rounded-full bg-indigo-50 text-indigo-700 font-mono">24H</span>
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
            </nav>
        </div>

        <!-- Sidebar System Status -->
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
                <div class="font-extrabold text-base text-slate-900 tracking-tight">AI Engine Analytics</div>
                <span class="hidden sm:inline-flex px-2 py-0.5 rounded-md text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">Production</span>
            </div>

            <div class="flex items-center gap-2 sm:gap-3">
                <!-- Period Filter Selector -->
                <div class="flex items-center bg-slate-100 border border-slate-200 rounded-lg p-0.5 text-xs font-semibold">
                    <a href="?days=1" class="px-2.5 py-1 rounded-md {'bg-indigo-600 text-white shadow-xs font-bold' if days == 1 else 'text-slate-600 hover:text-slate-900 transition'}">Hari Ini</a>
                    <a href="?days=7" class="px-2.5 py-1 rounded-md {'bg-indigo-600 text-white shadow-xs font-bold' if days == 7 else 'text-slate-600 hover:text-slate-900 transition'}">7 Hari</a>
                    <a href="?days=30" class="px-2.5 py-1 rounded-md {'bg-indigo-600 text-white shadow-xs font-bold' if days == 30 else 'text-slate-600 hover:text-slate-900 transition'}">30 Hari</a>
                </div>

                <button type="button" onclick="openGlobalAiModal()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-xs transition cursor-pointer" title="Buka Pengaturan Prompt & Engine AI">
                    <svg class="w-3.5 h-3.5 text-indigo-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                    <span class="hidden md:inline">Konfigurasi AI Engine</span>
                    <span class="md:hidden">Settings AI</span>
                </button>

                <a href="/api/v1/analytics/overview?days={days}" target="_blank" class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 shadow-xs transition">
                    <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    <span>Raw JSON</span>
                </a>

                <button onclick="window.location.reload()" class="p-1.5 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 text-slate-600 hover:text-slate-900 shadow-xs transition" title="Refresh Data">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                </button>
            </div>
        </header>

        <!-- Main Body Content -->
        <main class="p-6 lg:p-10 space-y-8 flex-1">

            <!-- SECTION 1: EXECUTIVE KPIS -->
            <section id="overview" class="scroll-mt-24 space-y-4 rounded-2xl transition-all duration-300">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-base font-bold text-slate-900 tracking-tight">Key Performance Indicators</h2>
                        <p class="text-xs text-slate-500">Performa penyelesaian pertanyaan dan efisiensi model AI</p>
                    </div>
                    <span class="text-xs text-slate-500 font-mono">Periode {days} Hari Terakhir</span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-slate-300 transition relative overflow-hidden group">
                        <div class="flex items-center justify-between text-slate-500 mb-3">
                            <span class="text-xs font-bold uppercase tracking-wider">Total Obrolan</span>
                            <div class="w-8 h-8 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center font-bold text-sm border border-sky-100">💬</div>
                        </div>
                        <div class="text-3xl font-extrabold text-slate-900 tracking-tight">{kpis.get('total_conversations', 0):,}</div>
                        <div class="mt-2 text-xs text-slate-500 flex items-center gap-1.5">
                            <span class="text-emerald-600 font-bold">{kpis.get('total_messages', 0):,}</span> total pesan dipertukarkan
                        </div>
                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-sky-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition"></div>
                    </div>

                    <div class="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-slate-300 transition relative overflow-hidden group">
                        <div class="flex items-center justify-between text-slate-500 mb-3">
                            <span class="text-xs font-bold uppercase tracking-wider">Resolution Rate</span>
                            <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-sm border border-emerald-100">⚡</div>
                        </div>
                        <div class="text-3xl font-extrabold text-emerald-600 tracking-tight">{kpis.get('resolution_rate_percent', 100.0)}%</div>
                        <div class="mt-2 text-xs text-slate-500">Terjawab mandiri oleh AI tanpa eskalasi</div>
                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 to-teal-500 opacity-0 group-hover:opacity-100 transition"></div>
                    </div>

                    <div class="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-slate-300 transition relative overflow-hidden group">
                        <div class="flex items-center justify-between text-slate-500 mb-3">
                            <span class="text-xs font-bold uppercase tracking-wider">Handoff WhatsApp</span>
                            <div class="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-sm border border-amber-100">📲</div>
                        </div>
                        <div class="text-3xl font-extrabold text-amber-600 tracking-tight">{kpis.get('handoff_rate_percent', 0.0)}%</div>
                        <div class="mt-2 text-xs text-slate-500">Prospek diarahkan ke CS / WhatsApp</div>
                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 to-rose-500 opacity-0 group-hover:opacity-100 transition"></div>
                    </div>

                    <div class="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-slate-300 transition relative overflow-hidden group">
                        <div class="flex items-center justify-between text-slate-500 mb-3">
                            <span class="text-xs font-bold uppercase tracking-wider">Rata-rata Latensi</span>
                            <div class="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-sm border border-indigo-100">⏱️</div>
                        </div>
                        <div class="text-3xl font-extrabold text-indigo-600 tracking-tight font-mono">{kpis.get('avg_latency_ms', 0)} <span class="text-sm font-sans font-normal text-slate-500">ms</span></div>
                        <div class="mt-2 text-xs text-slate-500 font-mono">Konsumsi {kpis.get('total_tokens', 0):,} token LLM</div>
                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition"></div>
                    </div>
                </div>
            </section>

            <!-- SECTION 2: MULTI-TIER LAYER ARCHITECTURE -->
            <section id="layers" class="scroll-mt-24 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4 transition-all duration-300">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-base font-bold text-slate-900 tracking-tight">Distribusi Beban per Layer Layanan</h2>
                        <p class="text-xs text-slate-500 mt-0.5">Pemecahan lalu lintas pertanyaan berdasarkan 4 layer layanan</p>
                    </div>
                    <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">Multi-Tier Architecture</span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="p-4 rounded-xl bg-sky-50/50 border border-sky-100 hover:border-sky-300 transition">
                        <div class="flex items-center justify-between">
                            <div class="text-xs font-bold text-sky-700">L1 · D-Kreasi Concierge</div>
                            <span class="text-[10px] px-1.5 py-0.2 rounded bg-sky-100 text-sky-800 font-mono font-semibold">Router</span>
                        </div>
                        <div class="text-2xl font-extrabold mt-2 text-slate-900 font-mono">{layers.get('l1', {}).get('messages', 0)} <span class="text-xs font-sans text-slate-500 font-normal">pesan</span></div>
                        <div class="text-xs text-slate-500 mt-1 font-mono">{layers.get('l1', {}).get('tokens', 0):,} tokens</div>
                    </div>

                    <div class="p-4 rounded-xl bg-rose-50/50 border border-rose-100 hover:border-rose-300 transition">
                        <div class="flex items-center justify-between">
                            <div class="text-xs font-bold text-rose-700">L2 · D-Karsa Undangan</div>
                            <span class="text-[10px] px-1.5 py-0.2 rounded bg-rose-100 text-rose-800 font-mono font-semibold">Undangan</span>
                        </div>
                        <div class="text-2xl font-extrabold mt-2 text-slate-900 font-mono">{layers.get('l2', {}).get('messages', 0)} <span class="text-xs font-sans text-slate-500 font-normal">pesan</span></div>
                        <div class="text-xs text-slate-500 mt-1 font-mono">{layers.get('l2', {}).get('tokens', 0):,} tokens</div>
                    </div>

                    <div class="p-4 rounded-xl bg-amber-50/50 border border-amber-100 hover:border-amber-300 transition">
                        <div class="flex items-center justify-between">
                            <div class="text-xs font-bold text-amber-700">L3 · Webia Sales AI</div>
                            <span class="text-[10px] px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 font-mono font-semibold">Konsultan</span>
                        </div>
                        <div class="text-2xl font-extrabold mt-2 text-slate-900 font-mono">{layers.get('l3', {}).get('messages', 0)} <span class="text-xs font-sans text-slate-500 font-normal">pesan</span></div>
                        <div class="text-xs text-slate-500 mt-1 font-mono">{layers.get('l3', {}).get('tokens', 0):,} tokens</div>
                    </div>

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

            <!-- SECTION 2B: PEAK HOURS TRAFFIC (SMOOTH AREA/LINE CHART ELEGAN & HOVER TOP 5 TENANT TOOLTIP) -->
            <section id="traffic" class="scroll-mt-24 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                        <div class="flex items-center gap-2">
                            <h2 class="text-base font-bold text-slate-900 tracking-tight">Peak Hours Traffic & Throughput Trend</h2>
                            <span id="trafficBadge" class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono">{traffic_badge}</span>
                        </div>
                        <p class="text-xs text-slate-500 mt-0.5">Tren throughput lalu lintas chat AI. Geser kursor di sepanjang kurva untuk melihat Top 5 tenant aktif.</p>
                    </div>

                    <div class="flex items-center bg-slate-100 border border-slate-200 rounded-lg p-0.5 text-xs font-semibold" id="trafficFilterButtons">
                        <button type="button" onclick="loadTrafficChart(1)" data-days="1" class="traffic-btn px-2.5 py-1 rounded-md {'bg-indigo-600 text-white shadow-xs font-bold' if days == 1 else 'text-slate-600 hover:text-slate-900 transition'}">Hari Ini</button>
                        <button type="button" onclick="loadTrafficChart(7)" data-days="7" class="traffic-btn px-2.5 py-1 rounded-md {'bg-indigo-600 text-white shadow-xs font-bold' if days == 7 else 'text-slate-600 hover:text-slate-900 transition'}">7 Hari</button>
                        <button type="button" onclick="loadTrafficChart(30)" data-days="30" class="traffic-btn px-2.5 py-1 rounded-md {'bg-indigo-600 text-white shadow-xs font-bold' if days == 30 else 'text-slate-600 hover:text-slate-900 transition'}">30 Hari</button>
                    </div>
                </div>

                <div class="bg-slate-50 border border-slate-200/80 rounded-xl p-5">
                    <div class="flex items-center justify-between text-xs text-slate-500 mb-2">
                        <span class="flex items-center gap-1.5 font-medium">
                            <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
                            <span id="trafficSubtitle">{traffic_subtitle}</span>
                        </span>
                        <div class="flex items-center gap-3 text-[11px] font-mono">
                            <span class="flex items-center gap-1"><span class="w-2.5 h-0.5 bg-indigo-600 rounded"></span> Beban Lalu Lintas</span>
                            <span id="trafficPeakLabel" class="text-slate-400">Puncak: {max_traffic_count} {peak_unit}</span>
                        </div>
                    </div>

                    <!-- Clean Smooth Area Curve Line Chart Container with Dynamic X-Axis & Animation -->
                    <div id="hourlyChartWrapper" class="relative pt-2 pb-1 transition-opacity duration-200">
                        {cls._render_hourly_chart(traffic_trend if traffic_trend else traffic_points, days=days)}
                    </div>
                </div>
            </section>

            <!-- SECTION 3: TENANT QUOTA ENFORCEMENT TABLE (CLEAN, TANPA BYPASS) -->
            <section id="tenants" class="scroll-mt-24 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4 transition-all duration-300">
                <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <h2 class="text-base font-bold text-slate-900 tracking-tight">Monitoring Kuota Klien (Tenant Quota Enforcement)</h2>
                            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono">Layer 4</span>
                        </div>
                        <p class="text-xs text-slate-500 mt-0.5">Pemantauan konsumsi pesan bulanan klien Webia terhadap limit paket langganan</p>
                    </div>

                    <!-- Search & Filter Controls -->
                    <div class="flex flex-wrap items-center gap-2">
                        <div class="relative">
                            <input type="text" id="tenantSearchInput" placeholder="Cari nama / ID..." class="w-48 sm:w-56 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:bg-white transition shadow-2xs">
                        </div>

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
                    <span>Menampilkan seluruh tenant aktif di database SQLite sistem.</span>
                    <span class="font-mono text-slate-600">Siklus Kuota: Bulanan · Reset Otomatis: <strong>{reset_label}</strong></span>
                </div>
            </section>

            <!-- SECTION 4: SPLIT 2 COLUMN (TOP QUESTIONS & UNANSWERED QUERIES) -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Left: Top Frequent Questions -->
                <section id="questions" class="scroll-mt-24 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4 transition-all duration-300">
                    <div class="flex items-center justify-between">
                        <span class="text-base font-bold text-slate-900 tracking-tight">Pertanyaan Paling Populer</span>
                        <span class="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono border border-slate-200">Top Inquiries</span>
                    </div>

                    <div class="space-y-2.5">
                        {"".join([f'''
                        <div class="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200/80 hover:bg-slate-100/70 transition group">
                            <div class="flex items-center gap-3 pr-4 truncate">
                                <span class="w-6 h-6 rounded-full bg-white border border-slate-200 text-slate-600 text-[11px] font-mono font-bold flex items-center justify-center shrink-0 shadow-2xs">#{idx+1}</span>
                                <span class="text-sm text-slate-800 truncate group-hover:text-slate-900 transition font-medium">"{q.get('query', '')}"</span>
                            </div>
                            <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 shrink-0 font-mono">
                                {q.get('count', 0)}x
                            </span>
                        </div>
                        ''' for idx, q in enumerate(top_q)]) if top_q else '<p class="text-sm text-slate-400 py-8 text-center">Belum ada rekaman riwayat pertanyaan pengunjung.</p>'}
                    </div>
                </section>

                <!-- Right: Unanswered Queries & Product Insights -->
                <section id="insights" class="scroll-mt-24 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4 transition-all duration-300">
                    <div class="flex items-center justify-between">
                        <span class="text-base font-bold text-slate-900 tracking-tight">Insight Kebutuhan Pelanggan Baru</span>
                        <span class="text-xs font-bold text-rose-700 px-2 py-0.5 rounded bg-rose-50 border border-rose-200 font-mono">Unanswered Queries</span>
                    </div>

                    <div class="space-y-2.5">
                        {"".join([f'''
                        <div class="p-3 rounded-xl bg-rose-50/50 border border-rose-200/80 hover:bg-rose-50 transition">
                            <div class="flex items-center justify-between text-xs text-slate-500 mb-1 font-mono">
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
            <div>AI Engine · D-Kreasi Central Ecosystem · Sinkron otomatis</div>
            <div class="font-mono text-[11px] text-emerald-700 font-semibold hidden sm:flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                Status: Healthy (200 OK)
            </div>
        </footer>

    </div>

    <!-- Modal Detail & Editor AI Klien (Tenant Intelligence & Knowledge Editor) -->
    <div id="tenantDetailModal" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 transition-all duration-200 hidden" role="dialog" aria-modal="true" aria-labelledby="modalTenantName">
        <div class="bg-white rounded-2xl shadow-2xl border border-slate-200/90 max-w-2xl w-full overflow-hidden transform transition-all flex flex-col max-h-[92vh]">
            
            <!-- Modal Header with Tab Switcher -->
            <div class="px-6 py-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white flex items-center justify-between gap-4">
                <div class="flex items-center gap-3 min-w-0">
                    <div class="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-xl shrink-0">
                        🏢
                    </div>
                    <div class="min-w-0">
                        <div class="flex items-center gap-2 flex-wrap">
                            <h3 id="modalTenantName" class="text-base font-bold text-white tracking-tight truncate">Nama Bisnis</h3>
                            <span id="modalTenantCategory" class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white/10 text-indigo-200 border border-white/10 uppercase tracking-wider">Kategori</span>
                        </div>
                        <div id="modalTenantId" class="text-xs text-indigo-300 font-mono mt-0.5 truncate">tenant_id</div>
                    </div>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                    <!-- Mode Switcher Tabs -->
                    <div class="flex items-center bg-white/10 p-1 rounded-xl border border-white/10 text-xs">
                        <button type="button" onclick="switchModalTab('overview')" id="modalTabBtnOverview" class="px-3 py-1 rounded-lg font-bold bg-white text-slate-900 shadow-xs transition cursor-pointer">
                            👁️ Ringkasan
                        </button>
                        <button type="button" onclick="switchModalTab('edit')" id="modalTabBtnEdit" class="px-3 py-1 rounded-lg font-medium text-slate-200 hover:text-white transition cursor-pointer">
                            ✏️ Edit AI
                        </button>
                    </div>

                    <button type="button" onclick="closeTenantModal()" class="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white flex items-center justify-center transition cursor-pointer text-lg font-bold" aria-label="Tutup Modal">
                        ✕
                    </button>
                </div>
            </div>

            <!-- TAB 1: OVERVIEW VIEW -->
            <div id="modalViewOverview" class="p-6 overflow-y-auto space-y-5 text-sm text-slate-700 bg-slate-50/50">
                <!-- Status & Paket AI Highlights -->
                <div class="bg-white p-4 rounded-xl border border-slate-200/90 shadow-2xs space-y-3">
                    <div class="flex items-center justify-between pb-2 border-b border-slate-100">
                        <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Status Kuota &amp; Langganan</span>
                        <div id="modalStatusBadge"></div>
                    </div>
                    
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80">
                            <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Paket Tier</div>
                            <div id="modalTierBadge" class="mt-1 font-bold text-slate-900">PIXEL</div>
                        </div>
                        <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80">
                            <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Limit Kuota</div>
                            <div id="modalQuotaLimit" class="mt-1 font-bold text-slate-900 font-mono">500</div>
                        </div>
                        <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80">
                            <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Terpakai</div>
                            <div id="modalQuotaUsed" class="mt-1 font-bold text-slate-900 font-mono">0</div>
                        </div>
                        <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80">
                            <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Sisa Pesan</div>
                            <div id="modalQuotaRemaining" class="mt-1 font-bold text-emerald-700 font-mono">500</div>
                        </div>
                    </div>

                    <!-- Progress bar -->
                    <div class="pt-1">
                        <div class="flex justify-between text-xs mb-1 font-semibold">
                            <span class="text-slate-600">Konsumsi Bulan Berjalan</span>
                            <span id="modalPercentage" class="font-mono text-slate-900">0%</span>
                        </div>
                        <div class="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden border border-slate-200">
                            <div id="modalProgressBar" class="h-2.5 rounded-full transition-all duration-300 bg-indigo-600" style="width: 0%;"></div>
                        </div>
                        <div class="flex items-center justify-between text-[11px] text-slate-500 mt-1.5 font-mono">
                            <span>Siklus s/d: <strong id="modalCycleEnd" class="text-slate-700">-</strong></span>
                            <span class="text-indigo-600">Reset: <strong id="modalResetDate" class="text-indigo-700">-</strong></span>
                        </div>
                    </div>
                </div>

                <!-- Informasi Operasional Bisnis -->
                <div class="bg-white p-4 rounded-xl border border-slate-200/90 shadow-2xs space-y-3">
                    <div class="text-xs font-bold uppercase tracking-wider text-slate-400 pb-2 border-b border-slate-100 flex items-center justify-between">
                        <span>Informasi Profil Bisnis Klien</span>
                        <span class="text-[11px] text-slate-500 font-normal">Tersinkronisasi otomatis</span>
                    </div>

                    <div class="space-y-2.5 text-xs">
                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 py-1 border-b border-slate-50">
                            <span class="font-semibold text-slate-500">Nomor WhatsApp CS:</span>
                            <div class="sm:col-span-2 font-mono font-bold text-slate-900 flex items-center gap-2">
                                <span id="modalWhatsApp">-</span>
                                <a id="modalWhatsAppLink" href="#" target="_blank" rel="noopener" class="text-emerald-600 hover:text-emerald-700 underline text-[11px] font-sans font-semibold">Chat WA ↗</a>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 py-1 border-b border-slate-50">
                            <span class="font-semibold text-slate-500">Alamat / Lokasi:</span>
                            <span id="modalAddress" class="sm:col-span-2 text-slate-800 font-medium">-</span>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 py-1 border-b border-slate-50">
                            <span class="font-semibold text-slate-500">Jam Operasional:</span>
                            <span id="modalOperatingHours" class="sm:col-span-2 text-slate-800 font-medium">-</span>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 py-1">
                            <span class="font-semibold text-slate-500">Sapaan Asisten AI:</span>
                            <div id="modalGreeting" class="sm:col-span-2 p-2 rounded bg-slate-50 border border-slate-200 text-slate-700 italic font-normal text-[11px]">
                                -
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Status Berkas Knowledge Base AI (L4) -->
                <div class="bg-white p-4 rounded-xl border border-slate-200/90 shadow-2xs space-y-2.5">
                    <div class="text-xs font-bold uppercase tracking-wider text-slate-400 pb-1.5 border-b border-slate-100 flex items-center justify-between">
                        <span>Kelengkapan Pengetahuan AI (Layer 4)</span>
                        <button type="button" onclick="switchModalTab('edit'); switchEditSubTab('kb');" class="text-[11px] font-bold text-indigo-600 hover:text-indigo-800 transition cursor-pointer">
                            Buka Editor Dokumen ↗
                        </button>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-[11px]">
                        <div id="kbBadgeProfil" class="p-2 rounded-lg border flex items-center justify-between">
                            <span class="font-mono">profil.md</span>
                            <span>✓</span>
                        </div>
                        <div id="kbBadgeLayanan" class="p-2 rounded-lg border flex items-center justify-between">
                            <span class="font-mono">layanan.md</span>
                            <span>✓</span>
                        </div>
                        <div id="kbBadgeKebijakan" class="p-2 rounded-lg border flex items-center justify-between">
                            <span class="font-mono">kebijakan.md</span>
                            <span>✓</span>
                        </div>
                        <div id="kbBadgeFaq" class="p-2 rounded-lg border flex items-center justify-between">
                            <span class="font-mono">faq.md</span>
                            <span>✓</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: EDIT AI VIEW (Comprehensive AI & Knowledge Base Editor) -->
            <div id="modalViewEdit" class="p-6 overflow-y-auto space-y-4 text-sm text-slate-700 bg-slate-50/50 hidden">
                <!-- Sub-Tabs inside Edit Mode -->
                <div class="flex items-center gap-1.5 p-1 bg-slate-200/70 rounded-xl border border-slate-200 text-xs font-semibold">
                    <button type="button" onclick="switchEditSubTab('profile')" id="subTabBtnProfile" class="flex-1 py-1.5 rounded-lg bg-white text-indigo-700 font-bold shadow-xs transition cursor-pointer">
                        🏢 Profil &amp; Sapaan AI
                    </button>
                    <button type="button" onclick="switchEditSubTab('quota')" id="subTabBtnQuota" class="flex-1 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition cursor-pointer font-medium">
                        📊 Paket &amp; Kuota AI
                    </button>
                    <button type="button" onclick="switchEditSubTab('kb')" id="subTabBtnKb" class="flex-1 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition cursor-pointer font-medium">
                        📚 Knowledge Base L4 (4 Berkas)
                    </button>
                </div>

                <!-- Sub-Pane 1: Profil & Sapaan AI -->
                <div id="subPaneProfile" class="space-y-3.5 bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Nama Resmi Bisnis</label>
                            <input type="text" id="editTenantName" class="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" />
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Kategori Industri</label>
                            <input type="text" id="editTenantCategory" class="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Nomor WhatsApp CS (Handoff)</label>
                            <input type="text" id="editTenantWhatsApp" placeholder="contoh: 081234567890" class="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" />
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Jam Operasional</label>
                            <input type="text" id="editTenantHours" placeholder="contoh: Senin - Sabtu 08.00 - 17.00 WIB" class="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" />
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Alamat / Lokasi Fisik Bisnis</label>
                        <textarea id="editTenantAddress" rows="2" class="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"></textarea>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1 flex items-center justify-between">
                            <span>Sapaan Pembuka AI (Greeting Message)</span>
                            <span class="text-[10px] text-slate-400 font-normal">Diucapkan saat pengunjung membuka widget chat</span>
                        </label>
                        <textarea id="editTenantGreeting" rows="2" class="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none italic"></textarea>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Deskripsi &amp; Cakupan Layanan Bisnis</label>
                        <textarea id="editTenantDescription" rows="2" class="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"></textarea>
                    </div>
                </div>

                <!-- Sub-Pane 2: Paket & Kuota AI -->
                <div id="subPaneQuota" class="space-y-4 bg-white p-4 rounded-xl border border-slate-200 shadow-2xs hidden">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Paket Tier AI</label>
                            <select id="editTenantTier" onchange="onTierChange(this.value)" class="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none bg-white">
                                <option value="pixel">Pixel (500 pesan / bulan)</option>
                                <option value="pulse">Pulse / Vector (1.000 pesan / bulan)</option>
                                <option value="nexus">Nexus / Artisan (2.500 pesan / bulan)</option>
                                <option value="infinity">Infinity (5.000 pesan / bulan)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Batas Kuota Pesan per Bulan</label>
                            <input type="number" id="editTenantQuota" min="50" step="50" class="w-full text-xs font-mono font-bold px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" />
                        </div>
                    </div>

                    <!-- Reset Kuota Checkbox -->
                    <label class="flex items-start gap-3 p-3.5 rounded-xl bg-amber-50 border border-amber-200 cursor-pointer">
                        <input type="checkbox" id="editTenantResetUsage" class="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer" />
                        <div>
                            <div class="text-xs font-bold text-amber-900">Reset Total Pesan Terpakai Bulan Ini ke 0</div>
                            <div class="text-[11px] text-amber-700 mt-0.5">Centang opsi ini jika Anda ingin mengembalikan total kuota yang telah terkonsumsi menjadi 0 pesan (membuka blokir secara instan jika kuota habis).</div>
                        </div>
                    </label>
                </div>

                <!-- Sub-Pane 3: Knowledge Base L4 (Markdown Editor) -->
                <div id="subPaneKb" class="space-y-3 bg-white p-4 rounded-xl border border-slate-200 shadow-2xs hidden">
                    <div class="flex items-center justify-between pb-2 border-b border-slate-100 flex-wrap gap-2">
                        <div class="flex items-center gap-1.5 bg-slate-900 p-1 rounded-lg">
                            <button type="button" onclick="switchKbFile('profil')" id="kbTabBtn_profil" class="px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-indigo-600 text-white shadow-xs transition cursor-pointer">
                                profil.md
                            </button>
                            <button type="button" onclick="switchKbFile('layanan')" id="kbTabBtn_layanan" class="px-2.5 py-1 rounded-md text-xs font-mono text-slate-300 hover:text-white transition cursor-pointer">
                                layanan.md
                            </button>
                            <button type="button" onclick="switchKbFile('kebijakan')" id="kbTabBtn_kebijakan" class="px-2.5 py-1 rounded-md text-xs font-mono text-slate-300 hover:text-white transition cursor-pointer">
                                kebijakan.md
                            </button>
                            <button type="button" onclick="switchKbFile('faq')" id="kbTabBtn_faq" class="px-2.5 py-1 rounded-md text-xs font-mono text-slate-300 hover:text-white transition cursor-pointer">
                                faq.md
                            </button>
                        </div>

                        <div class="text-[11px] text-slate-500 font-mono flex items-center gap-1.5">
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            <span id="activeKbFileName">profil.md</span>
                        </div>
                    </div>

                    <div class="relative">
                        <textarea id="editKbTextarea" rows="11" class="w-full font-mono text-xs p-3 rounded-xl bg-slate-950 text-slate-100 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none leading-relaxed" placeholder="Memuat isi dokumen markdown..."></textarea>
                    </div>

                    <div class="flex items-center justify-between text-[11px] text-slate-500">
                        <span>ℹ Markdown ini di-chunk otomatis dan diindeks ke FAISS saat disimpan.</span>
                        <button type="button" onclick="reloadActiveKbFile()" class="text-indigo-600 hover:text-indigo-800 font-semibold cursor-pointer">
                            Muat Ulang Berkas ↺
                        </button>
                    </div>
                </div>
            </div>

            <!-- Modal Footers -->
            <!-- Overview Footer -->
            <div id="modalFooterOverview" class="px-6 py-3.5 bg-white border-t border-slate-200 flex items-center justify-between gap-3">
                <span class="text-xs text-slate-400 font-mono">AI Engine · Tenant Intelligence</span>
                <div class="flex items-center gap-2">
                    <button type="button" onclick="switchModalTab('edit')" class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-xs transition flex items-center gap-1.5 cursor-pointer">
                        <span>✏️ Edit AI Klien Ini</span>
                    </button>
                    <a id="modalBtnWhatsApp" href="#" target="_blank" rel="noopener" class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-xs transition inline-flex items-center gap-1.5 cursor-pointer">
                        <span>💬 WhatsApp</span>
                    </a>
                    <button type="button" onclick="closeTenantModal()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition cursor-pointer">
                        Tutup
                    </button>
                </div>
            </div>

            <!-- Edit Footer -->
            <div id="modalFooterEdit" class="px-6 py-3.5 bg-white border-t border-slate-200 flex items-center justify-between gap-3 hidden">
                <button type="button" onclick="switchModalTab('overview')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition cursor-pointer">
                    Batal
                </button>
                <div class="flex items-center gap-2">
                    <button type="button" id="btnSaveAiConfig" onclick="saveTenantAiChanges()" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-xs transition flex items-center gap-2 cursor-pointer">
                        <span>💾 Simpan Perubahan AI &amp; Rebuild FAISS</span>
                    </button>
                </div>
            </div>

        </div>
    </div>

    <!-- Modal Konfigurasi Global AI Engine (Prompts & Parameter) -->
    <div id="globalAiModal" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 transition-all duration-200 hidden" role="dialog" aria-modal="true" aria-labelledby="globalModalTitle">
        <div class="bg-white rounded-2xl shadow-2xl border border-slate-200/90 max-w-3xl w-full overflow-hidden transform transition-all flex flex-col max-h-[92vh]">
            
            <!-- Global Modal Header -->
            <div class="px-6 py-4 bg-gradient-to-r from-indigo-900 via-slate-900 to-indigo-950 text-white flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center text-xl shrink-0">
                        ⚙️
                    </div>
                    <div>
                        <h3 id="globalModalTitle" class="text-base font-bold text-white tracking-tight">Konfigurasi Global AI Engine</h3>
                        <div class="text-xs text-indigo-200 font-mono mt-0.5">Prompt Multi-Layer, Parameter Gateway LLM &amp; Cache</div>
                    </div>
                </div>
                <button type="button" onclick="closeGlobalAiModal()" class="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white flex items-center justify-center transition cursor-pointer text-lg font-bold" aria-label="Tutup">
                    ✕
                </button>
            </div>

            <!-- Global Modal Body (Tabs & Panes) -->
            <div class="p-6 overflow-y-auto space-y-4 text-sm text-slate-700 bg-slate-50/50">
                <!-- Sub-Tabs -->
                <div class="flex items-center gap-1.5 p-1 bg-slate-200/70 rounded-xl border border-slate-200 text-xs font-semibold">
                    <button type="button" onclick="switchGlobalTab('prompts')" id="globalTabBtn_prompts" class="flex-1 py-1.5 rounded-lg bg-white text-indigo-700 font-bold shadow-xs transition cursor-pointer">
                        📝 System Prompts (L1, L2, L3, L4)
                    </button>
                    <button type="button" onclick="switchGlobalTab('params')" id="globalTabBtn_params" class="flex-1 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition cursor-pointer font-medium">
                        🎛 Parameter LLM Gateway
                    </button>
                </div>

                <!-- Pane 1: Layer Prompts -->
                <div id="globalPanePrompts" class="space-y-4">
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-2">
                        <div class="flex items-center justify-between">
                            <label class="text-xs font-bold text-slate-900">Layer 1 · D-Kreasi Concierge Prompt</label>
                            <span class="text-[11px] text-indigo-600 font-mono">app/layers/l1_dkreasi</span>
                        </div>
                        <textarea id="globalL1Prompt" rows="4" class="w-full font-mono text-xs p-3 rounded-lg bg-slate-950 text-slate-100 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none leading-relaxed"></textarea>
                    </div>

                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-2">
                        <div class="flex items-center justify-between">
                            <label class="text-xs font-bold text-slate-900">Layer 2 · D-Karsa Portfolio AI Prompt</label>
                            <span class="text-[11px] text-indigo-600 font-mono">app/layers/l2_dkarsa</span>
                        </div>
                        <textarea id="globalL2Prompt" rows="4" class="w-full font-mono text-xs p-3 rounded-lg bg-slate-950 text-slate-100 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none leading-relaxed"></textarea>
                    </div>

                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-2">
                        <div class="flex items-center justify-between">
                            <label class="text-xs font-bold text-slate-900">Layer 3 · Webia Sales AI Prompt</label>
                            <span class="text-[11px] text-indigo-600 font-mono">app/layers/l3_webia</span>
                        </div>
                        <textarea id="globalL3Prompt" rows="4" class="w-full font-mono text-xs p-3 rounded-lg bg-slate-950 text-slate-100 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none leading-relaxed"></textarea>
                    </div>

                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-2">
                        <div class="flex items-center justify-between">
                            <label class="text-xs font-bold text-slate-900">Layer 4 · Base Business Prompt</label>
                            <span class="text-[11px] text-indigo-600 font-mono">app/layers/l4_business</span>
                        </div>
                        <textarea id="globalL4Prompt" rows="4" class="w-full font-mono text-xs p-3 rounded-lg bg-slate-950 text-slate-100 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none leading-relaxed"></textarea>
                    </div>
                </div>

                <!-- Pane 2: LLM Parameters -->
                <div id="globalPaneParams" class="space-y-4 hidden">
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-3">
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Model Name (Gateway)</label>
                                <input type="text" id="globalLlmModel" class="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" />
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Temperature (0.0 - 1.0)</label>
                                <input type="number" step="0.1" min="0" max="1" id="globalLlmTemp" class="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" />
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Max Tokens</label>
                                <input type="number" id="globalLlmTokens" class="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" />
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Customer Support WhatsApp Handoff</label>
                                <input type="text" id="globalCsWa" class="w-full text-xs font-mono px-3 py-2 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" />
                            </div>
                        </div>
                    </div>

                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-2">
                        <div class="text-xs font-bold text-slate-900">Aksi Pemeliharaan Cache</div>
                        <div class="text-xs text-slate-500">Kosongkan semantic cache agar AI langsung merefleksikan perubahan prompt terbaru.</div>
                        <button type="button" onclick="clearGlobalCache()" class="mt-2 px-3 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-bold transition cursor-pointer">
                            Bersihkan Semantic Cache Sekarang 🗑️
                        </button>
                    </div>
                </div>
            </div>

            <!-- Global Modal Footer -->
            <div class="px-6 py-3.5 bg-white border-t border-slate-200 flex items-center justify-between gap-3">
                <button type="button" onclick="closeGlobalAiModal()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition cursor-pointer">
                    Tutup
                </button>
                <button type="button" id="btnSaveGlobalAi" onclick="saveGlobalAiSettings()" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-xs transition flex items-center gap-2 cursor-pointer">
                    <span>💾 Simpan Pengaturan Global</span>
                </button>
            </div>

        </div>
    </div>

    <!-- Client-side Interactive Logic -->
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

                    targetElement.classList.add('ring-2', 'ring-indigo-500/40');
                    setTimeout(() => {{
                        targetElement.classList.remove('ring-2', 'ring-indigo-500/40');
                    }}, 1200);
                }}
            }});
        }});

        // 2. Auto sync sidebar active item on scroll
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

        // 3. Search & Status Filter for Tenant Quota Table
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

        // 4. Asynchronous Filter for Peak Hours & Traffic Trend
        async function loadTrafficChart(days) {{
            const chartWrapper = document.getElementById('hourlyChartWrapper');
            const peakLabel = document.getElementById('trafficPeakLabel');
            const badge = document.getElementById('trafficBadge');
            const subtitle = document.getElementById('trafficSubtitle');
            const buttons = document.querySelectorAll('.traffic-btn');

            buttons.forEach(btn => {{
                const btnDays = parseInt(btn.getAttribute('data-days'));
                if (btnDays === days) {{
                    btn.className = 'traffic-btn px-2.5 py-1 rounded-md bg-indigo-600 text-white shadow-xs font-bold transition';
                }} else {{
                    btn.className = 'traffic-btn px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 transition font-medium';
                }}
            }});

            if (!chartWrapper) return;

            chartWrapper.classList.add('opacity-40', 'pointer-events-none');

            try {{
                const basePath = window.location.pathname.includes('/api/v1/analytics') ? '/api/v1/analytics' : '/analytics';
                const response = await fetch(basePath + '/hourly-traffic?days=' + days);
                if (!response.ok) {{
                    throw new Error('HTTP ' + response.status);
                }}
                const data = await response.json();

                if (data.chart_svg) {{
                    chartWrapper.innerHTML = data.chart_svg;
                }}
                if (peakLabel && data.peak_label) {{
                    peakLabel.textContent = data.peak_label;
                }}
                if (badge && data.badge_text) {{
                    badge.textContent = data.badge_text;
                }}
                if (subtitle && data.subtitle) {{
                    subtitle.textContent = data.subtitle;
                }}
            }} catch (error) {{
                console.error('Gagal memperbarui grafik traffic:', error);
            }} finally {{
                chartWrapper.classList.remove('opacity-40', 'pointer-events-none');
            }}
        }}

        // 5. Tenant Detail & Edit Modal Logic
        const tenantModal = document.getElementById('tenantDetailModal');
        let currentTenantData = null;
        let currentKbFiles = {{ profil: '', layanan: '', kebijakan: '', faq: '' }};
        let activeKbFileKey = 'profil';
        let currentActiveTenantButton = null;

        function openTenantModal(button) {{
            if (!tenantModal) return;
            const rawData = button.getAttribute('data-tenant');
            if (!rawData) return;

            try {{
                currentActiveTenantButton = button;
                const data = JSON.parse(rawData);
                currentTenantData = data;

                // 1. Populate Overview View
                document.getElementById('modalTenantName').textContent = data.name || 'Detail Klien';
                document.getElementById('modalTenantId').textContent = data.tenant_id || '-';
                document.getElementById('modalTenantCategory').textContent = data.category || 'Bisnis';
                
                document.getElementById('modalTierBadge').textContent = data.tier || 'PIXEL';
                document.getElementById('modalQuotaLimit').textContent = data.limit || '500';
                document.getElementById('modalQuotaUsed').textContent = data.used || '0';
                document.getElementById('modalQuotaRemaining').textContent = data.remaining || '0';
                document.getElementById('modalPercentage').textContent = data.pct || '0%';
                
                const pBar = document.getElementById('modalProgressBar');
                if (pBar) {{
                    pBar.style.width = (data.bar_width || 0) + '%';
                    pBar.className = 'h-2.5 rounded-full transition-all duration-300 ' + (data.status_cat === 'blocked' ? 'bg-rose-500' : (data.status_cat === 'warning' ? 'bg-amber-500' : 'bg-emerald-500'));
                }}
                
                const statusBadgeContainer = document.getElementById('modalStatusBadge');
                if (statusBadgeContainer) {{
                    statusBadgeContainer.innerHTML = data.status_badge || '';
                }}

                document.getElementById('modalCycleEnd').textContent = data.cycle_end || '-';
                document.getElementById('modalResetDate').textContent = (data.reset_date || '-') + ' (' + (data.days_left || 0) + ' hari lagi)';

                document.getElementById('modalWhatsApp').textContent = data.whatsapp || '-';
                document.getElementById('modalAddress').textContent = data.address || '-';
                document.getElementById('modalOperatingHours').textContent = data.operating_hours || '-';
                document.getElementById('modalGreeting').textContent = data.greeting || '-';

                const cleanWa = (data.whatsapp || '').replace(/[^0-9]/g, '');
                const waFormatted = cleanWa.startsWith('0') ? '62' + cleanWa.substring(1) : cleanWa;
                const waUrl = waFormatted ? ('https://wa.me/' + waFormatted + '?text=' + encodeURIComponent('Halo ' + (data.name || '') + ', kami dari Tim D-Kreasi / Webia ingin mengonfirmasikan terkait performa AI Assistant website Anda.')) : '#';

                const waLink = document.getElementById('modalWhatsAppLink');
                const btnWa = document.getElementById('modalBtnWhatsApp');
                if (waLink) {{
                    waLink.href = waUrl;
                    waLink.style.display = waFormatted ? 'inline-block' : 'none';
                }}
                if (btnWa) {{
                    btnWa.href = waUrl;
                    btnWa.style.display = waFormatted ? 'inline-flex' : 'none';
                }}

                function updateKbBadge(id, exists) {{
                    const el = document.getElementById(id);
                    if (!el) return;
                    if (exists) {{
                        el.className = 'p-2 rounded-lg border border-emerald-200 bg-emerald-50 text-emerald-800 flex items-center justify-between font-medium';
                        el.lastElementChild.textContent = '✓';
                    }} else {{
                        el.className = 'p-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-400 flex items-center justify-between';
                        el.lastElementChild.textContent = '–';
                    }}
                }}
                updateKbBadge('kbBadgeProfil', data.has_profil);
                updateKbBadge('kbBadgeLayanan', data.has_layanan);
                updateKbBadge('kbBadgeKebijakan', data.has_kebijakan);
                updateKbBadge('kbBadgeFaq', data.has_faq);

                // 2. Populate Edit Form Fields
                document.getElementById('editTenantName').value = data.name || '';
                document.getElementById('editTenantCategory').value = data.category || '';
                document.getElementById('editTenantWhatsApp').value = data.whatsapp === '-' ? '' : (data.whatsapp || '');
                document.getElementById('editTenantHours').value = data.operating_hours === '-' ? '' : (data.operating_hours || '');
                document.getElementById('editTenantAddress').value = data.address === '-' ? '' : (data.address || '');
                document.getElementById('editTenantGreeting').value = data.greeting === '-' ? '' : (data.greeting || '');
                document.getElementById('editTenantDescription').value = data.description === '-' ? '' : (data.description || '');
                
                const tierSel = document.getElementById('editTenantTier');
                if (tierSel) {{
                    tierSel.value = (data.tier || 'pixel').toLowerCase();
                }}
                const numQuota = parseInt((data.limit || '500').replace(/[^0-9]/g, '')) || 500;
                document.getElementById('editTenantQuota').value = numQuota;
                document.getElementById('editTenantResetUsage').checked = false;

                // Reset views to overview tab
                switchModalTab('overview');

                // 3. Fetch Knowledge Base files in background
                fetchTenantKnowledgeFiles(data.tenant_id);

                tenantModal.classList.remove('hidden');
                document.body.style.overflow = 'hidden';
            }} catch (err) {{
                console.error('Gagal membuka modal tenant:', err);
            }}
        }}

        function closeTenantModal() {{
            if (!tenantModal) return;
            tenantModal.classList.add('hidden');
            document.body.style.overflow = '';
        }}

        function switchModalTab(tab) {{
            const viewOverview = document.getElementById('modalViewOverview');
            const viewEdit = document.getElementById('modalViewEdit');
            const btnOverview = document.getElementById('modalTabBtnOverview');
            const btnEdit = document.getElementById('modalTabBtnEdit');
            const footerOverview = document.getElementById('modalFooterOverview');
            const footerEdit = document.getElementById('modalFooterEdit');

            if (tab === 'edit') {{
                viewOverview.classList.add('hidden');
                viewEdit.classList.remove('hidden');
                footerOverview.classList.add('hidden');
                footerEdit.classList.remove('hidden');
                btnOverview.className = 'px-3 py-1 rounded-lg font-medium text-slate-200 hover:text-white transition cursor-pointer';
                btnEdit.className = 'px-3 py-1 rounded-lg font-bold bg-white text-slate-900 shadow-xs transition cursor-pointer';
                switchEditSubTab('profile');
            }} else {{
                viewOverview.classList.remove('hidden');
                viewEdit.classList.add('hidden');
                footerOverview.classList.remove('hidden');
                footerEdit.classList.add('hidden');
                btnOverview.className = 'px-3 py-1 rounded-lg font-bold bg-white text-slate-900 shadow-xs transition cursor-pointer';
                btnEdit.className = 'px-3 py-1 rounded-lg font-medium text-slate-200 hover:text-white transition cursor-pointer';
            }}
        }}

        function switchEditSubTab(subTab) {{
            const panes = {{
                profile: document.getElementById('subPaneProfile'),
                quota: document.getElementById('subPaneQuota'),
                kb: document.getElementById('subPaneKb')
            }};
            const btns = {{
                profile: document.getElementById('subTabBtnProfile'),
                quota: document.getElementById('subTabBtnQuota'),
                kb: document.getElementById('subTabBtnKb')
            }};

            for (const key in panes) {{
                if (key === subTab) {{
                    if (panes[key]) panes[key].classList.remove('hidden');
                    if (btns[key]) btns[key].className = 'flex-1 py-1.5 rounded-lg bg-white text-indigo-700 font-bold shadow-xs transition cursor-pointer';
                }} else {{
                    if (panes[key]) panes[key].classList.add('hidden');
                    if (btns[key]) btns[key].className = 'flex-1 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition cursor-pointer font-medium';
                }}
            }}
        }}

        function onTierChange(val) {{
            const quotaMap = {{ pixel: 500, pulse: 1000, nexus: 2500, infinity: 5000 }};
            const input = document.getElementById('editTenantQuota');
            if (input && quotaMap[val]) {{
                input.value = quotaMap[val];
            }}
        }}

        async function fetchTenantKnowledgeFiles(tenantId) {{
            try {{
                const res = await fetch('/api/v1/tenants/' + tenantId + '/knowledge');
                if (!res.ok) return;
                const data = await res.json();
                currentKbFiles = {{
                    profil: data.profil || '',
                    layanan: data.layanan || '',
                    kebijakan: data.kebijakan || '',
                    faq: data.faq || '',
                }};
                switchKbFile(activeKbFileKey);
            }} catch (err) {{
                console.warn('Gagal mengambil berkas knowledge base:', err);
            }}
        }}

        function switchKbFile(fileKey) {{
            const txt = document.getElementById('editKbTextarea');
            if (txt && activeKbFileKey && currentKbFiles[activeKbFileKey] !== undefined) {{
                currentKbFiles[activeKbFileKey] = txt.value;
            }}

            activeKbFileKey = fileKey;
            ['profil', 'layanan', 'kebijakan', 'faq'].forEach(k => {{
                const b = document.getElementById('kbTabBtn_' + k);
                if (b) {{
                    if (k === fileKey) {{
                        b.className = 'px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-indigo-600 text-white shadow-xs transition cursor-pointer';
                    }} else {{
                        b.className = 'px-2.5 py-1 rounded-md text-xs font-mono text-slate-300 hover:text-white transition cursor-pointer';
                    }}
                }}
            }});

            const lbl = document.getElementById('activeKbFileName');
            if (lbl && currentTenantData) {{
                lbl.textContent = fileKey + '.md (' + currentTenantData.tenant_id + ')';
            }}

            if (txt) {{
                txt.value = currentKbFiles[fileKey] || '';
            }}
        }}

        function reloadActiveKbFile() {{
            if (!currentTenantData || !currentTenantData.tenant_id) return;
            fetchTenantKnowledgeFiles(currentTenantData.tenant_id);
            showToast('Memuat ulang berkas dari server...');
        }}

        async function saveTenantAiChanges() {{
            if (!currentTenantData || !currentTenantData.tenant_id) return;

            const txt = document.getElementById('editKbTextarea');
            if (txt && activeKbFileKey) {{
                currentKbFiles[activeKbFileKey] = txt.value;
            }}

            const btnSave = document.getElementById('btnSaveAiConfig');
            if (btnSave) {{
                btnSave.disabled = true;
                btnSave.innerHTML = '<svg class="w-4 h-4 animate-spin text-white inline-block mr-1" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg> <span>Menyimpan &amp; Rebuild FAISS...</span>';
            }}

            const payload = {{
                name: document.getElementById('editTenantName').value.trim(),
                category: document.getElementById('editTenantCategory').value.trim(),
                package_tier: document.getElementById('editTenantTier').value,
                monthly_quota: parseInt(document.getElementById('editTenantQuota').value) || 500,
                reset_usage: document.getElementById('editTenantResetUsage').checked,
                whatsapp: document.getElementById('editTenantWhatsApp').value.trim(),
                operating_hours: document.getElementById('editTenantHours').value.trim(),
                address: document.getElementById('editTenantAddress').value.trim(),
                greeting: document.getElementById('editTenantGreeting').value.trim(),
                description: document.getElementById('editTenantDescription').value.trim(),
                profil_md: currentKbFiles.profil,
                layanan_md: currentKbFiles.layanan,
                kebijakan_md: currentKbFiles.kebijakan,
                faq_md: currentKbFiles.faq,
            }};

            try {{
                const res = await fetch('/api/v1/tenants/' + currentTenantData.tenant_id + '/update-ai', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload),
                }});

                const resData = await res.json();
                if (!res.ok) {{
                    throw new Error(resData.detail || 'Gagal menyimpan perubahan.');
                }}

                // Update currentTenantData
                currentTenantData.name = resData.name;
                currentTenantData.category = resData.category;
                currentTenantData.tier = (resData.package_tier || 'PIXEL').toUpperCase();
                currentTenantData.limit = (resData.monthly_quota || 500).toLocaleString();

                if (payload.reset_usage) {{
                    currentTenantData.used = '0';
                    currentTenantData.remaining = currentTenantData.limit;
                    currentTenantData.pct = '0.0%';
                    currentTenantData.bar_width = 0;
                    currentTenantData.status_cat = 'normal';
                    currentTenantData.status_badge = '<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 inline-flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Aman</span>';
                }} else {{
                    const used = resData.stats.usage || 0;
                    const limit = resData.monthly_quota || 500;
                    const pct = limit > 0 ? (used / limit * 100) : 0;
                    currentTenantData.used = used.toLocaleString();
                    currentTenantData.remaining = Math.max(0, limit - used).toLocaleString();
                    currentTenantData.pct = pct.toFixed(1) + '%';
                    currentTenantData.bar_width = Math.min(100, pct);
                    if (used >= limit) {{
                        currentTenantData.status_cat = 'blocked';
                        currentTenantData.status_badge = '<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 inline-flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span> Habis (Blocked)</span>';
                    }} else if (pct >= 80) {{
                        currentTenantData.status_cat = 'warning';
                        currentTenantData.status_badge = '<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 inline-flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Waspada (&ge;80%)</span>';
                    }} else {{
                        currentTenantData.status_cat = 'normal';
                        currentTenantData.status_badge = '<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 inline-flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Aman</span>';
                    }}
                }}

                if (resData.detail) {{
                    currentTenantData.whatsapp = resData.detail.whatsapp;
                    currentTenantData.address = resData.detail.address;
                    currentTenantData.operating_hours = resData.detail.operating_hours;
                    currentTenantData.greeting = resData.detail.greeting;
                    currentTenantData.description = resData.detail.description;
                    currentTenantData.has_profil = resData.detail.has_profil;
                    currentTenantData.has_layanan = resData.detail.has_layanan;
                    currentTenantData.has_kebijakan = resData.detail.has_kebijakan;
                    currentTenantData.has_faq = resData.detail.has_faq;
                }}

                // Update table row DOM element
                if (currentActiveTenantButton) {{
                    currentActiveTenantButton.setAttribute('data-tenant', JSON.stringify(currentTenantData));
                    const tr = currentActiveTenantButton.closest('tr');
                    if (tr) {{
                        const nameSpan = tr.querySelector('.tenant-name-span');
                        if (nameSpan) nameSpan.textContent = currentTenantData.name;
                        const tierCell = tr.querySelector('.tenant-tier-td');
                        if (tierCell) tierCell.innerHTML = '<span class="px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider bg-slate-100 text-slate-800 border border-slate-200">' + currentTenantData.tier + '</span>';
                        const quotaLimit = tr.querySelector('.tenant-quota-limit');
                        if (quotaLimit) quotaLimit.textContent = currentTenantData.limit;
                        const quotaUsed = tr.querySelector('.tenant-quota-used');
                        if (quotaUsed) quotaUsed.textContent = currentTenantData.used;
                        const remaining = tr.querySelector('.tenant-remaining');
                        if (remaining) remaining.textContent = currentTenantData.remaining;
                        const pctSpan = tr.querySelector('.tenant-pct-span');
                        if (pctSpan) pctSpan.textContent = currentTenantData.pct;
                        const pBar = tr.querySelector('.tenant-pbar');
                        if (pBar) {{
                            pBar.style.width = currentTenantData.bar_width + '%';
                            pBar.className = 'tenant-pbar h-2 rounded-full transition-all duration-500 ' + (currentTenantData.status_cat === 'blocked' ? 'bg-rose-500' : (currentTenantData.status_cat === 'warning' ? 'bg-amber-500' : 'bg-emerald-500'));
                        }}
                        const statusTd = tr.querySelector('.tenant-status-td');
                        if (statusTd) statusTd.innerHTML = currentTenantData.status_badge;
                    }}
                }}

                // Re-populate modal and switch back to overview
                openTenantModal(currentActiveTenantButton);
                switchModalTab('overview');

                showToast('✓ Konfigurasi AI &amp; Knowledge Base ' + currentTenantData.name + ' berhasil disimpan &amp; di-index ke FAISS!');
            }} catch (err) {{
                alert('Gagal menyimpan perubahan AI: ' + err.message);
            }} finally {{
                if (btnSave) {{
                    btnSave.disabled = false;
                    btnSave.innerHTML = '<span>💾 Simpan Perubahan AI &amp; Rebuild FAISS</span>';
                }}
            }}
        }}

        if (tenantModal) {{
            tenantModal.addEventListener('click', function(e) {{
                if (e.target === tenantModal) closeTenantModal();
            }});
        }}
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape' && tenantModal && !tenantModal.classList.contains('hidden')) {{
                closeTenantModal();
            }}
        }});

        // 6. Global AI Engine Modal Logic
        const globalAiModal = document.getElementById('globalAiModal');
        function openGlobalAiModal() {{
            if (!globalAiModal) return;
            loadGlobalAiSettings();
            globalAiModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }}

        function closeGlobalAiModal() {{
            if (!globalAiModal) return;
            globalAiModal.classList.add('hidden');
            document.body.style.overflow = '';
        }}

        function switchGlobalTab(tab) {{
            const panePrompts = document.getElementById('globalPanePrompts');
            const paneParams = document.getElementById('globalPaneParams');
            const btnPrompts = document.getElementById('globalTabBtn_prompts');
            const btnParams = document.getElementById('globalTabBtn_params');

            if (tab === 'params') {{
                panePrompts.classList.add('hidden');
                paneParams.classList.remove('hidden');
                btnPrompts.className = 'flex-1 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition cursor-pointer font-medium';
                btnParams.className = 'flex-1 py-1.5 rounded-lg bg-white text-indigo-700 font-bold shadow-xs transition cursor-pointer';
            }} else {{
                panePrompts.classList.remove('hidden');
                paneParams.classList.add('hidden');
                btnPrompts.className = 'flex-1 py-1.5 rounded-lg bg-white text-indigo-700 font-bold shadow-xs transition cursor-pointer';
                btnParams.className = 'flex-1 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition cursor-pointer font-medium';
            }}
        }}

        async function loadGlobalAiSettings() {{
            try {{
                const res = await fetch('/api/v1/analytics/engine-config');
                if (!res.ok) return;
                const data = await res.json();
                document.getElementById('globalLlmModel').value = data.llm_model || 'd-kreasi';
                document.getElementById('globalLlmTemp').value = data.llm_temperature !== undefined ? data.llm_temperature : 0.2;
                document.getElementById('globalLlmTokens').value = data.llm_max_tokens || 2048;
                document.getElementById('globalCsWa').value = data.ai_cs_whatsapp || '';
                document.getElementById('globalL1Prompt').value = data.l1_prompt || '';
                document.getElementById('globalL2Prompt').value = data.l2_prompt || '';
                document.getElementById('globalL3Prompt').value = data.l3_prompt || '';
                document.getElementById('globalL4Prompt').value = data.l4_prompt || '';
            }} catch (err) {{
                console.error('Gagal memuat setting engine:', err);
            }}
        }}

        async function saveGlobalAiSettings() {{
            const btn = document.getElementById('btnSaveGlobalAi');
            if (btn) {{
                btn.disabled = true;
                btn.innerHTML = '<svg class="w-4 h-4 animate-spin text-white inline-block mr-1" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg> <span>Menyimpan...</span>';
            }}

            const payload = {{
                llm_model: document.getElementById('globalLlmModel').value.trim(),
                llm_temperature: parseFloat(document.getElementById('globalLlmTemp').value) || 0.2,
                llm_max_tokens: parseInt(document.getElementById('globalLlmTokens').value) || 2048,
                ai_cs_whatsapp: document.getElementById('globalCsWa').value.trim(),
                l1_prompt: document.getElementById('globalL1Prompt').value,
                l2_prompt: document.getElementById('globalL2Prompt').value,
                l3_prompt: document.getElementById('globalL3Prompt').value,
                l4_prompt: document.getElementById('globalL4Prompt').value,
            }};

            try {{
                const res = await fetch('/api/v1/analytics/engine-config', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
                if (!res.ok) throw new Error('Gagal menyimpan konfigurasi global.');
                closeGlobalAiModal();
                showToast('✓ Konfigurasi Global AI Engine &amp; Prompts berhasil disimpan &amp; cache dibersihkan!');
            }} catch (err) {{
                alert('Gagal: ' + err.message);
            }} finally {{
                if (btn) {{
                    btn.disabled = false;
                    btn.innerHTML = '<span>💾 Simpan Pengaturan Global</span>';
                }}
            }}
        }}

        async function clearGlobalCache() {{
            try {{
                const res = await fetch('/api/v1/analytics/cache/clear', {{ method: 'POST' }});
                if (res.ok) {{
                    showToast('✓ Semantic cache berhasil dibersihkan!');
                }}
            }} catch (err) {{
                alert('Gagal membersihkan cache: ' + err.message);
            }}
        }}

        if (globalAiModal) {{
            globalAiModal.addEventListener('click', function(e) {{
                if (e.target === globalAiModal) closeGlobalAiModal();
            }});
        }}
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape' && globalAiModal && !globalAiModal.classList.contains('hidden')) {{
                closeGlobalAiModal();
            }}
        }});

        // 7. Toast Notification Utility
        function showToast(msg) {{
            let t = document.getElementById('dashboardToast');
            if (!t) {{
                t = document.createElement('div');
                t.id = 'dashboardToast';
                t.className = 'fixed bottom-6 right-6 z-50 bg-slate-900 text-white px-5 py-3 rounded-xl shadow-2xl border border-slate-700 flex items-center gap-3 text-xs font-semibold transform transition-all duration-300 opacity-0 translate-y-3';
                document.body.appendChild(t);
            }}
            t.innerHTML = '<span class="text-emerald-400 font-bold">✓</span><span>' + msg + '</span>';
            t.classList.remove('opacity-0', 'translate-y-3');
            setTimeout(() => {{
                t.classList.add('opacity-0', 'translate-y-3');
            }}, 4000);
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
            tenant_name_map = {t.id: t.name for t in tenant_rows}

            tenant_quotas = []
            for t in tenant_rows:
                stats = await UsageService.get_tenant_usage_stats(db=db, tenant_id=t.id)
                stats["name"] = t.name or t.id.replace("_", " ").title()
                stats["category"] = getattr(t, "category", "Bisnis") or "Bisnis"
                kb_info = cls._get_tenant_detail_info(t.id)
                stats.update(kb_info)
                tenant_quotas.append(stats)

            # 11. Distribusi & Tren Lalu Lintas AI (Traffic Trend)
            traffic_metrics = await cls.get_traffic_trend_metrics(db=db, days=days)
            hourly_traffic = traffic_metrics.get("hourly_traffic", [])

            return {
                "period_days": days,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "kpis": kpis,
                "layer_breakdown": layer_breakdown,
                "tenant_quotas": tenant_quotas,
                "top_questions": top_questions,
                "unanswered_queries": unanswered_queries,
                "recent_activity": recent_activity,
                "hourly_traffic": hourly_traffic,
                "traffic_trend": traffic_metrics,
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
                "hourly_traffic": [
                    {"hour": f"{h:02d}:00", "hour_num": h, "count": 0, "tenants": []}
                    for h in range(24)
                ],
            }

    @classmethod
    async def get_hourly_traffic_metrics(cls, db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """Backward-compatible wrapper untuk get_traffic_trend_metrics."""
        return await cls.get_traffic_trend_metrics(db=db, days=days)

    @classmethod
    async def get_traffic_trend_metrics(cls, db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """Menghitung tren lalu lintas AI:
        - days == 1: Distribusi 24 Jam (Hourly) Hari Ini (00:00 - 23:00 WIB)
        - days == 7: Distribusi Harian 7 Hari Terakhir (D-6 s.d. Hari Ini)
        - days == 30: Distribusi Harian 30 Hari Terakhir (D-29 s.d. Hari Ini)
        """
        now = datetime.now()
        today = now.date()

        DAYS_NAMES_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        DAYS_SHORT_ID = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
        MONTHS_SHORT_ID = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]
        MONTHS_FULL_ID = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

        try:
            tenant_stmt = select(Tenant)
            tenant_rows = (await db.execute(tenant_stmt)).scalars().all()
            tenant_name_map = {t.id: t.name for t in tenant_rows}

            if days == 1:
                # Agregasi per Jam untuk Hari Ini (00:00 - 23:00 WIB)
                period_type = "hourly"
                badge_text = "Continuous 24 Jam"
                subtitle = "Kurva Throughput Beban Chat per Jam (00:00 - 23:00 WIB)"
                peak_unit = "chat/jam"
                since_date = datetime(now.year, now.month, now.day, 0, 0, 0)

                stmt = select(
                    func.strftime("%H", Usage.created_at).label("time_key"),
                    Usage.tenant_id,
                    func.count(Usage.id).label("cnt")
                ).where(Usage.created_at >= since_date).group_by("time_key", Usage.tenant_id)
                raw_rows = (await db.execute(stmt)).all()

                data_dict = {f"{h:02d}": {"count": 0, "tenants": []} for h in range(24)}
                for row in raw_rows:
                    hr_str, t_id, cnt = row[0], row[1], row[2]
                    if hr_str and hr_str in data_dict:
                        data_dict[hr_str]["count"] += cnt
                        t_name = tenant_name_map.get(t_id, (t_id.replace("_", " ").title() if t_id else "Layer L1/L2/L3 (Non-Tenant)"))
                        data_dict[hr_str]["tenants"].append({
                            "tenant_id": t_id or "system",
                            "name": t_name,
                            "count": cnt,
                        })

                traffic_points = []
                for h in range(24):
                    key = f"{h:02d}"
                    data_dict[key]["tenants"].sort(key=lambda x: x["count"], reverse=True)
                    traffic_points.append({
                        "key": key,
                        "hour": f"{key}:00",
                        "hour_num": h,
                        "label": f"{key}:00",
                        "tooltip_title": f"⏰ {key}:00 - {key}:59 WIB",
                        "count": data_dict[key]["count"],
                        "tenants": data_dict[key]["tenants"],
                    })

                x_ticks = [
                    {"label": f"{h:02d}:00", "is_major": True}
                    for h in [0, 3, 6, 9, 12, 15, 18, 21, 23]
                ]

            elif days == 7:
                # Agregasi Harian untuk 7 Hari Terakhir
                period_type = "daily"
                badge_text = "Tren 7 Hari (Harian)"
                subtitle = "Kurva Throughput Beban Chat Harian (7 Hari Terakhir)"
                peak_unit = "chat/hari"

                date_list = [today - timedelta(days=6 - i) for i in range(7)]
                since_date = datetime.combine(date_list[0], datetime.min.time())

                stmt = select(
                    func.strftime("%Y-%m-%d", Usage.created_at).label("time_key"),
                    Usage.tenant_id,
                    func.count(Usage.id).label("cnt")
                ).where(Usage.created_at >= since_date).group_by("time_key", Usage.tenant_id)
                raw_rows = (await db.execute(stmt)).all()

                data_dict = {d.strftime("%Y-%m-%d"): {"count": 0, "tenants": []} for d in date_list}
                for row in raw_rows:
                    dt_str, t_id, cnt = row[0], row[1], row[2]
                    if dt_str and dt_str in data_dict:
                        data_dict[dt_str]["count"] += cnt
                        t_name = tenant_name_map.get(t_id, (t_id.replace("_", " ").title() if t_id else "Layer L1/L2/L3 (Non-Tenant)"))
                        data_dict[dt_str]["tenants"].append({
                            "tenant_id": t_id or "system",
                            "name": t_name,
                            "count": cnt,
                        })

                traffic_points = []
                x_ticks = []
                for i, d in enumerate(date_list):
                    key = d.strftime("%Y-%m-%d")
                    data_dict[key]["tenants"].sort(key=lambda x: x["count"], reverse=True)
                    day_short = DAYS_SHORT_ID[d.weekday()]
                    day_full = DAYS_NAMES_ID[d.weekday()]
                    date_display = "Hari Ini" if i == 6 else f"{day_short}, {d.day:02d}/{d.month:02d}"

                    traffic_points.append({
                        "key": key,
                        "hour": date_display,
                        "hour_num": i,
                        "label": date_display,
                        "tooltip_title": f"📅 {day_full}, {d.day} {MONTHS_FULL_ID[d.month]} {d.year}",
                        "count": data_dict[key]["count"],
                        "tenants": data_dict[key]["tenants"],
                    })
                    x_ticks.append({"label": date_display, "is_major": True})

            else:
                # Agregasi Harian untuk 30 Hari Terakhir (Default)
                period_type = "daily"
                badge_text = "Tren 30 Hari (Harian)"
                subtitle = "Kurva Throughput Beban Chat Harian (30 Hari Terakhir)"
                peak_unit = "chat/hari"

                date_list = [today - timedelta(days=29 - i) for i in range(30)]
                since_date = datetime.combine(date_list[0], datetime.min.time())

                stmt = select(
                    func.strftime("%Y-%m-%d", Usage.created_at).label("time_key"),
                    Usage.tenant_id,
                    func.count(Usage.id).label("cnt")
                ).where(Usage.created_at >= since_date).group_by("time_key", Usage.tenant_id)
                raw_rows = (await db.execute(stmt)).all()

                data_dict = {d.strftime("%Y-%m-%d"): {"count": 0, "tenants": []} for d in date_list}
                for row in raw_rows:
                    dt_str, t_id, cnt = row[0], row[1], row[2]
                    if dt_str and dt_str in data_dict:
                        data_dict[dt_str]["count"] += cnt
                        t_name = tenant_name_map.get(t_id, (t_id.replace("_", " ").title() if t_id else "Layer L1/L2/L3 (Non-Tenant)"))
                        data_dict[dt_str]["tenants"].append({
                            "tenant_id": t_id or "system",
                            "name": t_name,
                            "count": cnt,
                        })

                traffic_points = []
                x_ticks = []
                tick_indices = {0, 5, 10, 15, 20, 25, 29}
                for i, d in enumerate(date_list):
                    key = d.strftime("%Y-%m-%d")
                    data_dict[key]["tenants"].sort(key=lambda x: x["count"], reverse=True)
                    day_full = DAYS_NAMES_ID[d.weekday()]
                    date_display = "Hari Ini" if i == 29 else f"{d.day:02d} {MONTHS_SHORT_ID[d.month]}"

                    traffic_points.append({
                        "key": key,
                        "hour": date_display,
                        "hour_num": i,
                        "label": date_display,
                        "tooltip_title": f"📅 {day_full}, {d.day} {MONTHS_FULL_ID[d.month]} {d.year}",
                        "count": data_dict[key]["count"],
                        "tenants": data_dict[key]["tenants"],
                    })
                    if i in tick_indices:
                        x_ticks.append({"label": date_display, "is_major": True})

            max_count = max([p["count"] for p in traffic_points] or [0])
            return {
                "period_days": days,
                "period_type": period_type,
                "badge_text": badge_text,
                "subtitle": subtitle,
                "peak_unit": peak_unit,
                "max_count": max_count,
                "max_hourly_count": max_count,  # backward compatibility
                "traffic_points": traffic_points,
                "x_ticks": x_ticks,
                "hourly_traffic": traffic_points,  # backward compatibility
            }
        except Exception as e:
            logger.error(f"Error computing traffic trend metrics: {e}")
            fallback_points = [
                {"hour": f"{h:02d}:00", "hour_num": h, "label": f"{h:02d}:00", "tooltip_title": f"⏰ {h:02d}:00 WIB", "count": 0, "tenants": []}
                for h in range(24)
            ]
            return {
                "period_days": days,
                "period_type": "hourly",
                "badge_text": "Continuous 24 Jam",
                "subtitle": "Kurva Throughput Beban Chat per Jam",
                "peak_unit": "chat/jam",
                "max_count": 0,
                "max_hourly_count": 0,
                "traffic_points": fallback_points,
                "x_ticks": [{"label": f"{h:02d}:00", "is_major": True} for h in [0, 6, 12, 18, 23]],
                "hourly_traffic": fallback_points,
            }

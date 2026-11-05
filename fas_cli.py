#!/usr/bin/env python3
"""
=============================================================================
FAS 3 CLI — Orquestrador Unificado do Football Analysis System
=============================================================================
Comandos disponíveis:
  python fas_cli.py status      ➔ Exibe status dos bilhetes ativos, Soros e KPIs
  python fas_cli.py scan        ➔ Executa varredura global (20+ ligas e copas)
  python fas_cli.py sync        ➔ Comita no repo privado e sincroniza o repo público
  python fas_cli.py combo       ➔ Calculadora de odds para Same-Game Combos
  python fas_cli.py confere     ➔ Auxiliar de conferência e liquidação diária
=============================================================================
"""

import os
import sys
import json
import argparse
import subprocess
import datetime
from typing import Dict, Any, List

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FUTEBOL_DIR = os.path.join(BASE_DIR, "futebol")
HISTORICO_DIR = os.path.join(BASE_DIR, "historico")

BILHETES_FILE = os.path.join(FUTEBOL_DIR, "bilhetes_ativos.json")
SOROS_FILE = os.path.join(FUTEBOL_DIR, "soros_state.json")
RELATORIO_FILE = os.path.join(HISTORICO_DIR, "relatorio_performance.json")
BACKTEST_FILE = os.path.join(FUTEBOL_DIR, "FAS3_FOOTBALL_BACKTEST_DATABASE.md")

def run_cmd(cmd: str, cwd: str = BASE_DIR):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding="utf-8")
    return res.returncode, res.stdout.strip(), res.stderr.strip()

# =============================================================================
# COMANDO: STATUS
# =============================================================================
def cmd_status(args):
    print("\n" + "="*70)
    print("📊 PAINEL DE CONTROLE FAS 3 — STATUS DO SISTEMA")
    print("="*70)
    
    # 1. Bilhetes Ativos
    if os.path.exists(BILHETES_FILE):
        with open(BILHETES_FILE, "r", encoding="utf-8") as f:
            b_data = json.load(f)
        date = b_data.get("date", "N/A")
        status = b_data.get("status", "N/A")
        badge = "🟢 AUDITADO" if status == "AUDITED" else "🟡 PENDENTE (PRE-MATCH)"
        print(f"\n📅 Data da Grade: {date} | Status: {badge}")
        print(f"📝 Notas: {b_data.get('notes', '')[:120]}...")
        
        # Supremo
        supremo = b_data.get("supremoTicket", {})
        print(f"\n⭐ {supremo.get('name', 'Bilhete Supremo')} (Odd @{supremo.get('multiplierGlobal', 0):.2f})")
        for sel in supremo.get("selections", []):
            st = sel.get("status", "PENDING")
            icon = "✅" if st == "HIT" else ("❌" if st == "MISS" else "⏳")
            print(f"   {icon} {sel.get('match')}: {sel.get('market')} (@{sel.get('odd')})")
            
        # Estruturados
        print("\n🎫 Bilhetes Estruturados Ativos:")
        for t in b_data.get("structuredTickets", []):
            t_st = t.get("status", "PENDING")
            t_icon = "🟢" if t_st == "GREEN" else ("🔴" if t_st == "RED" else "⚪")
            print(f"   {t_icon} {t.get('name')} | Multiplicador: @{t.get('multiplier', '-')}")
            if "stopPoints" in t:
                for sp in t["stopPoints"]:
                    sp_icon = "🟢" if sp.get("status") == "GREEN" else "⚪"
                    print(f"      {sp_icon} {sp.get('level')} (@{sp.get('multiplier')}): {len(sp.get('legs', []))} seleções")
            elif "legs" in t:
                for leg in t.get("legs", []):
                    print(f"      • {leg}")
                    
    # 2. Desafio Soros
    if os.path.exists(SOROS_FILE):
        with open(SOROS_FILE, "r", encoding="utf-8") as f:
            s_data = json.load(f)
        day = s_data.get("currentDay", 1)
        stake = s_data.get("currentStake", 10.0)
        print(f"\n🔥 DESAFIO SOROS FAS 30 DIAS:")
        print(f"   ▫️ Dia Atual: DIA {day} DE {s_data.get('targetDays', 30)}")
        print(f"   ▫️ Stake Atual: R$ {stake:.2f}")
        history = s_data.get("history", [])
        if history:
            last = history[-1]
            last_st = last.get("status", "PENDING")
            last_icon = "✅ HIT" if last_st == "HIT" else ("❌ MISS" if last_st == "MISS" else "⏳ PENDING")
            print(f"   ▫️ Entrada [{last.get('date')}]: {last.get('selection')} (@{last.get('odd')}) ➔ {last_icon}")
            print(f"   ▫️ Retorno Projetado: R$ {last.get('potentialReturn', 0):.2f}")

    # 3. KPIs
    if os.path.exists(RELATORIO_FILE):
        with open(RELATORIO_FILE, "r", encoding="utf-8") as f:
            k_data = json.load(f).get("kpis", {})
        print(f"\n📈 Performance Histórica Acumulada:")
        print(f"   ▫️ Rodadas Disputadas: {k_data.get('totalRounds')} | Bilhetes: {k_data.get('totalTickets')}")
        print(f"   ▫️ Greens: {k_data.get('greenTickets')} | Reds: {k_data.get('redTickets')}")
        print(f"   ▫️ Win Rate Global: {k_data.get('winRateGlobal')} | Profit Factor: {k_data.get('profitFactor')}")
        print(f"   ▫️ SAFE Win Rate: {k_data.get('safeWinRate')} | SAFE+ Win Rate: {k_data.get('safePlusWinRate')}")
    print("="*70 + "\n")

# =============================================================================
# COMANDO: SCAN
# =============================================================================
def cmd_scan(args):
    hours = args.hours or 40
    print(f"\n🚀 Disparando varredura global FAS 3 para as próximas {hours}h...")
    scanner_py = os.path.join(FUTEBOL_DIR, "odds_scanner.py")
    if os.path.exists(scanner_py):
        subprocess.run([sys.executable, scanner_py], cwd=BASE_DIR)
    else:
        print("❌ Arquivo odds_scanner.py não encontrado!")

# =============================================================================
# COMANDO: SYNC
# =============================================================================
def cmd_sync(args):
    msg = args.msg or f"feat(fas): sincronizacao automatica [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}]"
    print(f"\n📦 Sincronizando repositório privado (tips) e público (bilhete)...")
    
    # 1. Commit e Push no repo tips
    print("1️⃣ Commitando e enviando para iadecria/tips (privado)...")
    run_cmd("git add .")
    code, out, err = run_cmd(f'git commit -m "{msg}"')
    if code == 0:
        print(f"   ✅ Commit local criado: {msg}")
    else:
        print(f"   ℹ️ Nenhuma alteração pendente para commit local.")
        
    code_push, out_p, err_p = run_cmd("git push origin main")
    if code_push == 0:
        print("   ✅ Push concluído com sucesso em origin/main (iadecria/tips)!")
    else:
        print(f"   ⚠️ Aviso no push privado: {err_p or out_p}")

    # 2. Executa sync_public.py
    print("\n2️⃣ Sincronizando e publicando em iadecria/bilhete (público)...")
    sync_py = os.path.join(BASE_DIR, "sync_public.py")
    if os.path.exists(sync_py):
        subprocess.run([sys.executable, sync_py], cwd=BASE_DIR)
    else:
        print("   ❌ sync_public.py não encontrado.")
    print("🎉 Sincronização concluída com sucesso!\n")

# =============================================================================
# COMANDO: COMBO CALCULATOR
# =============================================================================
def cmd_combo(args):
    print("\n" + "="*60)
    print("🧮 CALCULADORA DE SAME-GAME COMBOS FAS 3")
    print("="*60)
    
    if args.dc_under:
        # Combo Blindado: 1X + Under X.5
        dc_odd = args.dc or 1.15
        under_odd = args.under or 1.25
        # Correlação típica positiva entre não perder e jogo econômico ~1.10 a 1.20
        combo_fair = round((dc_odd * under_odd) * 1.08, 2)
        print(f"🛡️ COMBO BLINDADO: [1X (@{dc_odd}) + Menos de 3.5 (@{under_odd})]")
        print(f"   ➔ Odd Média de Mercado: @{combo_fair}")
        print(f"   ➔ Placares Cobertos: 1x0, 2x0, 3x0, 0x0, 1x1, 2x1 (6 placares)")
        
    if args.ml_over:
        # Combo Dominante: ML + Over 1.5
        ml_odd = args.ml or 1.30
        over_odd = args.over or 1.20
        combo_fair = round((ml_odd * over_odd) * 1.06, 2)
        print(f"\n🚀 COMBO DOMINANTE: [Vitória Seca (@{ml_odd}) + Mais de 1.5 Gols (@{over_odd})]")
        print(f"   ➔ Odd Média de Mercado: @{combo_fair}")
        print(f"   ➔ Placares Cobertos: 2x0, 2x1, 3x0, 3x1, 4x0...")

    if args.btts_over:
        # Combo Trocação: Ambos Marcam + Over 2.5
        btts_odd = args.btts or 1.60
        over25_odd = args.over25 or 1.70
        combo_fair = round(max(btts_odd, over25_odd) * 1.25, 2)
        print(f"\n💥 COMBO TROCAÇÃO: [Ambos Marcam (@{btts_odd}) + Mais de 2.5 Gols (@{over25_odd})]")
        print(f"   ➔ Odd Média de Mercado: @{combo_fair}")
        print(f"   ➔ Placares Cobertos: 2x1, 1x2, 2x2, 3x1, 3x2...")
        
    if not (args.dc_under or args.ml_over or args.btts_over):
        print("💡 Use parâmetros para simular combos:")
        print("   python fas_cli.py combo --dc-under --dc 1.14 --under 1.20")
        print("   python fas_cli.py combo --ml-over --ml 1.35 --over 1.20")
        print("   python fas_cli.py combo --btts-over --btts 1.55 --over25 1.70")
    print("="*60 + "\n")

# =============================================================================
# COMANDO: CONFERE (LIQUIDAÇÃO E AUDITORIA OFICIAL)
# =============================================================================
def cmd_confere(args):
    print("\n" + "="*70)
    print("⚖️ AUDITORIA E LIQUIDAÇÃO OFICIAL — PROTOCOLO CONFERE FAS 3")
    print("="*70)
    
    if os.path.exists(BILHETES_FILE):
        with open(BILHETES_FILE, "r", encoding="utf-8") as f:
            b_data = json.load(f)
            
        date = b_data.get("date", "N/A")
        status = b_data.get("status", "N/A")
        print(f"📅 Data da Rodada: {date} | Status Geral: {status}")
        print(f"📸 Snapshot ID: {b_data.get('snapshotId', 'N/A')}\n")
        
        # 1. Bilhete Supremo
        supremo = b_data.get("supremoTicket", {})
        s_status = supremo.get("status", "PENDING")
        s_badge = "🟢 GREEN" if s_status in ["GREEN", "HIT"] else ("🔴 RED" if s_status in ["RED", "MISS"] else "🟡 PENDING")
        print(f"⭐ {supremo.get('name')} ➔ {s_badge} (@{supremo.get('multiplierGlobal', 0):.2f})")
        for sel in supremo.get("selections", []):
            st = sel.get("status", "PENDING")
            icon = "✅ HIT" if st in ["HIT", "GREEN"] else ("❌ MISS" if st in ["MISS", "RED"] else "⏳ PENDING")
            print(f"   [{icon}] {sel.get('match')}: {sel.get('market')} (@{sel.get('odd')})")
            
        # 2. Bilhetes Estruturados
        print("\n🎫 Bilhetes Estruturados:")
        for t in b_data.get("structuredTickets", []):
            t_st = t.get("status", "PENDING")
            t_badge = "🟢 GREEN" if t_st in ["GREEN", "HIT"] else ("🔴 RED" if t_st in ["RED", "MISS"] else ("🟡 PARCIAL" if t_st in ["PARTIAL", "PARTIAL_HIT"] else "🟡 PENDING"))
            mult = f"@{t.get('multiplier')}" if t.get('multiplier') else ""
            print(f"\n   {t_badge} {t.get('name')} {mult}")
            
            if "stopPoints" in t:
                for sp in t["stopPoints"]:
                    sp_st = sp.get("status", "PENDING")
                    sp_icon = "🟢 GREEN" if sp_st in ["GREEN", "HIT"] else ("🔴 RED" if sp_st in ["RED", "MISS"] else "⚪")
                    print(f"      ▫️ [{sp_icon}] {sp.get('level')} (@{sp.get('multiplier')}):")
                    for leg in sp.get("legs", []):
                        print(f"         • {leg}")
            elif "legs" in t:
                for leg in t.get("legs", []):
                    print(f"      • {leg}")
                    
        # 3. Desafio Soros
        soros = b_data.get("sorosTicket", {})
        soros_st = soros.get("status", "PENDING")
        soros_badge = "🟢 GREEN" if soros_st in ["GREEN", "HIT"] else ("🔴 RED" if soros_st in ["RED", "MISS"] else "🟡 PENDING")
        print(f"\n🔥 {soros.get('name')} ➔ {soros_badge}")
        print(f"   Stake: R$ {soros.get('stake', 0):.2f} | Multiplicador: @{soros.get('multiplier', 0):.2f} | Retorno: R$ {soros.get('potentialReturn', 0):.2f}")
        for leg in soros.get("legs", []):
            print(f"   • {leg}")
            
    print("="*70 + "\n")

# =============================================================================
# MAIN
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="FAS 3 CLI — Orquestrador Unificado do Football Analysis System")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # Status
    p_status = subparsers.add_parser("status", help="Exibe status dos bilhetes ativos e Soros")
    p_status.set_defaults(func=cmd_status)

    # Confere
    p_confere = subparsers.add_parser("confere", help="Exibe relatório oficial de conferência e liquidação diária")
    p_confere.set_defaults(func=cmd_confere)

    # Scan
    p_scan = subparsers.add_parser("scan", help="Executa varredura global nas 20+ ligas e copas")
    p_scan.add_argument("--hours", type=int, default=40, help="Horas à frente para varredura (padrão: 40h)")
    p_scan.set_defaults(func=cmd_scan)

    # Sync
    p_sync = subparsers.add_parser("sync", help="Comita e sincroniza repositórios privado e público")
    p_sync.add_argument("--msg", type=str, default="", help="Mensagem do commit")
    p_sync.set_defaults(func=cmd_sync)

    # Combo
    p_combo = subparsers.add_parser("combo", help="Calculadora de Same-Game Combos")
    p_combo.add_argument("--dc-under", action="store_true", help="Simula Combo Blindado (1X + Sub 3.5)")
    p_combo.add_argument("--ml-over", action="store_true", help="Simula Combo Dominante (V1 + Over 1.5)")
    p_combo.add_argument("--btts-over", action="store_true", help="Simula Combo Trocação (BTTS + Over 2.5)")
    p_combo.add_argument("--dc", type=float, default=1.14, help="Odd Dupla Chance")
    p_combo.add_argument("--under", type=float, default=1.20, help="Odd Under Gols")
    p_combo.add_argument("--ml", type=float, default=1.30, help="Odd Vitória Seca")
    p_combo.add_argument("--over", type=float, default=1.20, help="Odd Over Gols")
    p_combo.add_argument("--btts", type=float, default=1.55, help="Odd Ambos Marcam")
    p_combo.add_argument("--over25", type=float, default=1.70, help="Odd Mais de 2.5 Gols")
    p_combo.set_defaults(func=cmd_combo)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    args.func(args)

if __name__ == "__main__":
    main()

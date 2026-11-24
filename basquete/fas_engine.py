"""
FAS Basketball - Motor de Execução e Disparo (FAS Basketball Engine V2.0)
Responsável por disparar a grade da NBA, atualizar os arquivos e notificar os mensageiros.
"""

import os
import sys
import json
import datetime
import subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, "futebol"))

import notifier
from notifier import display_ticket_label

def format_nba_message(data: dict) -> str:
    date = data.get("date", "Hoje")
    supremo = data.get("supremoTicket", {})
    safe = data.get("safeTicket", {})
    soros = data.get("sorosTicket", {})
    experimental = data.get("experimentalTickets", [])
    round_sweep = data.get("roundSweepTicket", {})

    lines = []
    lines.append(f"🏀 <b>FAS BASKETBALL V2.0 — EMIRATES NBA CUP ({date})</b>")
    lines.append("⚡ <i>Melbet / Asian Elastic Engine • Spreads Protegidos</i>\n")

    # Soros
    if soros:
        day = soros.get("currentDay", 1)
        stake = soros.get("stake", 10.0)
        mult = soros.get("multiplier", 1.37)
        ret = soros.get("potentialReturn", 13.70)
        lines.append(f"🎯 <b>DESAFIO SOROS BASQUETE — DIA {day} DE 30</b>")
        lines.append(f"💰 Stake: <b>R$ {stake:.2f}</b> | Cotação: <b>@{mult:.2f}</b> ➔ Retorno: <b>R$ {ret:.2f}</b>")
        for leg in soros.get("legs", []):
            lines.append(f"  • {leg}")
        lines.append("")

    # Supremo
    if supremo:
        mult = supremo.get("multiplierGlobal", 2.05)
        lines.append(f"💎 <b>{display_ticket_label('SUPREMO', 'SUPREMO BASQUETE')} (@{mult:.2f})</b>")
        lines.append("<i>Tripla de Elite com Spreads Elásticos e Mando de Quadra</i>")
        for sel in supremo.get("selections", []):
            lines.append(f"  • <b>{sel.get('match')}</b>: {sel.get('market')} (@{sel.get('odd')})")
        lines.append("")

    # Safe
    if safe:
        mult = safe.get("multiplier", 3.17)
        lines.append(f"👑 <b>{display_ticket_label('SAFE', 'MÚLTIPLA 1 — SAFE BASQUETE')} (Stop Points @{mult:.2f})</b>")
        for sp in safe.get("stopPoints", []):
            stop_name = sp.get("stop", "")
            s_mult = sp.get("subtotalOdd", 0.0)
            lines.append(f"  📍 <b>{stop_name}</b> (@{s_mult:.2f}):")
            for leg in sp.get("legs", []):
                lines.append(f"     - {leg}")
        lines.append("")

    # Ataque
    for exp in experimental:
        name = exp.get("name", "")
        e_mult = exp.get("multiplier", 0.0)
        lines.append(f"⚔️ <b>{display_ticket_label(exp.get('type', 'ATTACK'), name)} (@{e_mult:.2f})</b>")
        for leg in exp.get("legs", []):
            lines.append(f"  • {leg}")
        lines.append("")

    # Round Sweep
    if round_sweep:
        r_name = round_sweep.get("name", "")
        r_mult = round_sweep.get("multiplier", 41.80)
        lines.append(f"🥉 <b>{display_ticket_label(round_sweep.get('type', 'IMPROVAVEL'), r_name)}</b>")
        lines.append(f"🏆 Cotação Acumulada: <b>@{r_mult:.2f}</b> (Previsão dos 9 jogos da Copa da NBA)")
        for sel in round_sweep.get("selections", []):
            lines.append(f"  • {sel.get('match').split('(')[0].strip()}: <b>{sel.get('market')}</b> (@{sel.get('odd')})")

    lines.append("\n🔗 <b>Raw JSON:</b> https://raw.githubusercontent.com/iadecria/bilhete/main/basquete/bilhetes_ativos.json")
    return "\n".join(lines)


def run_basketball_pipeline():
    print("="*60)
    print("🏀 INICIANDO PIPELINE DE BASQUETE FAS V2.0 (NBA CUP)")
    print("="*60)

    bilhetes_file = os.path.join(current_dir, "bilhetes_ativos.json")
    if not os.path.exists(bilhetes_file):
        print(f"❌ Arquivo {bilhetes_file} não encontrado.")
        return False

    with open(bilhetes_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_str = data.get("date", datetime.date.today().isoformat())
    print(f"📅 Data da Grade NBA: {date_str} | Status: {data.get('status')}")

    # 1. Formata mensagem
    msg = format_nba_message(data)

    # 2. Dispara notificação Telegram
    sent = notifier.send_telegram(msg)
    if not sent:
        print("ℹ️ Notificação Telegram não enviada ou credenciais pendentes.")

    # 3. Executa sincronização com o repositório público (sync_public.py)
    sync_script = os.path.join(parent_dir, "sync_public.py")
    if os.path.exists(sync_script):
        print("\n🚀 Executando sincronização pública (sync_public.py)...")
        try:
            res = subprocess.run([sys.executable, sync_script], capture_output=True, text=True, check=True)
            print(res.stdout)
        except Exception as e:
            print(f"⚠️ Erro ao sincronizar público: {e}")

    print("\n✅ Pipeline de Basquete finalizado com sucesso!")
    return True

if __name__ == "__main__":
    run_basketball_pipeline()

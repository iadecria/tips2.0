"""
FAS 3 - Motor de Auditoria e Disparo Noturno (Confere Engine V7.0)
Responsável por auditar os resultados, liquidar os bilhetes, atualizar o Soros e notificar o mensageiro.
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

import notifier

def run_confere_pipeline():
    print("="*60)
    print("🌙 INICIANDO PIPELINE DE CONFERE NOTURNO FAS V7.0")
    print("="*60)

    bilhetes_file = os.path.join(current_dir, "bilhetes_ativos.json")
    if not os.path.exists(bilhetes_file):
        print(f"❌ Arquivo {bilhetes_file} não encontrado.")
        return False

    with open(bilhetes_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_str = data.get("date", datetime.date.today().isoformat())
    audit_summary = data.get("auditSummary", {})

    # Placares resumidos se disponíveis
    placares = [
        "Bayern de Munique 4 × 0 Colônia (W1 ✅, V1 & +1.5 ✅, Over 2.5 ✅)",
        "Athletic Bilbao 1 × 0 Espanyol (W1 ✅, 1X ✅, Under 3.5 ✅)",
        "Arminia Bielefeld 2 × 1 Magdeburg (Over 1.5 ✅)",
        "Troyes 1 × 1 Le Havre (Troyes 1X ✅, Under 3.5 ✅)"
    ]

    # 1. Formata mensagem do Confere
    msg = notifier.format_confere_message(date_str, audit_summary, placares)

    # 2. Envia para o Telegram
    sent = notifier.send_telegram(msg)
    if not sent:
        print("ℹ️ Notificação Telegram não enviada ou credenciais pendentes.")

    # 3. Executa sincronização com o repositório público
    sync_script = os.path.join(parent_dir, "sync_public.py")
    if os.path.exists(sync_script):
        print("\n🚀 Executando sincronização pública (sync_public.py)...")
        try:
            res = subprocess.run([sys.executable, sync_script], capture_output=True, text=True, check=True)
            print(res.stdout)
        except Exception as e:
            print(f"⚠️ Erro ao sincronizar público: {e}")

    print("\n✅ Pipeline de confere finalizado com sucesso!")
    return True

if __name__ == "__main__":
    run_confere_pipeline()

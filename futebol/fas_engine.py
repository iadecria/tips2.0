"""
FAS 3 - Motor de Execução e Disparo Matinal (FAS Engine V7.0)
Responsável por disparar a grade diária, atualizar os arquivos e notificar os mensageiros.
"""

import os
import sys
import json
import datetime
import subprocess

# Garante path correto
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

import notifier

def run_morning_pipeline():
    print("="*60)
    print("🌅 INICIANDO PIPELINE MATINAL FAS V7.0 (MELBET ENGINE)")
    print("="*60)

    bilhetes_file = os.path.join(current_dir, "bilhetes_ativos.json")
    if not os.path.exists(bilhetes_file):
        print(f"❌ Arquivo {bilhetes_file} não encontrado.")
        return False

    with open(bilhetes_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_str = data.get("date", datetime.date.today().isoformat())
    status = data.get("status", "ACTIVE")
    print(f"📅 Data da Grade: {date_str} | Status: {status}")

    # 1. Formata mensagem para Telegram / Mensageiro
    msg = notifier.format_grade_message(data)

    # 2. Dispara notificação
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

    print("\n✅ Pipeline matinal finalizado com sucesso!")
    return True

if __name__ == "__main__":
    run_morning_pipeline()

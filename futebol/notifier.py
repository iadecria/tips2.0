"""
FAS 3 - Notifier Module (Telegram & WhatsApp Webhook)
Módulo universal para envio de notificações automáticas da Grade FAS V7.0 e do Confere Noturno.
"""

import os
import sys
import json
import html
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Configurações de credenciais via variáveis de ambiente ou arquivo local seguro (.env / config)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# WhatsApp via CallMeBot (Opcional)
CALLMEBOT_PHONE = os.environ.get("CALLMEBOT_PHONE", "")
CALLMEBOT_API_KEY = os.environ.get("CALLMEBOT_API_KEY", "")


def display_ticket_label(ticket_type: Any, fallback_name: str = "Bilhete") -> str:
    """Return the FAS Elo presentation label without changing internal ticket IDs."""
    normalized = str(ticket_type or "").strip().upper().replace("Á", "A")
    if "SAFE_PLUS" in normalized or "SAFE+" in normalized or "SAFEPLUS" in normalized:
        elo = "OURO"
    elif normalized == "SAFE" or normalized.startswith("SAFE_") or normalized == "MODULAR_STOP_POINTS":
        elo = "MESTRE"
    elif "SUPREMO" in normalized or "SUPREMA" in normalized:
        elo = "DIAMANTE"
    elif "ATTACK" in normalized or "PRA CIMA" in normalized:
        elo = "PRATA"
    elif "IMPROV" in normalized or "ROUND_SWEEP" in normalized:
        elo = "BRONZE"
    else:
        return str(fallback_name)
    return f"{elo} — {fallback_name}"


def send_telegram(message: str, bot_token: Optional[str] = None, chat_id: Optional[str] = None) -> bool:
    """
    Envia mensagem formatada para o Telegram via Bot API oficial.
    Suporta quebra automática em chunks se a mensagem exceder 4000 caracteres.
    """
    token = bot_token or TELEGRAM_BOT_TOKEN
    target_chat = chat_id or TELEGRAM_CHAT_ID

    if not token or not target_chat:
        print("⚠️ [Notifier] Telegram não configurado (TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID ausentes).")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Telegram aceita até 4096 caracteres por mensagem
    max_len = 3900
    chunks = [message[i:i + max_len] for i in range(0, len(message), max_len)]

    success = True
    for chunk in chunks:
        payload = {
            "chat_id": target_chat,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if not result.get("ok"):
                    print(f"❌ [Notifier] Erro Telegram: {result}")
                    success = False
        except Exception as e:
            # Fallback sem HTML se houver erro de formatação
            try:
                payload["parse_mode"] = ""
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    pass
            except Exception as ex2:
                print(f"❌ [Notifier] Falha ao enviar Telegram: {e} | Fallback: {ex2}")
                success = False

    if success:
        print("✅ [Notifier] Mensagem enviada com sucesso para o Telegram!")
    return success


def send_whatsapp_callmebot(message: str, phone: Optional[str] = None, apikey: Optional[str] = None) -> bool:
    """Envia mensagem para WhatsApp pessoal via CallMeBot (gratuito)"""
    ph = phone or CALLMEBOT_PHONE
    key = apikey or CALLMEBOT_API_KEY

    if not ph or not key:
        return False

    encoded_text = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={ph}&text={encoded_text}&apikey={key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FAS-Notifier/7.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode("utf-8")
            if "Success" in content:
                print("✅ [Notifier] Mensagem enviada com sucesso para o WhatsApp!")
                return True
    except Exception as e:
        print(f"❌ [Notifier] Erro CallMeBot WhatsApp: {e}")
    return False


def format_grade_message(data: Dict[str, Any]) -> str:
    """Formata o JSON de bilhetes ativos para uma mensagem rica e elegante do Telegram (HTML)"""
    date = data.get("date", "Hoje")
    supremo = data.get("supremoTicket", {})
    soros = data.get("sorosTicket", {})
    multiplas = data.get("structuredTickets", [])

    lines = []
    lines.append(f"📋 <b>FAS V7.5 — GRADE OFICIAL ({date})</b>")
    lines.append("⚡ <i>Melbet Engine Edition • Regras FAS V7.5</i>\n")

    conformity = data.get("conformity", {})
    conformity_status = conformity.get("status")
    if conformity_status == "REVIEW":
        lines.append("⚠️ <b>Conformidade em revisão; selo não emitido.</b> Consulte o relatório local antes de tratar as regras como verificadas.\n")
    elif conformity_status == "COMPLIANT":
        lines.append("✅ <b>Grade aprovada pelas regras operacionais V7.5.</b>\n")
    elif conformity_status == "NO_BET":
        lines.append("📭 <b>Dia sem bilhetes (NO BET).</b>\n")

    # Soros
    if soros:
        s_day = soros.get("day", 1)
        s_stake = soros.get("stake", 10.0)
        s_odd = soros.get("multiplier", 1.44)
        s_ret = soros.get("potentialReturn", 0.0)
        lines.append(f"🔥 <b>DESAFIO SOROS — DIA {s_day} DE 30</b>")
        lines.append(f"💰 Stake: <b>R$ {s_stake:.2f}</b> | Cotação: <b>@{s_odd:.2f}</b> ➔ Retorno: <b>R$ {s_ret:.2f}</b>")
        for leg in soros.get("legs", []):
            lines.append(f"  • {leg}")
        lines.append("")

    # Supremo
    if supremo:
        sup_odd = supremo.get("multiplierGlobal", 3.0)
        sup_stake = supremo.get("stake", 3.0)
        sup_ret = supremo.get("potentialReturn", 0.0)
        lines.append(f"💎 <b>DIAMANTE — BILHETE SUPREMO V7 (@{sup_odd:.2f})</b>")
        lines.append(f"💵 Stake sugerida: <b>R$ {sup_stake:.2f}</b> ➔ Retorno: <b>R$ {sup_ret:.2f}</b>")
        for sel in supremo.get("selections", []):
            lines.append(f"  • <b>{sel.get('match')}</b>: {sel.get('market')} (@{sel.get('odd')})")
        lines.append("")

    # SAFE
    safe_ticket = next((t for t in multiplas if t.get("type") == "SAFE"), None)
    if safe_ticket:
        lines.append("👑 <b>MESTRE — MÚLTIPLA 1 (SAFE) V7 (Stop Points)</b>")
        lines.append(f"💵 Stake: <b>R$ {safe_ticket.get('stake', 15.0):.2f}</b>")
        for sp in safe_ticket.get("stopPoints", []):
            lvl = sp.get("level", "")
            mult = sp.get("multiplier", 0.0)
            ret = sp.get("potentialReturn", 0.0)
            lines.append(f"  🎯 <b>{lvl}</b> (@{mult:.2f}) ➔ Retorno: <b>R$ {ret:.2f}</b>")
            for leg in sp.get("legs", []):
                lines.append(f"     - {leg}")
        lines.append("")

    # Outras Múltiplas resumidas
    lines.append("🎲 <b>BILHETES DE COBERTURA & ALAVANCAGEM:</b>")
    for m in multiplas:
        if m.get("type") == "SAFE":
            continue
        name = display_ticket_label(m.get("type"), m.get("name", "Bilhete"))
        mult = m.get("multiplier", 0.0)
        stk = m.get("stake", 1.0)
        ret = m.get("potentialReturn", 0.0)
        lines.append(f"  • <b>{name}</b> (@{mult:.2f}) | Stake: R$ {stk:.2f} ➔ R$ {ret:.2f}")

    lines.append("\n🔗 <b>Links e Arquivos:</b>")
    lines.append("• Raw JSON: https://raw.githubusercontent.com/iadecria/bilhete/main/futebol/bilhetes_ativos.json")
    lines.append("• Simulador de Unidade: Abra simulador_unidades.html")

    return "\n".join(lines)


def format_confere_message(date: str, summary: Dict[str, Any], placares: list) -> str:
    """Formata o relatório de auditoria e confere da noite para o Telegram"""
    lines = []
    lines.append(f"📊 <b>CONFERE OFICIAL FAS — {date}</b>")
    lines.append(f"🏆 Resultado: <b>{summary.get('roundResult', 'CONFERE CONCLUÍDO')}</b>\n")

    financial = summary.get("financialSettlements", [])
    if financial:
        inv = summary.get("invested", 0.0)
        ret = summary.get("returned", 0.0)
        luc = summary.get("netProfit", 0.0)
        lines.append("💵 <b>LIQUIDAÇÃO FINANCEIRA DO SNAPSHOT:</b>")
        lines.append(f"• Stake declarada: <b>R$ {inv:.2f}</b>")
        ret_text = f"R$ {ret:.2f}" if isinstance(ret, (int, float)) else "pendente (há combinações/bilhetes sem resultado)"
        luc_text = f"R$ {luc:.2f}" if isinstance(luc, (int, float)) else "pendente (há combinações/bilhetes sem resultado)"
        lines.append(f"• Retorno bruto calculado: <b>{ret_text}</b>")
        lines.append(f"• Resultado líquido calculado: <b>{luc_text}</b>")
        for item in financial:
            result = item.get("result", {})
            gross = result.get("grossReturn")
            net = result.get("netResult")
            gross_text = f"R$ {gross:.2f}" if isinstance(gross, (int, float)) else "pendente"
            net_text = f"R$ {net:.2f}" if isinstance(net, (int, float)) else "pendente"
            evidence = "recibo confirmado" if result.get("calculationBasis") == "VERIFIED_RECEIPT" else "estimativa"
            ticket_name = display_ticket_label(item.get("ticketType"), item.get("ticketName", item.get("ticketId", "Bilhete")))
            label = html.escape(ticket_name)
            status = html.escape(str(result.get("status", "PENDING")))
            lines.append(f"  • {label}: <b>{status}</b> | bruto {gross_text} | líquido {net_text} | {evidence}")
            divergence = item.get("divergence")
            if divergence:
                lines.append("    ⚠️ <b>DIVERGÊNCIA:</b> " + html.escape(json.dumps(divergence, ensure_ascii=False, sort_keys=True)))
            for proof in item.get("selectionEvidence", []):
                fixture = html.escape(str(proof.get("fixture", "partida desconhecida")))
                period = html.escape(str(proof.get("period", "período desconhecido")))
                source = html.escape(str(proof.get("source", "fonte desconhecida")))
                retrieved = html.escape(str(proof.get("retrievedAt", "horário desconhecido")))
                score = html.escape(str(proof.get("score", "placar não informado")))
                lines.append(f"    • {fixture} | {period} | {score} | fonte: {source} | consulta: {retrieved}")
    else:
        lines.append("💵 <b>LIQUIDAÇÃO FINANCEIRA:</b>")
        lines.append("• Sem evidência estruturada verificável; nenhum retorno foi apresentado como realizado.")
    lines.append("")

    lines.append("⚽ <b>RESULTADOS DOS JOGOS AUDITADOS:</b>")
    for p in placares:
        lines.append(f"  • {p}")
    lines.append("")

    lines.append("🔥 <b>DESAFIO SOROS:</b>")
    lines.append(f"• Status: <b>{summary.get('sorosDay5Status', summary.get('sorosDay4Status', 'ATIVO'))}</b>")
    lines.append(f"• Próxima Stake (Dia {summary.get('sorosNextDay', 6)}): <b>R$ {summary.get('sorosNextStake', 0.0):.2f}</b>")
    lines.append(f"• Cofre Seguro: <b>R$ {summary.get('sorosVaultProfit', 10.0):.2f} 🔒</b>")

    return "\n".join(lines)


if __name__ == "__main__":
    # Teste de conexão caso executado diretamente
    print("Testando módulo de notificação...")
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        send_telegram("🧪 <b>Teste de Conexão FAS Notifier</b>\nMódulo de notificação pronto para operação!")
    else:
        print("ℹ️ Variáveis TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID não definidas no ambiente.")

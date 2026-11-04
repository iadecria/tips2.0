"""
Sync Public - Publicador Automático de Dados para o Repositório Público (iadecria/bilhete)
Copia apenas os arquivos JSON públicos do repositório privado (tips) para o repositório público (bilhete)
e faz o commit e push automaticamente.
"""

import os
import shutil
import subprocess
import datetime
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_REPO_DIR = os.path.join(BASE_DIR, ".bilhete_dist")
PUBLIC_REPO_URL = "https://github.com/iadecria/bilhete.git"

def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding="utf-8")
    return res.returncode, res.stdout, res.stderr

def sync():
    print("🚀 Iniciando sincronização de dados para o repositório público (iadecria/bilhete)...")
    
    # 1. Garante que o clone existe
    if not os.path.exists(PUBLIC_REPO_DIR):
        print("Clonando repositório público...")
        code, out, err = run_cmd(f'git clone {PUBLIC_REPO_URL} "{PUBLIC_REPO_DIR}"')
        if code != 0:
            print(f"❌ Erro ao clonar: {err}")
            sys.exit(1)
            
    # Atualiza o repositório público (git pull) preservando commits remotos
    run_cmd("git pull --rebase origin main", cwd=PUBLIC_REPO_DIR)
    
    # 2. Cria pastas necessárias no repo público
    os.makedirs(os.path.join(PUBLIC_REPO_DIR, "data"), exist_ok=True)
    os.makedirs(os.path.join(PUBLIC_REPO_DIR, "futebol"), exist_ok=True)
    os.makedirs(os.path.join(PUBLIC_REPO_DIR, "basquete"), exist_ok=True)
    os.makedirs(os.path.join(PUBLIC_REPO_DIR, "historico"), exist_ok=True)
    
    # Suporte a Next.js public folder se existir
    pub_dir = os.path.join(PUBLIC_REPO_DIR, "public")
    if os.path.exists(pub_dir):
        os.makedirs(os.path.join(pub_dir, "futebol"), exist_ok=True)
        os.makedirs(os.path.join(pub_dir, "basquete"), exist_ok=True)
        os.makedirs(os.path.join(pub_dir, "historico"), exist_ok=True)
    
    # 3. Copia bilhetes ativos de futebol
    src_bilhetes = os.path.join(BASE_DIR, "futebol", "bilhetes_ativos.json")
    if os.path.exists(src_bilhetes):
        shutil.copy2(src_bilhetes, os.path.join(PUBLIC_REPO_DIR, "data", "bilhetes_ativos.json"))
        shutil.copy2(src_bilhetes, os.path.join(PUBLIC_REPO_DIR, "futebol", "bilhetes_ativos.json"))
        if os.path.exists(pub_dir):
            shutil.copy2(src_bilhetes, os.path.join(pub_dir, "futebol", "bilhetes_ativos.json"))
        print("✅ Copiado: bilhetes_ativos.json (Futebol)")

    # 3.1 Copia soros_state.json se existir
    src_soros = os.path.join(BASE_DIR, "futebol", "soros_state.json")
    if os.path.exists(src_soros):
        shutil.copy2(src_soros, os.path.join(PUBLIC_REPO_DIR, "data", "soros_state.json"))
        shutil.copy2(src_soros, os.path.join(PUBLIC_REPO_DIR, "futebol", "soros_state.json"))
        if os.path.exists(pub_dir):
            shutil.copy2(src_soros, os.path.join(pub_dir, "futebol", "soros_state.json"))
        print("✅ Copiado: soros_state.json")

    # 4. Copia bilhetes ativos de basquete
    src_basquete = os.path.join(BASE_DIR, "basquete", "bilhetes_ativos.json")
    if os.path.exists(src_basquete):
        shutil.copy2(src_basquete, os.path.join(PUBLIC_REPO_DIR, "data", "bilhetes_ativos_basquete.json"))
        shutil.copy2(src_basquete, os.path.join(PUBLIC_REPO_DIR, "basquete", "bilhetes_ativos.json"))
        if os.path.exists(pub_dir):
            shutil.copy2(src_basquete, os.path.join(pub_dir, "basquete", "bilhetes_ativos.json"))
        print("✅ Copiado: bilhetes_ativos.json (Basquete)")
        
    # 5. Copia relatório consolidado
    src_relatorio = os.path.join(BASE_DIR, "historico", "relatorio_performance.json")
    if os.path.exists(src_relatorio):
        shutil.copy2(src_relatorio, os.path.join(PUBLIC_REPO_DIR, "data", "relatorio_performance.json"))
        shutil.copy2(src_relatorio, os.path.join(PUBLIC_REPO_DIR, "historico", "relatorio_performance.json"))
        if os.path.exists(pub_dir):
            shutil.copy2(src_relatorio, os.path.join(pub_dir, "historico", "relatorio_performance.json"))
        print("✅ Copiado: relatorio_performance.json")
        
    # 6. README no repo público
    readme_path = os.path.join(PUBLIC_REPO_DIR, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# FAS ELITE — Public Data Feed\n\nFeed público de dados e bilhetes sincronizados automaticamente para o dashboard.\n")
            
    # 6. Git commit e push no repo público
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    run_cmd("git checkout -B main", cwd=PUBLIC_REPO_DIR)
    run_cmd("git add .", cwd=PUBLIC_REPO_DIR)
    code_c, out_c, _ = run_cmd(f'git commit -m "feat(data): sincroniza bilhetes e relatorio [{now_str}]"', cwd=PUBLIC_REPO_DIR)
    
    print("Enviando dados para o GitHub (iadecria/bilhete)...")
    code_p, out_p, err_p = run_cmd("git push -u origin main", cwd=PUBLIC_REPO_DIR)
    if code_p == 0:
        print("🎉 Sincronização pública concluída com sucesso no GitHub!")
        print(f"🔗 https://raw.githubusercontent.com/iadecria/bilhete/main/futebol/bilhetes_ativos.json")
        print(f"🔗 https://raw.githubusercontent.com/iadecria/bilhete/main/historico/relatorio_performance.json")
    else:
        print(f"⚠️ Aviso ao subir: {err_p} {out_p}")

if __name__ == "__main__":
    sync()

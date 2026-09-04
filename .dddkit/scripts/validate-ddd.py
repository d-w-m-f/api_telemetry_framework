import os
import sys
import glob
import re
from pathlib import Path

def get_project_root():
    """Assumes this script is in specs/DDD-Kit/scripts/"""
    script_path = Path(__file__).resolve()
    return script_path.parent.parent.parent.parent

def find_domain_files(specs_dir):
    return glob.glob(str(specs_dir / "BoundedContexts" / "**" / "domain.md"), recursive=True)

def extract_implemented_in(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Busca por implemented_in: <wildcard> no header
    match = re.search(r'^implemented_in:\s*(.+)$', content, re.MULTILINE)
    if match:
        val = match.group(1).strip()
        # Remove eventuais aspas
        if val.startswith(('"', "'")) and val.endswith(('"', "'")):
            val = val[1:-1]
        return val
    return None

def validate():
    root_dir = get_project_root()
    specs_dir = root_dir / "specs" / "DDD-Kit"
    
    domain_files = find_domain_files(specs_dir)
    if not domain_files:
        print("⚠️ Nenhum arquivo domain.md encontrado em specs/DDD-Kit/BoundedContexts/")
        return 0
        
    errors = 0
    
    for df in domain_files:
        rel_df = Path(df).relative_to(root_dir)
        print(f"🔍 Analisando: {rel_df}")
        
        wildcard = extract_implemented_in(df)
        if not wildcard or "WILDCARD_EXATO" in wildcard:
            print(f"   ❌ ERRO: 'implemented_in' não definido ou inválido no header.")
            errors += 1
            continue
            
        print(f"   Wildcard de implementação: {wildcard}")
        
        # Resolve o wildcard a partir da raiz do projeto
        search_pattern = str(root_dir / wildcard)
        matched_dirs = glob.glob(search_pattern, recursive=True)
        
        # Filtra apenas diretórios
        matched_dirs = [d for d in matched_dirs if os.path.isdir(d)]
        
        if not matched_dirs:
            print(f"   ❌ ERRO: Wildcard '{wildcard}' não encontrou nenhum diretório no código fonte.")
            errors += 1
            continue
            
        # Para cada diretório encontrado, verifica se tem regra-de-negocio.md
        for d in matched_dirs:
            rel_dir = Path(d).relative_to(root_dir)
            rule_file = Path(d) / "regra-de-negocio.md"
            if rule_file.exists():
                print(f"   ✅ OK (SdSFC respeitado): {rel_dir}/regra-de-negocio.md encontrado.")
            else:
                print(f"   ❌ ERRO SdSFC: O diretório {rel_dir} não possui regra-de-negocio.md!")
                errors += 1
                
    if errors > 0:
        print(f"\n❌ Validação Falhou. Encontrados {errors} erro(s) de SdSFC.")
        sys.exit(1)
    else:
        print(f"\n✅ Validação de SdSFC Passou! A documentação está sincronizada com o código.")
        sys.exit(0)

if __name__ == "__main__":
    print("=== DDD-Kit SdSFC Linter ===")
    validate()

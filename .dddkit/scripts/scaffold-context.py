import os
import sys
import shutil
import argparse
from pathlib import Path

def get_project_root():
    script_path = Path(__file__).resolve()
    return script_path.parent.parent.parent.parent

def main():
    parser = argparse.ArgumentParser(description='Scaffold DDD-Kit Context and Module')
    parser.add_argument('--context', required=True, help='Nome do Bounded Context (PascalCase)')
    parser.add_argument('--module', required=True, help='Nome do Módulo (kebab-case)')
    
    args = parser.parse_args()
    
    root = get_project_root()
    kit_dir = root / "specs" / "DDD-Kit"
    templates_dir = kit_dir / "templates"
    
    context_name = args.context
    module_name = args.module
    
    # Criar pasta do contexto e do modulo
    module_dir = kit_dir / "BoundedContexts" / context_name / module_name
    
    if module_dir.exists():
        print(f"❌ Erro: O módulo '{module_name}' já existe no contexto '{context_name}'.")
        sys.exit(1)
        
    os.makedirs(module_dir, exist_ok=True)
    
    # Copiar templates
    domain_tpl = templates_dir / "domain-template.md"
    vocab_tpl = templates_dir / "vocabulary-template.md"
    
    target_domain = module_dir / "domain.md"
    target_vocab = module_dir / "vocabulary.md"
    
    try:
        shutil.copy2(domain_tpl, target_domain)
        shutil.copy2(vocab_tpl, target_vocab)
        print(f"✅ Sucesso: Módulo '{module_name}' criado em {module_dir.relative_to(root)}")
        print(f"📝 Agora edite {target_domain.relative_to(root)} e {target_vocab.relative_to(root)}")
    except FileNotFoundError as e:
        print(f"❌ Erro: Arquivo de template não encontrado. Certifique-se de que {templates_dir.relative_to(root)} possui os templates.")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()

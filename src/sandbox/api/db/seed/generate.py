#!/usr/bin/env python3
"""Gerador determinístico do dataset do Domínio de Referência.

Mesmo perfil, mesmo seed, mesmos bytes — em qualquer máquina, em qualquer dia.
Nada aqui consulta o relógio: `created_at` deriva de um epoch fixo em
profiles.yaml. Um dataset que depende de "agora" torna dois runs separados por
uma semana incomparáveis sem que nada acuse.

Saída: TSV para COPY, mais manifest.json com contagens e sha256 por arquivo. O
`dataset_hash` é o que o Run grava para provar contra qual dataset ele mediu.

    python3 db/seed/generate.py --profile small --out /tmp/seed-small
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from array import array
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

ADJETIVOS = [
    "azure", "basalt", "cobalt", "dusky", "ember", "flinty", "gilded", "hazel",
    "ivory", "jade", "kelp", "lunar", "mauve", "nimbus", "onyx", "pearl",
    "quartz", "russet", "sable", "teal", "umber", "verdant", "wheat", "zinc",
]
SUBSTANTIVOS = [
    "anvil", "beacon", "cradle", "dial", "engine", "flask", "girder", "hinge",
    "ingot", "jigsaw", "kettle", "lantern", "mantle", "nozzle", "oar", "piston",
    "quiver", "ratchet", "spindle", "trellis", "urn", "valve", "wedge", "yoke",
]
CHAVES_ATTR = ["color", "size", "material", "origin", "finish", "grade", "pack", "warranty"]
VALORES_ATTR = ["red", "blue", "small", "large", "steel", "oak", "matte", "gloss",
                "eu", "us", "a", "b", "single", "dual", "12m", "24m"]
STATUS = ["pending", "paid", "shipped", "cancelled"]


def carregar_perfis() -> dict:
    caminho = RAIZ / "db" / "seed" / "profiles.yaml"
    try:
        import yaml
    except ImportError:
        raise SystemExit("pyyaml necessário: pip install pyyaml")
    return yaml.safe_load(caminho.read_text())


def escapar(valor: str) -> str:
    return valor.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")


def marca_tempo(base: datetime, rng: random.Random, janela_dias: int) -> str:
    delta = timedelta(milliseconds=rng.randrange(janela_dias * 86_400_000))
    return (base - delta).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def gerar(perfil: str, destino: Path) -> dict:
    perfis = carregar_perfis()
    if perfil not in perfis or perfil == "comum":
        raise SystemExit(f"perfil desconhecido: {perfil}")
    cfg, comum = perfis[perfil], perfis["comum"]

    epoch = datetime.fromisoformat(comum["epoch"].replace("Z", "+00:00")).astimezone(timezone.utc)
    janela = comum["janela_dias"]
    estoque = comum["estoque_por_produto"]
    min_itens, max_itens = comum["itens_por_pedido"]
    preco_min, preco_max = comum["preco_centavos"]

    rng = random.Random(cfg["seed"])
    destino.mkdir(parents=True, exist_ok=True)

    with (destino / "categories.tsv").open("w") as f:
        for i in range(1, cfg["categories"] + 1):
            f.write(f"{i}\t{escapar(SUBSTANTIVOS[i % len(SUBSTANTIVOS)])}-{i}\n")

    precos = array("i", bytes(4 * (cfg["products"] + 1)))
    with (destino / "products.tsv").open("w") as f:
        for i in range(1, cfg["products"] + 1):
            preco = rng.randrange(preco_min, preco_max)
            precos[i] = preco
            nome = (f"{ADJETIVOS[rng.randrange(len(ADJETIVOS))]} "
                    f"{SUBSTANTIVOS[rng.randrange(len(SUBSTANTIVOS))]} {i}")
            attrs = {CHAVES_ATTR[k]: VALORES_ATTR[rng.randrange(len(VALORES_ATTR))]
                     for k in range(rng.randrange(3, 9))}
            f.write("\t".join([
                str(i), f"SKU-{i:010d}", escapar(nome), str(preco), str(estoque),
                str(rng.randrange(1, cfg["categories"] + 1)),
                escapar(json.dumps(attrs, separators=(",", ":"), sort_keys=True)),
                marca_tempo(epoch, rng, janela),
            ]) + "\n")

    with (destino / "customers.tsv").open("w") as f:
        for i in range(1, cfg["customers"] + 1):
            nome = (f"{ADJETIVOS[rng.randrange(len(ADJETIVOS))]} "
                    f"{SUBSTANTIVOS[rng.randrange(len(SUBSTANTIVOS))]}")
            f.write(f"{i}\tcustomer{i}@lab.test\t{escapar(nome)}\t"
                    f"{marca_tempo(epoch, rng, janela)}\n")

    total_itens = 0
    with (destino / "orders.tsv").open("w") as fo, \
         (destino / "order_items.tsv").open("w") as fi:
        for pedido in range(1, cfg["orders"] + 1):
            quantos = min(rng.randrange(min_itens, max_itens + 1), cfg["products"])
            produtos = rng.sample(range(1, cfg["products"] + 1), quantos)
            total = 0
            for pid in sorted(produtos):
                qtd = rng.randrange(1, 6)
                total += qtd * precos[pid]
                fi.write(f"{pedido}\t{pid}\t{qtd}\t{precos[pid]}\n")
                total_itens += 1
            fo.write("\t".join([
                str(pedido), str(rng.randrange(1, cfg["customers"] + 1)),
                STATUS[rng.randrange(len(STATUS))], str(total),
                f"seed-{pedido}", marca_tempo(epoch, rng, janela),
            ]) + "\n")

    arquivos = {}
    for tsv in sorted(destino.glob("*.tsv")):
        h = hashlib.sha256()
        with tsv.open("rb") as f:
            for bloco in iter(lambda: f.read(1 << 20), b""):
                h.update(bloco)
        arquivos[tsv.name] = {"sha256": h.hexdigest(), "bytes": tsv.stat().st_size}

    manifesto = {
        "profile": perfil,
        "seed": cfg["seed"],
        "epoch": comum["epoch"],
        "counts": {
            "categories": cfg["categories"], "products": cfg["products"],
            "customers": cfg["customers"], "orders": cfg["orders"],
            "order_items": total_itens,
        },
        "files": arquivos,
    }
    manifesto["dataset_hash"] = hashlib.sha256(
        json.dumps(manifesto, sort_keys=True).encode()).hexdigest()[:16]
    (destino / "manifest.json").write_text(json.dumps(manifesto, indent=2) + "\n")
    return manifesto


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    m = gerar(args.profile, args.out)
    print(json.dumps(m["counts"]), "dataset_hash=" + m["dataset_hash"])

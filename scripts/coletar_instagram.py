#!/usr/bin/env python3
"""
Coleta dados do Instagram para análise de branding.
Execute na SUA máquina local com: python3 coletar_instagram.py
"""

import json
import os
import sys
from datetime import datetime

try:
    import instaloader
except ImportError:
    print("Instalando instaloader...")
    os.system(f"{sys.executable} -m pip install instaloader -q")
    import instaloader

PERFIS = [
    "grupobraco_",
    "colunasbrasil",
    "goyaco",
    "saojudas",
    "sks",
    "gerdau",
    "arcelormittal",
    "csn_oficial",
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "instagram")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def coletar_perfil(L, username):
    print(f"\n📥 Coletando @{username}...")
    try:
        profile = instaloader.Profile.from_username(L.context, username)

        posts = []
        count = 0
        for post in profile.get_posts():
            if count >= 12:
                break
            posts.append({
                "shortcode": post.shortcode,
                "tipo": "video" if post.is_video else ("carousel" if post.typename == "GraphSidecar" else "foto"),
                "legenda": (post.caption or "")[:300],
                "hashtags": list(post.caption_hashtags) if post.caption else [],
                "curtidas": post.likes,
                "comentarios": post.comments,
                "data": post.date_utc.strftime("%Y-%m-%d"),
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
            })
            count += 1

        data = {
            "coletado_em": datetime.now().isoformat(),
            "username": username,
            "nome": profile.full_name,
            "bio": profile.biography,
            "link_bio": profile.external_url or "",
            "seguidores": profile.followers,
            "seguindo": profile.followees,
            "posts_count": profile.mediacount,
            "categoria": profile.business_category_name or "",
            "is_business": profile.is_business_account,
            "is_verified": profile.is_verified,
            "highlights": [],
            "ultimos_posts": posts,
            "status": "ok",
        }

        print(f"   ✅ {profile.full_name} | {profile.followers:,} seguidores | {profile.mediacount} posts")
        return data

    except instaloader.exceptions.ProfileNotExistsException:
        print(f"   ❌ Perfil não encontrado")
        return {"username": username, "status": "não encontrado", "coletado_em": datetime.now().isoformat()}
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"   🔒 Perfil privado")
        return {"username": username, "status": "privado", "coletado_em": datetime.now().isoformat()}
    except Exception as e:
        print(f"   ⚠️  Erro: {e}")
        return {"username": username, "status": f"erro: {str(e)}", "coletado_em": datetime.now().isoformat()}


def main():
    print("=" * 50)
    print("  Coleta de dados Instagram — Marca Braço")
    print("=" * 50)

    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
        quiet=True,
    )

    # Login opcional — melhora acesso a dados privados
    login = input("\nDeseja fazer login no Instagram para melhor acesso? (s/N): ").strip().lower()
    if login == "s":
        usuario = input("Usuário Instagram: ").strip()
        senha = input("Senha: ").strip()
        try:
            L.login(usuario, senha)
            print("✅ Login realizado com sucesso!")
        except Exception as e:
            print(f"⚠️  Login falhou: {e} — continuando sem login")

    resultados = {}
    data_hoje = datetime.now().strftime("%Y-%m-%d")

    for username in PERFIS:
        dados = coletar_perfil(L, username)
        resultados[username] = dados

        # Salvar individualmente
        nome_arquivo = f"{data_hoje}_{username}.json"
        if username == "grupobraco_":
            caminho = os.path.join(OUTPUT_DIR, nome_arquivo)
        else:
            caminho_concorrente = os.path.join(os.path.dirname(__file__), "..", "data", "concorrentes")
            os.makedirs(caminho_concorrente, exist_ok=True)
            caminho = os.path.join(caminho_concorrente, nome_arquivo)

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"   💾 Salvo em: {caminho}")

    print("\n" + "=" * 50)
    print("✅ Coleta concluída!")
    print(f"   Perfis coletados: {len(resultados)}")
    print("   Agora rode Claude Code no projeto e peça a análise.")
    print("=" * 50)


if __name__ == "__main__":
    main()

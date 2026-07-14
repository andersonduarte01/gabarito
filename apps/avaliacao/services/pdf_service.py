"""
Geração de PDF de avaliação via Typst.
Compilação pura Python (typst-py embute o compilador Rust).
"""
import json
import pathlib
import shutil
import tempfile

import typst

_TEMPLATE = pathlib.Path(__file__).parent.parent / "assets" / "avaliacao.typ"


def gerar_pdf_avaliacao(avaliacao, escola) -> bytes:
    """Retorna os bytes do PDF da avaliação pronto para envio."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        payload = _serializar(avaliacao, escola, tmp)
        (tmp / "data.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )
        shutil.copy2(_TEMPLATE, tmp / "avaliacao.typ")
        return typst.compile(str(tmp / "avaliacao.typ"), root=str(tmp))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ── Serialização ──────────────────────────────────────────────────────

def _serializar(avaliacao, escola, tmp: pathlib.Path) -> dict:
    return {
        "escola":    _escola(escola, tmp),
        "avaliacao": _avaliacao(avaliacao),
        "questoes":  _questoes(avaliacao, tmp),
    }


def _copiar_media(src_path: str, tmp: pathlib.Path, nome: str) -> str | None:
    """Copia arquivo de mídia para o temp dir e retorna o nome relativo."""
    try:
        src = pathlib.Path(src_path)
        if src.is_file():
            dest = tmp / nome
            shutil.copy2(src, dest)
            return nome
    except Exception:
        pass
    return None


def _escola(escola, tmp: pathlib.Path) -> dict:
    logo_path = None
    if escola.logo:
        try:
            logo_path = _copiar_media(escola.logo.path, tmp, f"logo{pathlib.Path(escola.logo.name).suffix}")
        except Exception:
            pass
    return {"nome": escola.nome, "logo_path": logo_path}


def _avaliacao(av) -> dict:
    professor = None
    if av.professor:
        try:
            professor = av.professor.papel.vinculo.usuario.nome
        except Exception:
            pass

    return {
        "titulo":         av.titulo,
        "turma":          av.turma.nome,
        "materia":        av.materia.nome,
        "professor":      professor,
        "ano_letivo":     str(av.ano_letivo.ano),
        "periodo":        av.periodo_letivo.nome if av.periodo_letivo else "—",
        "data_aplicacao": (av.data_aplicacao.strftime("%d/%m/%Y")
                           if av.data_aplicacao else "—"),
        "nota_maxima":    str(av.nota_maxima),
    }


def _questoes(avaliacao, tmp: pathlib.Path) -> list:
    result = []
    for q in avaliacao.questoes.prefetch_related("opcoes").all():
        imagem_path = None
        if q.imagem:
            try:
                imagem_path = _copiar_media(
                    q.imagem.path, tmp,
                    f"q{q.numero}{pathlib.Path(q.imagem.name).suffix}"
                )
            except Exception:
                pass

        opcoes = [
            {"letra": op.letra, "texto": op.texto}
            for op in q.opcoes.all()
        ]

        result.append({
            "numero":      q.numero,
            "enunciado":   q.enunciado,
            "tipo":        q.tipo,
            "pontuacao":   float(q.pontuacao),
            "imagem_path": imagem_path,
            "opcoes":      opcoes,
        })
    return result

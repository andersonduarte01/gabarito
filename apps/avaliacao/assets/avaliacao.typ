// ════════════════════════════════════════════════════════════════════
//  EduCare — Template de Avaliação
// ════════════════════════════════════════════════════════════════════

#let d        = json("data.json")
#let escola   = d.escola
#let av       = d.avaliacao
#let questoes = d.questoes

#let azul        = rgb("#1e3a5f")
#let cinza       = rgb("#64748b")
#let cinza-borda = rgb("#e2e8f0")
#let cinza-linha = rgb("#b0bec5")
#let fundo       = rgb("#f8fafc")
#let texto       = rgb("#1e293b")

#set page(paper: "a4", margin: (x: 2.2cm, top: 1.7cm, bottom: 2.2cm))
#set text(size: 10.5pt, fill: texto, hyphenate: false)
#set par(leading: 0.55em, spacing: 0.7em)

// ── Helpers ──────────────────────────────────────────────────────────
#let meta-cel(rotulo, valor, negrito: false) = stack(
  spacing: 1.5pt,
  text(5.5pt, weight: "bold", fill: cinza, upper(rotulo)),
  if negrito { text(8.5pt, weight: "bold")[#valor] } else { text(8.5pt)[#valor] },
)

#let campo-aluno(rotulo, valor: "") = stack(
  spacing: 2pt,
  text(5.5pt, weight: "bold", fill: cinza, upper(rotulo)),
  stack(
    spacing: 2pt,
    text(8.5pt)[#if valor != "" { valor } else { " " }],
    line(length: 100%, stroke: 0.8pt + cinza-linha),
  ),
)

#let bolinha() = box(
  width: 14pt, height: 14pt, baseline: 3pt,
  place(center + horizon, circle(radius: 5.5pt, stroke: 1.2pt + cinza, fill: white)),
)

#let quadradinho(r: 2pt) = box(
  width: 14pt, height: 14pt, baseline: 3pt,
  place(center + horizon, rect(width: 11pt, height: 11pt, radius: r,
    stroke: 1.2pt + cinza, fill: white)),
)

#let linhas-resposta(n: 6) = {
  let itens = range(n).map(_ =>
    block(height: 8mm, width: 100%, above: 0pt, below: 0pt,
      place(bottom, line(length: 100%, stroke: 0.8pt + cinza-linha))
    )
  )
  stack(spacing: 0pt, ..itens)
}

#let caixa-numerica() = rect(
  width: 4.5cm, height: 1.1cm,
  stroke: 1pt + cinza-linha, radius: 3pt, fill: white,
)

// ════════════════════════════════════════════════════════════════════
//  CABEÇALHO
// ════════════════════════════════════════════════════════════════════
#grid(
  columns: (auto, 1fr),
  column-gutter: 10pt,
  align: horizon,
  if escola.logo_path != none {
    image(escola.logo_path, width: 1.2cm, height: 1.2cm, fit: "contain")
  } else {
    box(
      width: 1.2cm, height: 1.2cm, fill: azul, radius: 4pt,
      align(center + horizon,
        text(18pt, weight: "bold", fill: white,
          upper(escola.nome.clusters().first()))
      )
    )
  },
  stack(
    spacing: 1.5pt,
    text(12pt, weight: "bold", fill: azul)[#escola.nome],
    text(7.5pt, fill: cinza)[Ensino Fundamental — Avaliação Presencial],
  ),
)
#v(4pt)
#line(length: 100%, stroke: 1.5pt + azul)
#v(6pt)

// ════════════════════════════════════════════════════════════════════
//  TÍTULO + METADADOS + IDENTIFICAÇÃO — em linha única compacta
// ════════════════════════════════════════════════════════════════════

// Título
#align(center)[
  #text(12pt, weight: "bold")[#upper(av.titulo)]
  #v(2pt)
  #text(8pt, fill: cinza)[#av.turma #h(4pt)#sym.bullet#h(4pt)#av.materia]
]
#v(6pt)

// Metadados
#block(
  fill: fundo, stroke: 0.4pt + cinza-borda, radius: 3pt,
  width: 100%, inset: (x: 9pt, y: 6pt),
)[
  #if av.professor != none [
    #grid(
      columns: (auto, 1fr), column-gutter: 5pt, align: horizon,
      text(5.5pt, weight: "bold", fill: cinza, "PROFESSOR(A)"),
      text(8.5pt)[#av.professor],
    )
    #v(4pt)
    #line(length: 100%, stroke: 0.3pt + cinza-borda)
    #v(4pt)
  ]
  #grid(
    columns: (1fr, 1fr, 1fr, auto), column-gutter: 8pt,
    meta-cel("Ano Letivo",        av.ano_letivo),
    meta-cel("Período",           av.periodo),
    meta-cel("Data de Aplicação", av.data_aplicacao),
    meta-cel("Nota Máxima",       av.nota_maxima, negrito: true),
  )
]
#v(6pt)

// Identificação do aluno
#block(stroke: 0.4pt + cinza-borda, radius: 3pt, width: 100%, clip: true)[
  #block(fill: azul, width: 100%, inset: (x: 9pt, y: 3.5pt),
    text(6.5pt, weight: "bold", fill: white, tracking: 0.5pt,
      "IDENTIFICAÇÃO DO(A) ALUNO(A)")
  )
  #block(inset: (x: 9pt, y: 6pt))[
    #grid(
      columns: (1fr, 0.32fr, 0.36fr), column-gutter: 10pt,
      campo-aluno("Nome Completo"),
      campo-aluno("Turma", valor: av.turma),
      campo-aluno("Data de Aplicação",
        valor: if av.data_aplicacao != "—" { av.data_aplicacao } else { "" }),
    )
  ]
]
#v(12pt)

// ════════════════════════════════════════════════════════════════════
//  QUESTÕES
// ════════════════════════════════════════════════════════════════════
#line(length: 100%, stroke: 0.4pt + cinza-borda)
#v(4pt)
#text(6.5pt, weight: "bold", fill: cinza, tracking: 1pt, "Q U E S T Õ E S")
#v(8pt)

#if questoes.len() == 0 [
  #align(center, text(9.5pt, fill: cinza-linha)[Nenhuma questão cadastrada.])
] else {
  for (i, q) in questoes.enumerate() {
    let tipo = q.tipo

    let area = if tipo == "MULTIPLA_ESCOLHA" or tipo == "MULTIPLAS_RESPOSTAS" {
      // Letra) ○ Texto
      pad(left: 0.65cm, stack(
        spacing: 5pt,
        ..q.opcoes.map(op => grid(
          columns: (0.45cm, auto, 1fr), column-gutter: 5pt, align: horizon,
          text(10pt, weight: "bold", fill: azul)[#op.letra)],
          bolinha(),
          text(10pt)[#op.texto],
        ))
      ))
    } else if tipo == "VERDADEIRO_FALSO" {
      // Verticalmente empilhado
      pad(left: 0.65cm, stack(
        spacing: 6pt,
        grid(columns: (auto, auto), column-gutter: 6pt, align: horizon,
          quadradinho(), text(10pt)[Verdadeiro]),
        grid(columns: (auto, auto), column-gutter: 6pt, align: horizon,
          quadradinho(), text(10pt)[Falso]),
      ))
    } else if tipo == "ORDENACAO" {
      // Caixa maior para escrever o número da ordem
      pad(left: 0.65cm, stack(
        spacing: 6pt,
        ..q.opcoes.map(op => grid(
          columns: (1.4cm, 1fr), column-gutter: 8pt, align: horizon,
          rect(width: 1.2cm, height: 0.65cm, radius: 3pt,
            stroke: 1pt + cinza-linha, fill: white),
          text(10pt)[#op.texto],
        ))
      ))
    } else if tipo == "NUMERICA" {
      // Só uma linha, sem label
      pad(left: 0.65cm, linhas-resposta(n: 1))
    } else if tipo == "RESPOSTA_CURTA" {
      // Só uma linha, sem label
      pad(left: 0.65cm, linhas-resposta(n: 1))
    } else if tipo == "LACUNAS" {
      none
    } else if tipo == "ASSOCIACAO" {
      // Coluna A: número + texto  |  Coluna B: caixinha vazia + letra) + texto
      // Opcoes com letra numérica ("1","2"...) → Coluna A
      // Opcoes com letra alfabética ("a","b"...) → Coluna B
      pad(left: 0.65cm, {
        let col-a = q.opcoes.filter(op => op.letra.match(regex("^[0-9]+$")) != none)
        let col-b = q.opcoes.filter(op => op.letra.match(regex("^[a-zA-Z]+$")) != none)
        let n = calc.max(col-a.len(), col-b.len(), 4)

        let caixinha() = rect(
          width: 0.7cm, height: 0.6cm,
          stroke: 0.8pt + cinza-linha, radius: 2pt, fill: white,
        )

        let rows = ()
        for k in range(n) {
          // célula Coluna A
          let ca = if k < col-a.len() {
            let op = col-a.at(k)
            grid(columns: (auto, 1fr), column-gutter: 5pt, align: horizon,
              text(10pt, weight: "bold")[#op.letra.],
              text(10pt)[#op.texto],
            )
          } else { [] }

          // célula Coluna B
          let cb = if k < col-b.len() {
            let op = col-b.at(k)
            grid(columns: (auto, auto, 1fr), column-gutter: 5pt, align: horizon,
              caixinha(),
              text(10pt, weight: "bold")[#op.letra)],
              text(10pt)[#op.texto],
            )
          } else { [] }

          rows += (ca, cb)
        }

        grid(
          columns: (1fr, 1fr),
          column-gutter: 18pt,
          row-gutter: 7pt,
          align: left + horizon,
          ..rows,
        )
      })
    } else {
      pad(left: 0.65cm, linhas-resposta(n: 7))
    }

    block(breakable: false)[
      #grid(
        columns: (0.65cm, 1fr, 1.7cm),
        text(10.5pt, weight: "bold", fill: azul)[#q.numero.],
        text(10.5pt)[#q.enunciado],
        align(right, text(8.5pt, style: "italic", fill: cinza)[
          #q.pontuacao pt#if q.pontuacao != 1 [s]
        ]),
      )
      #if q.imagem_path != none [
        #v(5pt)
        #pad(left: 0.65cm, image(q.imagem_path, height: 6cm, fit: "contain"))
      ]
      #v(6pt)
      #area
    ]

    if i < questoes.len() - 1 {
      v(8pt)
      line(length: 100%, stroke: (paint: cinza-borda, dash: "dashed", thickness: 0.5pt))
      v(10pt)
    }
  }
}

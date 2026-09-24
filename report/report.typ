
#import "@preview/tablex:0.0.9": hlinex, tablex, vlinex // optional, for fancier tables
#import "@preview/datify:1.0.1": custom-date-format

#let coursename = "Course name h"
#let reporttype = "Report type h"
#let report-title = "Report title h"
#let advisor = "Advisor h"
#let students = (
  ("Student 1", "ID 1"),
  ("Student 2", "ID 2"),
  ("Student 3", "ID 3"),
)

// Cover page
#let cover-page() = {
  set page(numbering: none)
  set align(center)

  text(size: 1em)[
    #upper[VIETNAM NATIONAL UNIVERSITY HO CHI MINH CITY] \
    #upper[HO CHI MINH CITY UNIVERSITY OF TECHNOLOGY ] \
    #upper[Faculty of Computer Science and Engineering] \
  ]

  v(2em)
  image("images/hcmut-logo.webp", width: 5cm)

  v(2em)
  text(size: 1.3em, weight: "bold")[#coursename]

  v(0.5em)
  line(length: 80%)
  v(2em)

  text(size: 1.3em, weight: "bold")[#reporttype]
  v(1em)
  text(size: 2em, weight: "bold")[#report-title]

  line(length: 80%, stroke: .12em)
  v(2em)

  align(left)[
    #set align(center)
    #table(
      columns: 3,
      stroke: none,
      column-gutter: 1em,
      align: left,
      [Advisor:], [#advisor], [],
      ..students
        .enumerate()
        .map(((i, s)) => (
          if i == 0 [Student] else [],
          s.at(0),
          s.at(1),
        ))
        .flatten(),
    )
  ]

  v(1fr)
  upper[Ho Chi Minh City,
    #custom-date-format(
      datetime.today(),
      pattern: "dd MMMM yyyy",
      lang: "en",
    )]
  v(1fr)
  pagebreak()
}

// General page / text setup
#let conf(doc) = {
  set document(title: report-title)
  set page(
    paper: "a4",
    margin: (top: 2.5cm, bottom: 2.5cm, left: 3cm, right: 2cm),
    numbering: "1",
    footer: context {
      set align(center)
      set text(size: .9em)
      [
        #counter(page).get().first() / #counter(page).final().first()
      ]
    },
  )
  set text(font: "New Computer Modern", size: 12pt, lang: "en")
  set heading(numbering: "I.1")
  set par(justify: true)

  set figure(numbering: "1.a")

  doc
}

#show: conf

#cover-page()
#outline(title: "Table of Contents", indent: auto)
#pagebreak()

= Introduction
// presentation of the project

= Software structure

= Shape Generators

= Shaders

= GUI
// explain user interface choices and navigation

= Performance


#pagebreak()
#outline(title: "List of Figures", target: figure.where(kind: image))

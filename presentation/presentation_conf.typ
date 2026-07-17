#import "@preview/touying:0.6.1": *

#let ink = rgb("#1B1F1C")
#let muted = rgb("#6E7A70")
#let rule-color = rgb("#D3DCD5")
#let zebra = rgb("#F2F5F2")
#let accent = rgb("#B4552F")


#let title-slide(subtitle: none, ..args) = touying-slide-wrapper(
	self => {
		let info = self.info + args.named()

		let body = {
			set align(left + horizon)
			block(width: 100%, inset: (x: 1.2em))[
				#block(height: 4pt, width: 3.5em, fill: self.colors.primary)
				#v(0.9em)
				#text(size: 2.05em, weight: "bold", fill: self.colors.primary-dark, info.title)
				#if subtitle != none {
					v(0.4em)
					text(size: 1.05em, fill: muted, subtitle)
				}
				#v(1.4em)
				#line(length: 100%, stroke: 0.6pt + rule-color)
				#v(0.7em)
				#text(size: 1em, fill: ink, weight: "medium", info.author)
				#h(1fr)
				#text(size: 0.9em, fill: muted, utils.display-info-date(self))
			]
		}

		touying-slide(self: utils.merge-dicts(self, (freeze-slide-counter: true)), body)
	}
)


#let slide(title: auto, body) = touying-slide-wrapper(
	self => {
	  	let header-content = {
			set align(top)
			show: components.cell.with(fill: self.colors.primary, inset: (x: 1.15em, y: 0.75em))
			set align(horizon + left)
			set text(fill: self.colors.neutral-lightest, size: 1.35em, weight: "bold")
			if title != auto {
			  	utils.call-or-display(self, title)
			} else {
			  	utils.display-current-heading(level: 2)
			}
		}

	  	let footer-content = {
			set align(bottom)
			block(width: 100%, inset: (x: 1.15em, bottom: 0.7em))[
				#line(length: 100%, stroke: 0.6pt + rule-color)
				#v(0.35em)
				#set text(fill: muted, size: 0.62em)
				#utils.call-or-display(self, self.info.title)
				#h(1fr)
				#utils.call-or-display(self, self.info.author)
				#h(1.2em)
				#context { utils.slide-counter.display() + " / " + utils.last-slide-number }
			]
  		}

		let conf = config-page(header: header-content, footer: footer-content)
	  	touying-slide(self: utils.merge-dicts(self, conf), align(horizon, body))
	}
)


#let new-section-slide(self: none, body) = touying-slide-wrapper(
	self => {
		let main-body = {
			set align(center + horizon)
			set text(size: 2.3em, fill: self.colors.primary, weight: "bold")
			utils.display-current-heading(level: 1)
		}
		touying-slide(self: self, main-body)
	}
)


#let focus-slide(body) = touying-slide-wrapper(
	self => {
		let config = config-page(fill: self.colors.primary-dark, margin: 2.3em, header: none, footer: none)
		let main-body = {
			set align(horizon + center)
			set text(fill: self.colors.neutral-lightest, size: 2.4em, weight: "bold")
			body
			v(0.5em)
			line(length: 3.5em, stroke: 3pt + self.colors.primary)
		}
		touying-slide(
			self: utils.merge-dicts(self, config, (freeze-slide-counter: true)),
			main-body,
		)
	}
)


#let bamboo-theme(aspect-ratio: "16-9", ..args, body) = {
	show: touying-slides.with(
		config-page(
			paper: "presentation-" + aspect-ratio,
			margin: (top: 3.5em, bottom: 2.2em, x: 1.6em),
		),
		config-colors(
			primary: rgb("#5E8B65"),
			primary-dark: rgb("#2F4E37"),
			neutral-lightest: rgb("#ffffff"),
			neutral-darkest: ink,
		),
		config-methods(alert: (self: none, it) => text(fill: accent, weight: "bold", it)),
		config-common(
			slide-fn: slide,
			new-section-slide-fn: new-section-slide
		),
		config-info(..args)
    )

	set text(size: 18pt, font: "Lato", fill: ink)
	show raw: set text(font: "Fira Mono", size: 0.92em)
	set list(spacing: 0.7em, marker: text(fill: rgb("#5E8B65"), sym.bullet))
	set enum(spacing: 0.7em)
	set par(leading: 0.62em)

	// Tables: filled header row, zebra body, no interior rules.
	set table(
		inset: (x: 8pt, y: 6pt),
		align: left + horizon,
		stroke: none,
		fill: (_, y) => if y == 0 { rgb("#5E8B65") } else if calc.even(y) { zebra } else { white },
	)
	show table.cell.where(y: 0): set text(fill: white, weight: "bold")

	// Figures on slides are illustrations, not numbered exhibits.
	set figure(numbering: none, supplement: none)
	show figure.caption: it => text(size: 0.72em, fill: muted, it.body)

	body
}

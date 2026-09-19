// Package generator builds candidate domain names (label + TLD) out of
// keyword lists, prefixes and suffixes.
package generator

import (
	"strings"

	"domainscraper/internal/keywords"
)

// Options controls how candidate labels are generated.
type Options struct {
	Categories     []string // category names to include; empty = all
	IncludePlain   bool     // keyword alone (e.g. "music")
	IncludePrefix  bool     // prefix+keyword (e.g. "getmusic")
	IncludeSuffix  bool     // keyword+suffix (e.g. "musichub")
	IncludeDouble  bool     // keyword+keyword across two categories (e.g. "rockfood")
	MaxLabelLength int      // 0 = unlimited
}

// DefaultOptions returns sane defaults that keep the candidate count large
// but manageable.
func DefaultOptions() Options {
	return Options{
		IncludePlain:   true,
		IncludePrefix:  true,
		IncludeSuffix:  true,
		IncludeDouble:  false,
		MaxLabelLength: 63,
	}
}

func selectCategories(names []string) []keywords.Category {
	if len(names) == 0 {
		return keywords.Categories
	}
	set := make(map[string]bool, len(names))
	for _, n := range names {
		set[strings.ToLower(n)] = true
	}
	var out []keywords.Category
	for _, c := range keywords.Categories {
		if set[strings.ToLower(c.Name)] {
			out = append(out, c)
		}
	}
	return out
}

// Labels generates unique domain labels (without TLD) according to opts.
func Labels(opts Options) []string {
	cats := selectCategories(opts.Categories)

	seen := make(map[string]bool)
	var out []string

	add := func(s string) {
		s = strings.ToLower(s)
		if s == "" {
			return
		}
		if opts.MaxLabelLength > 0 && len(s) > opts.MaxLabelLength {
			return
		}
		if !seen[s] {
			seen[s] = true
			out = append(out, s)
		}
	}

	var words []string
	for _, c := range cats {
		words = append(words, c.Words...)
	}

	for _, w := range words {
		if opts.IncludePlain {
			add(w)
		}
		if opts.IncludePrefix {
			for _, p := range keywords.Prefixes {
				add(p + w)
			}
		}
		if opts.IncludeSuffix {
			for _, s := range keywords.Suffixes {
				add(w + s)
			}
		}
	}

	if opts.IncludeDouble {
		for i, w1 := range words {
			for j, w2 := range words {
				if i == j {
					continue
				}
				add(w1 + w2)
			}
		}
	}

	return out
}

// Domains combines labels with the given TLDs, producing fully qualified
// domain name candidates (e.g. "musichub.com").
func Domains(labels []string, tlds []string) []string {
	out := make([]string, 0, len(labels)*len(tlds))
	for _, l := range labels {
		for _, t := range tlds {
			t = strings.TrimPrefix(t, ".")
			out = append(out, l+"."+t)
		}
	}
	return out
}

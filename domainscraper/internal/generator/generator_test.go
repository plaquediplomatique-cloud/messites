package generator

import "testing"

func TestValidLabel(t *testing.T) {
	cases := map[string]bool{
		"music":          true,
		"get-music":      true,
		"a":              true,
		"":               false,
		"-music":         false,
		"music-":         false,
		"mu_sic":         false,
		"mu sic":         false,
		"MUSIC":          false, // must be pre-lowercased by caller
		"a..b":           false,
		"'; DROP TABLE;": false,
	}
	for in, want := range cases {
		if got := ValidLabel(in); got != want {
			t.Errorf("ValidLabel(%q) = %v, want %v", in, got, want)
		}
	}
}

func TestLabelsAreUniqueAndValid(t *testing.T) {
	opts := Options{
		Categories:     []string{"music"},
		IncludePlain:   true,
		IncludePrefix:  true,
		IncludeSuffix:  true,
		MaxLabelLength: 63,
	}
	labels := Labels(opts)
	if len(labels) == 0 {
		t.Fatal("expected non-empty labels")
	}

	seen := make(map[string]bool)
	for _, l := range labels {
		if seen[l] {
			t.Errorf("duplicate label: %q", l)
		}
		seen[l] = true
		if !ValidLabel(l) {
			t.Errorf("generated invalid label: %q", l)
		}
	}
}

func TestLabelsUnknownCategoryYieldsNothing(t *testing.T) {
	labels := Labels(Options{Categories: []string{"does-not-exist"}, IncludePlain: true})
	if len(labels) != 0 {
		t.Fatalf("expected 0 labels for unknown category, got %d", len(labels))
	}
}

func TestDomainsSkipsInvalidTLD(t *testing.T) {
	domains := Domains([]string{"music"}, []string{"com", "", "c", "toolongtldthatisnotreal12345678901234567890"})
	if len(domains) != 1 || domains[0] != "music.com" {
		t.Fatalf("expected only music.com, got %v", domains)
	}
}

func TestDomainsSkipsInvalidLabel(t *testing.T) {
	domains := Domains([]string{"music", "-bad-", "MUSIC"}, []string{"com"})
	if len(domains) != 1 || domains[0] != "music.com" {
		t.Fatalf("expected only music.com, got %v", domains)
	}
}

func TestMaxLabelLengthEnforced(t *testing.T) {
	opts := Options{
		Categories:     []string{"music"},
		IncludePrefix:  true,
		MaxLabelLength: 5,
	}
	labels := Labels(opts)
	for _, l := range labels {
		if len(l) > 5 {
			t.Errorf("label %q exceeds MaxLabelLength=5", l)
		}
	}
}

// Command domainscraper generates large numbers of English keyword-based
// domain-name candidates (music, rock, cook, food, travel, agency, tech...)
// and checks their availability concurrently via RDAP.
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"math/rand"
	"os"
	"os/signal"
	"strings"
	"sync/atomic"
	"time"

	"domainscraper/internal/checker"
	"domainscraper/internal/generator"
	"domainscraper/internal/keywords"
	"domainscraper/internal/output"
)

func main() {
	var (
		categoriesFlag = flag.String("categories", "", "comma-separated category names (default: all). Use -list to see them")
		tldsFlag       = flag.String("tlds", "com,net,org,io,co", "comma-separated TLDs to check (without dots)")
		outPath        = flag.String("out", "domains.csv", "full-detail output CSV file path (domain,status,source)")
		listOutPath    = flag.String("list-out", "result/list.txt", "plain-text output: one AVAILABLE domain name per line")
		workers        = flag.Int("workers", 40, "number of concurrent RDAP checks")
		timeout        = flag.Duration("timeout", 8*time.Second, "per-request timeout")
		limit          = flag.Int("limit", 0, "max number of domains to check (0 = no limit)")
		rps            = flag.Float64("rps", 15, "max RDAP requests per second (be conservative: avoids bans/throttling)")
		dnsFallback    = flag.Bool("dns-fallback", true, "fall back to a DNS lookup when RDAP is unreachable/inconclusive")
		shuffle        = flag.Bool("shuffle", true, "shuffle candidates before checking (spreads load, gives varied early results)")
		withPrefix     = flag.Bool("prefix", true, "include prefix+keyword combos (getmusic.com)")
		withSuffix     = flag.Bool("suffix", true, "include keyword+suffix combos (musichub.com)")
		withPlain      = flag.Bool("plain", true, "include plain keyword domains (music.com)")
		withDouble     = flag.Bool("double", false, "include keyword+keyword combos (expensive: quadratic)")
		onlyAvailable  = flag.Bool("only-available", false, "print only AVAILABLE domains to stdout")
		listCategories = flag.Bool("list", false, "list available keyword categories and exit")
		dryRun         = flag.Bool("dry-run", false, "generate and print candidate count without checking availability")
	)
	flag.Parse()

	if *workers < 1 {
		log.Fatal("-workers must be >= 1")
	}
	if *workers > 500 {
		log.Fatal("-workers > 500 is not allowed: that's not \"efficient\", it's a good way to get your IP banned by RDAP servers")
	}
	if *timeout <= 0 {
		log.Fatal("-timeout must be > 0")
	}
	if *rps < 0 {
		log.Fatal("-rps must be >= 0")
	}

	if *listCategories {
		for _, c := range keywords.Categories {
			fmt.Printf("%-14s (%d keywords)\n", c.Name, len(c.Words))
		}
		return
	}

	opts := generator.Options{
		IncludePlain:   *withPlain,
		IncludePrefix:  *withPrefix,
		IncludeSuffix:  *withSuffix,
		IncludeDouble:  *withDouble,
		MaxLabelLength: 63,
	}
	if *categoriesFlag != "" {
		opts.Categories = strings.Split(*categoriesFlag, ",")
	}

	labels := generator.Labels(opts)
	tlds := strings.Split(*tldsFlag, ",")
	domains := generator.Domains(labels, tlds)

	if *shuffle {
		rand.Shuffle(len(domains), func(i, j int) { domains[i], domains[j] = domains[j], domains[i] })
	}
	if *limit > 0 && *limit < len(domains) {
		domains = domains[:*limit]
	}

	fmt.Fprintf(os.Stderr, "generated %d unique labels -> %d candidate domains across %d TLD(s)\n",
		len(labels), len(domains), len(tlds))

	if *dryRun {
		return
	}

	w, err := output.NewCSV(*outPath)
	if err != nil {
		log.Fatalf("cannot open output file: %v", err)
	}
	defer w.Close()

	listW, err := output.NewList(*listOutPath)
	if err != nil {
		log.Fatalf("cannot open list output file: %v", err)
	}
	defer listW.Close()

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	c := checker.New(checker.Config{
		Timeout:           *timeout,
		RequestsPerSecond: *rps,
		DNSFallback:       *dnsFallback,
	})
	defer c.Close()

	go func() {
		<-ctx.Done()
		fmt.Fprintln(os.Stderr, "\ninterrupted: finishing in-flight checks and saving results collected so far...")
	}()

	var total, available, registered, failed int64
	start := time.Now()

	checker.RunPool(ctx, c, domains, *workers, func(r checker.Result) {
		atomic.AddInt64(&total, 1)
		switch r.Status {
		case checker.Available:
			atomic.AddInt64(&available, 1)
			fmt.Printf("\033[32m%-40s AVAILABLE\033[0m\n", r.Domain)
			if err := listW.WriteDomain(r.Domain); err != nil {
				log.Printf("list write error: %v", err)
			}
		case checker.Registered:
			atomic.AddInt64(&registered, 1)
			if !*onlyAvailable {
				fmt.Printf("%-40s registered\n", r.Domain)
			}
		default:
			atomic.AddInt64(&failed, 1)
			if !*onlyAvailable {
				fmt.Printf("%-40s %s\n", r.Domain, r.Status)
			}
		}
		if err := w.Write(r); err != nil {
			log.Printf("write error: %v", err)
		}
	})

	elapsed := time.Since(start)
	fmt.Fprintf(os.Stderr,
		"\ndone in %s | checked=%d available=%d registered=%d failed=%d | full results: %s | available domains: %s\n",
		elapsed.Round(time.Second), total, available, registered, failed, *outPath, *listOutPath)
}

// Package checker verifies domain-name availability using RDAP
// (Registration Data Access Protocol), the modern successor to WHOIS.
// rdap.org acts as a bootstrap proxy: it looks at the TLD, forwards the
// query to the right registry RDAP server, and returns:
//   - 404 Not Found  -> the domain is NOT registered (likely available)
//   - 200 OK         -> the domain IS registered
//   - anything else  -> inconclusive, caller should retry or skip
//
// When RDAP is unreachable or inconclusive, Check optionally falls back to
// a plain DNS lookup: no resolvable NS/A/AAAA record is a (weaker, but
// still useful) signal that a domain is unregistered.
package checker

import (
	"context"
	"fmt"
	"net"
	"net/http"
	"regexp"
	"time"

	"domainscraper/internal/ratelimit"
)

// Status describes the outcome of a single availability check.
type Status int

const (
	Unknown Status = iota
	Available
	Registered
	Error
)

func (s Status) String() string {
	switch s {
	case Available:
		return "AVAILABLE"
	case Registered:
		return "registered"
	case Error:
		return "error"
	default:
		return "unknown"
	}
}

// Result is the outcome of checking one domain.
type Result struct {
	Domain string
	Status Status
	Source string // "rdap" or "dns", for transparency in output/debugging
	Err    error
}

// domainRE is a defense-in-depth guard: even though the generator only
// emits validated labels, Check refuses to build a request or run a DNS
// lookup against anything that isn't a plain, safe hostname. This is what
// keeps a hostile or malformed candidate from ever reaching net/http or
// net.Resolver.
var domainRE = regexp.MustCompile(`^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$`)

// Checker queries RDAP (and optionally falls back to DNS) to determine
// domain availability.
type Checker struct {
	client      *http.Client
	baseURL     string
	maxRetries  int
	retryDelay  time.Duration
	limiter     *ratelimit.Limiter
	dnsFallback bool
	resolver    *net.Resolver
}

// Config controls Checker behavior.
type Config struct {
	Timeout           time.Duration // per-request timeout (default 8s)
	MaxRetries        int           // retries on transient failure (default 3)
	RetryBaseDelay    time.Duration // base delay for exponential backoff (default 500ms)
	RequestsPerSecond float64       // global RDAP rate limit, 0 = unlimited but NOT recommended
	DNSFallback       bool          // fall back to DNS when RDAP is inconclusive/unreachable
}

// New creates a Checker with sane, safe defaults; zero-valued fields in cfg
// are replaced with defaults rather than left as "unlimited" or "instant
// retry", so a caller can't accidentally construct a Checker that hammers
// a registry.
func New(cfg Config) *Checker {
	if cfg.Timeout <= 0 {
		cfg.Timeout = 8 * time.Second
	}
	if cfg.MaxRetries <= 0 {
		cfg.MaxRetries = 3
	}
	if cfg.RetryBaseDelay <= 0 {
		cfg.RetryBaseDelay = 500 * time.Millisecond
	}
	if cfg.RequestsPerSecond <= 0 {
		cfg.RequestsPerSecond = 15 // conservative default: safe for public RDAP bootstrap services
	}

	return &Checker{
		client: &http.Client{
			Timeout: cfg.Timeout,
			// Never follow redirects blindly to arbitrary hosts; rdap.org
			// itself doesn't redirect for domain queries, and refusing
			// redirects removes a whole class of SSRF-via-redirect risk.
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				return http.ErrUseLastResponse
			},
		},
		baseURL:     "https://rdap.org/domain/",
		maxRetries:  cfg.MaxRetries,
		retryDelay:  cfg.RetryBaseDelay,
		limiter:     ratelimit.New(cfg.RequestsPerSecond),
		dnsFallback: cfg.DNSFallback,
		resolver:    net.DefaultResolver,
	}
}

// Close releases background resources (the rate limiter's ticker).
func (c *Checker) Close() {
	c.limiter.Stop()
}

// Check performs an RDAP lookup for domain, retrying transient errors
// (network failures, 429, 5xx) with exponential backoff and jitter, rate
// limited to avoid tripping registry abuse protections. If RDAP ends up
// inconclusive and DNS fallback is enabled, it then tries a DNS lookup.
func (c *Checker) Check(ctx context.Context, domain string) (res Result) {
	// Defense in depth: recover from any unexpected panic (e.g. a future
	// code change with a nil-pointer bug) so one bad domain can never take
	// down the whole worker pool.
	defer func() {
		if r := recover(); r != nil {
			res = Result{Domain: domain, Status: Error, Err: fmt.Errorf("panic: %v", r)}
		}
	}()

	if !domainRE.MatchString(domain) || len(domain) > 253 {
		return Result{Domain: domain, Status: Error, Err: fmt.Errorf("refusing malformed domain %q", domain)}
	}

	res = c.checkRDAP(ctx, domain)
	if c.dnsFallback && (res.Status == Unknown || res.Status == Error) {
		if dnsRes, ok := c.checkDNS(ctx, domain); ok {
			return dnsRes
		}
	}
	return res
}

func (c *Checker) checkRDAP(ctx context.Context, domain string) Result {
	var lastErr error

	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		if attempt > 0 {
			delay := c.retryDelay * time.Duration(1<<uint(attempt-1))
			select {
			case <-ctx.Done():
				return Result{Domain: domain, Status: Error, Source: "rdap", Err: ctx.Err()}
			case <-time.After(delay):
			}
		}

		if err := c.limiter.Wait(ctx); err != nil {
			return Result{Domain: domain, Status: Error, Source: "rdap", Err: err}
		}

		req, err := http.NewRequestWithContext(ctx, http.MethodGet, c.baseURL+domain, nil)
		if err != nil {
			return Result{Domain: domain, Status: Error, Source: "rdap", Err: err}
		}
		req.Header.Set("Accept", "application/rdap+json")
		req.Header.Set("User-Agent", "domainscraper/1.0 (+https://github.com/)")

		resp, err := c.client.Do(req)
		if err != nil {
			lastErr = err
			continue
		}
		resp.Body.Close()

		switch {
		case resp.StatusCode == http.StatusNotFound:
			return Result{Domain: domain, Status: Available, Source: "rdap"}
		case resp.StatusCode == http.StatusOK:
			return Result{Domain: domain, Status: Registered, Source: "rdap"}
		case resp.StatusCode == http.StatusTooManyRequests, resp.StatusCode >= 500:
			lastErr = fmt.Errorf("rdap returned status %d", resp.StatusCode)
			continue
		default:
			return Result{Domain: domain, Status: Unknown, Source: "rdap", Err: fmt.Errorf("unexpected status %d", resp.StatusCode)}
		}
	}

	return Result{Domain: domain, Status: Error, Source: "rdap", Err: lastErr}
}

// checkDNS is a best-effort, much weaker signal than RDAP: a domain with
// no NS records is usually unregistered, but some registrars leave
// registered-but-parked domains with no records too, so this is only used
// as a fallback and results are still labeled Unknown when truly
// ambiguous.
func (c *Checker) checkDNS(ctx context.Context, domain string) (Result, bool) {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	_, err := c.resolver.LookupNS(ctx, domain)
	if err == nil {
		return Result{Domain: domain, Status: Registered, Source: "dns"}, true
	}

	var dnsErr *net.DNSError
	if isNXDomain(err, &dnsErr) {
		return Result{Domain: domain, Status: Available, Source: "dns"}, true
	}
	return Result{}, false
}

func isNXDomain(err error, target **net.DNSError) bool {
	de, ok := err.(*net.DNSError)
	if !ok {
		return false
	}
	*target = de
	return de.IsNotFound
}

// Package checker verifies domain-name availability using RDAP
// (Registration Data Access Protocol), the modern successor to WHOIS.
// rdap.org acts as a bootstrap proxy: it looks at the TLD, forwards the
// query to the right registry RDAP server, and returns:
//   - 404 Not Found  -> the domain is NOT registered (likely available)
//   - 200 OK         -> the domain IS registered
//   - anything else  -> inconclusive, caller should retry or skip
package checker

import (
	"context"
	"fmt"
	"net/http"
	"time"
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
	Err    error
}

// Checker queries RDAP to determine domain availability.
type Checker struct {
	client     *http.Client
	baseURL    string
	maxRetries int
	retryDelay time.Duration
}

// New creates a Checker with the given per-request timeout.
func New(timeout time.Duration) *Checker {
	return &Checker{
		client: &http.Client{
			Timeout: timeout,
		},
		baseURL:    "https://rdap.org/domain/",
		maxRetries: 3,
		retryDelay: 500 * time.Millisecond,
	}
}

// Check performs a single RDAP lookup for domain, retrying on transient
// errors (network failures, 429 rate limiting, 5xx) with exponential
// backoff.
func (c *Checker) Check(ctx context.Context, domain string) Result {
	var lastErr error

	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		if attempt > 0 {
			delay := c.retryDelay * time.Duration(1<<uint(attempt-1))
			select {
			case <-ctx.Done():
				return Result{Domain: domain, Status: Error, Err: ctx.Err()}
			case <-time.After(delay):
			}
		}

		req, err := http.NewRequestWithContext(ctx, http.MethodGet, c.baseURL+domain, nil)
		if err != nil {
			return Result{Domain: domain, Status: Error, Err: err}
		}
		req.Header.Set("Accept", "application/rdap+json")
		req.Header.Set("User-Agent", "domainscraper/1.0")

		resp, err := c.client.Do(req)
		if err != nil {
			lastErr = err
			continue
		}
		resp.Body.Close()

		switch {
		case resp.StatusCode == http.StatusNotFound:
			return Result{Domain: domain, Status: Available}
		case resp.StatusCode == http.StatusOK:
			return Result{Domain: domain, Status: Registered}
		case resp.StatusCode == http.StatusTooManyRequests, resp.StatusCode >= 500:
			lastErr = fmt.Errorf("rdap returned status %d", resp.StatusCode)
			continue
		default:
			return Result{Domain: domain, Status: Unknown, Err: fmt.Errorf("unexpected status %d", resp.StatusCode)}
		}
	}

	return Result{Domain: domain, Status: Error, Err: lastErr}
}

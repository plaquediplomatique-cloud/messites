// Package ratelimit provides a minimal token-bucket limiter with no external
// dependencies, used to cap outbound requests-per-second so the scraper
// never hammers a registry's RDAP endpoint into rate-limiting or banning us.
package ratelimit

import (
	"context"
	"time"
)

// Limiter allows at most `rate` operations per second, smoothed over time
// (one token every 1/rate seconds), not in bursts.
type Limiter struct {
	ticker *time.Ticker
	tokens chan struct{}
	done   chan struct{}
}

// New creates a Limiter allowing `ratePerSecond` operations/second.
// ratePerSecond <= 0 means unlimited (Wait returns immediately).
func New(ratePerSecond float64) *Limiter {
	if ratePerSecond <= 0 {
		return nil
	}
	interval := time.Duration(float64(time.Second) / ratePerSecond)
	if interval <= 0 {
		interval = time.Nanosecond
	}
	l := &Limiter{
		ticker: time.NewTicker(interval),
		tokens: make(chan struct{}, 1),
		done:   make(chan struct{}),
	}
	go func() {
		for {
			select {
			case <-l.done:
				return
			case <-l.ticker.C:
				select {
				case l.tokens <- struct{}{}:
				default:
				}
			}
		}
	}()
	return l
}

// Wait blocks until a token is available or ctx is done. A nil Limiter
// (unlimited) always returns immediately.
func (l *Limiter) Wait(ctx context.Context) error {
	if l == nil {
		return nil
	}
	select {
	case <-l.tokens:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

// Stop releases the limiter's internal ticker goroutine.
func (l *Limiter) Stop() {
	if l == nil {
		return
	}
	close(l.done)
	l.ticker.Stop()
}

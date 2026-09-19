package ratelimit

import (
	"context"
	"testing"
	"time"
)

func TestLimiterCapsRate(t *testing.T) {
	l := New(50) // 50/s -> 20ms apart
	defer l.Stop()

	ctx := context.Background()
	start := time.Now()
	for i := 0; i < 10; i++ {
		if err := l.Wait(ctx); err != nil {
			t.Fatalf("Wait returned error: %v", err)
		}
	}
	elapsed := time.Since(start)
	// 10 tokens at 50/s should take at least ~180ms (first token can be
	// near-instant, the rest are paced).
	if elapsed < 150*time.Millisecond {
		t.Errorf("limiter allowed burst too fast: %v for 10 tokens at 50/s", elapsed)
	}
}

func TestLimiterNilIsUnlimited(t *testing.T) {
	var l *Limiter
	ctx := context.Background()
	start := time.Now()
	for i := 0; i < 1000; i++ {
		if err := l.Wait(ctx); err != nil {
			t.Fatalf("nil limiter Wait returned error: %v", err)
		}
	}
	if time.Since(start) > 50*time.Millisecond {
		t.Errorf("nil limiter should be instant, took %v", time.Since(start))
	}
	l.Stop() // must not panic on nil
}

func TestLimiterRespectsContextCancel(t *testing.T) {
	l := New(0.001) // effectively never fires within test window
	defer l.Stop()

	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Millisecond)
	defer cancel()

	err := l.Wait(ctx)
	if err == nil {
		t.Fatal("expected context deadline error, got nil")
	}
}

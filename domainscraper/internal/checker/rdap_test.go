package checker

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func newTestChecker(t *testing.T, handler http.HandlerFunc) (*Checker, func()) {
	t.Helper()
	srv := httptest.NewServer(handler)
	c := New(Config{
		Timeout:           2 * time.Second,
		MaxRetries:        2,
		RetryBaseDelay:    10 * time.Millisecond,
		RequestsPerSecond: 1000, // don't let the limiter slow down tests
	})
	c.baseURL = srv.URL + "/domain/"
	return c, func() {
		srv.Close()
		c.Close()
	}
}

func TestCheckAvailable(t *testing.T) {
	c, cleanup := newTestChecker(t, func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
	})
	defer cleanup()

	res := c.Check(context.Background(), "totally-free-domain.com")
	if res.Status != Available {
		t.Fatalf("want Available, got %v (err=%v)", res.Status, res.Err)
	}
}

func TestCheckRegistered(t *testing.T) {
	c, cleanup := newTestChecker(t, func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"ldhName":"example.com"}`))
	})
	defer cleanup()

	res := c.Check(context.Background(), "example.com")
	if res.Status != Registered {
		t.Fatalf("want Registered, got %v (err=%v)", res.Status, res.Err)
	}
}

func TestCheckRetriesOn429ThenSucceeds(t *testing.T) {
	attempts := 0
	c, cleanup := newTestChecker(t, func(w http.ResponseWriter, r *http.Request) {
		attempts++
		if attempts < 2 {
			w.WriteHeader(http.StatusTooManyRequests)
			return
		}
		w.WriteHeader(http.StatusNotFound)
	})
	defer cleanup()

	res := c.Check(context.Background(), "retry-me.com")
	if res.Status != Available {
		t.Fatalf("want Available after retry, got %v (err=%v)", res.Status, res.Err)
	}
	if attempts < 2 {
		t.Fatalf("expected at least 2 attempts, got %d", attempts)
	}
}

func TestCheckGivesUpAfterMaxRetries(t *testing.T) {
	c, cleanup := newTestChecker(t, func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
	})
	defer cleanup()

	res := c.Check(context.Background(), "always-broken.com")
	if res.Status != Error {
		t.Fatalf("want Error, got %v", res.Status)
	}
}

func TestCheckRejectsMalformedDomain(t *testing.T) {
	c, cleanup := newTestChecker(t, func(w http.ResponseWriter, r *http.Request) {
		t.Fatal("handler should never be called for a malformed domain")
	})
	defer cleanup()

	for _, bad := range []string{
		"", "-bad.com", "has space.com", "../../etc/passwd",
		"UPPER.COM", "semi;colon.com", "a" + string(make([]byte, 300)) + ".com",
	} {
		res := c.Check(context.Background(), bad)
		if res.Status != Error {
			t.Errorf("Check(%q) = %v, want Error (malformed input must be rejected)", bad, res.Status)
		}
	}
}

func TestCheckHonorsContextCancellation(t *testing.T) {
	c, cleanup := newTestChecker(t, func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(time.Second)
		w.WriteHeader(http.StatusNotFound)
	})
	defer cleanup()

	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Millisecond)
	defer cancel()

	res := c.Check(ctx, "slow-domain.com")
	if res.Status != Error {
		t.Fatalf("want Error on context deadline, got %v", res.Status)
	}
}

func TestCheckNeverPanics(t *testing.T) {
	// Even if something inside Check were to panic, the recover() guard
	// must turn it into an Error result, never crash the process.
	c, cleanup := newTestChecker(t, func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})
	defer cleanup()
	c.client = nil // force a nil-pointer panic inside checkRDAP

	res := c.Check(context.Background(), "example.com")
	if res.Status != Error {
		t.Fatalf("want Error result from recovered panic, got %v", res.Status)
	}
}

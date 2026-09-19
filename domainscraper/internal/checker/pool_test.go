package checker

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"
)

func TestRunPoolProcessesAllDomains(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
	}))
	defer srv.Close()

	c := New(Config{Timeout: 2 * time.Second, RequestsPerSecond: 1000})
	c.baseURL = srv.URL + "/domain/"
	defer c.Close()

	domains := make([]string, 200)
	for i := range domains {
		domains[i] = fmt.Sprintf("d%d.com", i)
	}

	var mu sync.Mutex
	got := make(map[string]Status)

	RunPool(context.Background(), c, domains, 10, func(r Result) {
		mu.Lock()
		got[r.Domain] = r.Status
		mu.Unlock()
	})

	if len(got) != len(domains) {
		t.Fatalf("expected %d results, got %d", len(domains), len(got))
	}
	for _, d := range domains {
		if got[d] != Available {
			t.Errorf("domain %q: want Available, got %v", d, got[d])
		}
	}
}

func TestRunPoolStopsOnContextCancel(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(50 * time.Millisecond)
		w.WriteHeader(http.StatusNotFound)
	}))
	defer srv.Close()

	c := New(Config{Timeout: 2 * time.Second, RequestsPerSecond: 1000})
	c.baseURL = srv.URL + "/domain/"
	defer c.Close()

	domains := make([]string, 1000)
	for i := range domains {
		domains[i] = fmt.Sprintf("d%d.com", i)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Millisecond)
	defer cancel()

	var count int
	done := make(chan struct{})
	go func() {
		RunPool(ctx, c, domains, 5, func(r Result) { count++ })
		close(done)
	}()

	select {
	case <-done:
	case <-time.After(3 * time.Second):
		t.Fatal("RunPool did not return after context cancellation: goroutine/channel leak")
	}
}

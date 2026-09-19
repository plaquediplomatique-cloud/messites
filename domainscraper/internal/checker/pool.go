package checker

import (
	"context"
	"sync"
)

// RunPool checks all domains concurrently with the given worker count and
// invokes onResult for every completed check (called from a single
// goroutine, so it's safe to write to files/stdout without extra locking).
func RunPool(ctx context.Context, c *Checker, domains []string, workers int, onResult func(Result)) {
	if workers < 1 {
		workers = 1
	}

	jobs := make(chan string)
	results := make(chan Result)

	var wg sync.WaitGroup
	wg.Add(workers)
	for i := 0; i < workers; i++ {
		go func() {
			defer wg.Done()
			for domain := range jobs {
				select {
				case <-ctx.Done():
					return
				default:
				}
				results <- c.Check(ctx, domain)
			}
		}()
	}

	go func() {
		defer close(jobs)
		for _, d := range domains {
			select {
			case <-ctx.Done():
				return
			case jobs <- d:
			}
		}
	}()

	go func() {
		wg.Wait()
		close(results)
	}()

	for r := range results {
		onResult(r)
	}
}

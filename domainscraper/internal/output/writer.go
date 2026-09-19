// Package output writes scan results to CSV incrementally, flushing after
// every row so partial results survive an interrupted run.
package output

import (
	"encoding/csv"
	"fmt"
	"os"

	"domainscraper/internal/checker"
)

// CSVWriter writes checker.Result rows to a CSV file as they arrive.
type CSVWriter struct {
	file *os.File
	w    *csv.Writer
}

// NewCSV creates (or truncates) path and writes the header row.
func NewCSV(path string) (*CSVWriter, error) {
	f, err := os.Create(path)
	if err != nil {
		return nil, fmt.Errorf("create output file: %w", err)
	}
	w := csv.NewWriter(f)
	if err := w.Write([]string{"domain", "status"}); err != nil {
		f.Close()
		return nil, err
	}
	w.Flush()
	return &CSVWriter{file: f, w: w}, nil
}

// Write appends one result and flushes to disk immediately.
func (c *CSVWriter) Write(r checker.Result) error {
	if err := c.w.Write([]string{r.Domain, r.Status.String()}); err != nil {
		return err
	}
	c.w.Flush()
	return c.w.Error()
}

// Close flushes and closes the underlying file.
func (c *CSVWriter) Close() error {
	c.w.Flush()
	return c.file.Close()
}

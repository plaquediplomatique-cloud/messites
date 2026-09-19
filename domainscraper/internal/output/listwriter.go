package output

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
)

// ListWriter appends plain domain names, one per line, flushing after every
// write so the file is always complete on disk even if the process is
// interrupted.
type ListWriter struct {
	file *os.File
	w    *bufio.Writer
}

// NewList creates (or truncates) path, creating any missing parent
// directories first.
func NewList(path string) (*ListWriter, error) {
	if dir := filepath.Dir(path); dir != "." && dir != "" {
		if err := os.MkdirAll(dir, 0o755); err != nil {
			return nil, fmt.Errorf("create output directory %q: %w", dir, err)
		}
	}
	f, err := os.Create(path)
	if err != nil {
		return nil, fmt.Errorf("create output file: %w", err)
	}
	return &ListWriter{file: f, w: bufio.NewWriter(f)}, nil
}

// WriteDomain appends one domain name followed by a newline, flushed
// immediately.
func (l *ListWriter) WriteDomain(domain string) error {
	if _, err := l.w.WriteString(domain + "\n"); err != nil {
		return err
	}
	return l.w.Flush()
}

// Close flushes and closes the underlying file.
func (l *ListWriter) Close() error {
	if err := l.w.Flush(); err != nil {
		l.file.Close()
		return err
	}
	return l.file.Close()
}

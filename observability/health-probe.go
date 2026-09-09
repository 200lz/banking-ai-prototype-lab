// A fixed local readiness check; it accepts no arguments or remote destinations.
package main

import (
	"net/http"
	"os"
	"time"
)

func main() {
	client := http.Client{Timeout: 1500 * time.Millisecond}
	response, err := client.Get("http://127.0.0.1:13133/")
	if err != nil {
		os.Exit(1)
	}
	response.Body.Close()
	if response.StatusCode != http.StatusOK {
		os.Exit(1)
	}
}

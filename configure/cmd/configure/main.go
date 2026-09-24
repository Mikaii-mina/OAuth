package main

import (
	"github.com/cyllective/oauth-labs/configure/internal/db"
	"github.com/cyllective/oauth-labs/configure/internal/lab00"
)

func main() {
	lab00.Configure()
	db.Configure()
}

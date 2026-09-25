package main

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"

	"github.com/cyllective/oauth-labs/configure/internal/constants"
	"github.com/cyllective/oauth-labs/configure/internal/db"
	"github.com/cyllective/oauth-labs/configure/internal/lab00"
)

func main() {
	paths, err := filepath.Glob(filepath.Join(constants.RootDir, "lab[0-9][0-9]"))
	if err != nil {
		panic(err)
	}
	var labs []string
	valid := regexp.MustCompile(`^lab[0-9]{2}$`)
	for _, path := range paths {
		name := filepath.Base(path)
		if !valid.MatchString(name) {
			continue
		}
		for _, component := range []string{"client", "server"} {
			if _, err := os.Stat(filepath.Join(path, component, "go.mod")); err != nil {
				panic(fmt.Errorf("%s missing %s/go.mod: %w", name, component, err))
			}
		}
		labs = append(labs, name)
	}
	sort.Strings(labs)
	if len(labs) == 0 || labs[0] != "lab00" {
		panic("lab00 baseline is required")
	}
	for _, name := range labs {
		lab00.Configure(strings.TrimPrefix(name, "lab"))
	}
	db.Configure(labs)
}

package lab00

import (
	"strings"
	"testing"
)

func TestNumberedConfig(t *testing.T) {
	client := numberedConfig(clientConfigTemplate, "01")
	server := numberedConfig(serverConfigTemplate, "01")
	for _, expected := range []string{"client01", "client-01.oauth.labs", "server-01.oauth.labs"} {
		if !strings.Contains(client, expected) {
			t.Errorf("client config missing %q", expected)
		}
	}
	for _, expected := range []string{"server01", "server-01.oauth.labs"} {
		if !strings.Contains(server, expected) {
			t.Errorf("server config missing %q", expected)
		}
	}
	if strings.Contains(client, "client00") || strings.Contains(server, "server00") {
		t.Fatal("baseline database name leaked into new lab")
	}
	if !strings.Contains(client, "max_age: 80400") {
		t.Fatal("unrelated numeric configuration was changed")
	}
}

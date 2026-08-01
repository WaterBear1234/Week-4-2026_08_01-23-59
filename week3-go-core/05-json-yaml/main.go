// A struct tagged for both json and yaml, marshaled to both formats,
// unmarshaled back — then a deliberately mismatched tag to show Go's
// silent-zero-value behavior on unknown/missing fields.
package main

import (
	"bytes"
	"encoding/json"
	"fmt"

	"github.com/goccy/go-yaml"
)

type Config struct {
	Host  string `json:"host" yaml:"host"`
	Port  int    `json:"port" yaml:"port"`
	Debug bool   `json:"debug" yaml:"debug"`
}

func main() {
	original := Config{Host: "localhost", Port: 8080, Debug: true}

	fmt.Println("-- marshal to JSON --")
	jsonBytes, _ := json.MarshalIndent(original, "", "  ")
	fmt.Println(string(jsonBytes))

	fmt.Println("-- marshal to YAML --")
	yamlBytes, _ := yaml.Marshal(original)
	fmt.Print(string(yamlBytes))

	fmt.Println("-- unmarshal both back --")
	var fromJSON, fromYAML Config
	json.Unmarshal(jsonBytes, &fromJSON)
	yaml.Unmarshal(yamlBytes, &fromYAML)
	fmt.Printf("from JSON: %+v\n", fromJSON)
	fmt.Printf("from YAML: %+v\n", fromYAML)

	fmt.Println("\n-- deliberately broken tag: 'port' -> 'prt' in the source JSON --")
	brokenJSON := []byte(`{"host":"localhost","prt":8080,"debug":true}`)
	var broken Config
	err := json.Unmarshal(brokenJSON, &broken)
	fmt.Printf("err: %v\n", err)        // nil — no error at all
	fmt.Printf("result: %+v\n", broken) // Port silently comes back 0
	fmt.Println("Go does NOT error on unknown/missing JSON fields by default.")

	fmt.Println("\n-- fix: reject unknown fields explicitly --")
	dec := json.NewDecoder(bytes.NewReader(brokenJSON))
	dec.DisallowUnknownFields()
	var strict Config
	err = dec.Decode(&strict)
	fmt.Printf("err: %v\n", err) // now it errors, because "prt" isn't a known field
}

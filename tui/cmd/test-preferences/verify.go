//go:build ignore
// +build ignore

package main

import (
	"fmt"
	"log"
	"os"

	"github.com/kairin/dotfiles-installer/internal/config"
	"github.com/kairin/dotfiles-installer/internal/registry"
)

func main() {
	store := config.NewPreferenceStore()

	// Save a preference
	err := store.SetToolMethod("feh", registry.MethodSource)
	if err != nil {
		log.Fatalf("Failed to save: %v", err)
	}

	// Read and print the file contents
	data, err := os.ReadFile(store.GetPath())
	if err != nil {
		log.Fatalf("Failed to read file: %v", err)
	}

	fmt.Println("Preference file contents:")
	fmt.Println(string(data))
}

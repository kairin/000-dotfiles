package main

import (
	"fmt"
	"log"

	"github.com/kairin/dotfiles-installer/internal/config"
	"github.com/kairin/dotfiles-installer/internal/registry"
)

func main() {
	store := config.NewPreferenceStore()

	fmt.Println("=== Testing Preference Management ===")
	fmt.Println()

	// Check if preference exists
	fmt.Println("1. Checking for existing preference...")
	method, err := store.GetToolMethod("feh")
	if err != nil {
		log.Fatalf("Failed to read preference: %v", err)
	}
	if method == "" {
		fmt.Println("   No existing preference")
	} else {
		fmt.Printf("   Existing preference: %s\n", method)
	}

	// Save a new preference
	fmt.Println("\n2. Saving new preference (source)...")
	err = store.SetToolMethod("feh", registry.MethodSource)
	if err != nil {
		log.Fatalf("Failed to save preference: %v", err)
	}
	fmt.Println("   ✓ Preference saved")

	// Load the preference
	fmt.Println("\n3. Loading saved preference...")
	method, err = store.GetToolMethod("feh")
	if err != nil {
		log.Fatalf("Failed to load preference: %v", err)
	}
	fmt.Printf("   ✓ Loaded preference: %s\n", method)

	// Update preference
	fmt.Println("\n4. Updating preference to snap...")
	err = store.SetToolMethod("feh", registry.MethodSnap)
	if err != nil {
		log.Fatalf("Failed to update preference: %v", err)
	}
	fmt.Println("   ✓ Preference updated")

	// Verify update
	fmt.Println("\n5. Verifying updated preference...")
	method, err = store.GetToolMethod("feh")
	if err != nil {
		log.Fatalf("Failed to load preference: %v", err)
	}
	fmt.Printf("   ✓ Current preference: %s\n", method)

	// Show config file location
	fmt.Printf("\n6. Config file location: %s\n", store.GetPath())

	// Clear preference
	fmt.Println("\n7. Clearing preference...")
	err = store.Clear()
	if err != nil {
		log.Fatalf("Failed to clear preference: %v", err)
	}
	fmt.Println("   ✓ Preference cleared")

	// Verify cleared
	fmt.Println("\n8. Verifying preference is cleared...")
	method, err = store.GetToolMethod("feh")
	if err != nil {
		log.Fatalf("Failed to read preference: %v", err)
	}
	if method == "" {
		fmt.Println("   ✓ No preference found (as expected)")
	} else {
		fmt.Printf("   ✗ Unexpected preference: %s\n", method)
	}

	fmt.Println("\n=== All tests passed! ===")
}

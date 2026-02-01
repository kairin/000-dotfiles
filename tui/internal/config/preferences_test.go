package config

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/kairin/dotfiles-installer/internal/registry"
)

func TestPreferenceStore_SaveAndLoad(t *testing.T) {
	// Create temp directory for test
	tmpDir := t.TempDir()
	testPath := filepath.Join(tmpDir, "preferences.json")

	store := NewPreferenceStoreWithPath(testPath)

	// Save preference
	err := store.SetToolMethod("feh", registry.MethodSource)
	if err != nil {
		t.Fatalf("Failed to save preference: %v", err)
	}

	// Verify file exists
	if !store.Exists() {
		t.Error("Preference file should exist after save")
	}

	// Load preference
	method, err := store.GetToolMethod("feh")
	if err != nil {
		t.Fatalf("Failed to load preference: %v", err)
	}

	if method != registry.MethodSource {
		t.Errorf("Expected MethodSource, got %s", method)
	}
}

func TestPreferenceStore_LoadNonExistent(t *testing.T) {
	tmpDir := t.TempDir()
	testPath := filepath.Join(tmpDir, "nonexistent.json")

	store := NewPreferenceStoreWithPath(testPath)

	// Load should succeed with empty preferences
	prefs, err := store.Load()
	if err != nil {
		t.Fatalf("Load should not fail for non-existent file: %v", err)
	}

	if prefs.ToolMethods == nil || len(prefs.ToolMethods) != 0 {
		t.Error("Expected empty tool methods for non-existent file")
	}
}

func TestPreferenceStore_GetToolMethod_Empty(t *testing.T) {
	tmpDir := t.TempDir()
	testPath := filepath.Join(tmpDir, "empty.json")

	store := NewPreferenceStoreWithPath(testPath)

	method, err := store.GetToolMethod("feh")
	if err != nil {
		t.Fatalf("GetToolMethod failed: %v", err)
	}

	if method != "" {
		t.Errorf("Expected empty method, got %s", method)
	}
}

func TestPreferenceStore_Clear(t *testing.T) {
	tmpDir := t.TempDir()
	testPath := filepath.Join(tmpDir, "clear.json")

	store := NewPreferenceStoreWithPath(testPath)

	// Save preference
	err := store.SetToolMethod("feh", registry.MethodSource)
	if err != nil {
		t.Fatalf("Failed to save: %v", err)
	}

	// Clear
	err = store.Clear()
	if err != nil {
		t.Fatalf("Failed to clear: %v", err)
	}

	// Verify file is gone
	if store.Exists() {
		t.Error("Preference file should not exist after clear")
	}

	// Clear again should not error
	err = store.Clear()
	if err != nil {
		t.Fatalf("Clear should not fail on non-existent file: %v", err)
	}
}

func TestPreferenceStore_UpdateExisting(t *testing.T) {
	tmpDir := t.TempDir()
	testPath := filepath.Join(tmpDir, "update.json")

	store := NewPreferenceStoreWithPath(testPath)

	// Save source preference
	err := store.SetToolMethod("feh", registry.MethodSource)
	if err != nil {
		t.Fatalf("Failed to save initial: %v", err)
	}

	// Load first timestamp
	prefs1, _ := store.Load()

	// Update to tarball to validate updates overwrite previous value
	err = store.SetToolMethod("feh", registry.MethodTarball)
	if err != nil {
		t.Fatalf("Failed to update: %v", err)
	}

	// Load and verify
	method, err := store.GetToolMethod("feh")
	if err != nil {
		t.Fatalf("Failed to load: %v", err)
	}

	if method != registry.MethodTarball {
		t.Errorf("Expected MethodTarball after update, got %s", method)
	}

	// Verify timestamp was updated
	prefs2, _ := store.Load()
	if !prefs2.LastModified.After(prefs1.LastModified) {
		t.Error("LastModified should be updated on save")
	}
}

func TestPreferenceStore_JSONFormat(t *testing.T) {
	tmpDir := t.TempDir()
	testPath := filepath.Join(tmpDir, "format.json")

	store := NewPreferenceStoreWithPath(testPath)

	// Save preference
	err := store.SetToolMethod("feh", registry.MethodSource)
	if err != nil {
		t.Fatalf("Failed to save: %v", err)
	}

	// Read raw file
	data, err := os.ReadFile(testPath)
	if err != nil {
		t.Fatalf("Failed to read file: %v", err)
	}

	// Verify JSON contains expected fields
	content := string(data)
	if !contains(content, "tool_methods") {
		t.Error("JSON should contain tool_methods field")
	}

	if !contains(content, "feh") {
		t.Error("JSON should contain tool ID")
	}

	if !contains(content, "source") {
		t.Error("JSON should contain method value")
	}

	if !contains(content, "feh") {
		t.Error("JSON should contain tool id")
	}

	if !contains(content, "last_modified") {
		t.Error("JSON should contain last_modified field")
	}
}

func TestPreferenceStore_GetPath(t *testing.T) {
	tmpDir := t.TempDir()
	testPath := filepath.Join(tmpDir, "test.json")

	store := NewPreferenceStoreWithPath(testPath)

	if store.GetPath() != testPath {
		t.Errorf("GetPath() = %s, expected %s", store.GetPath(), testPath)
	}
}

func TestNewPreferenceStore_DefaultPath(t *testing.T) {
	store := NewPreferenceStore()

	path := store.GetPath()

	// Verify path contains expected components
	if !contains(path, ".config") {
		t.Error("Default path should contain .config")
	}

	if !contains(path, "dotfiles-installer") {
		t.Error("Default path should contain dotfiles-installer")
	}

	if !contains(path, "preferences.json") {
		t.Error("Default path should contain preferences.json")
	}
}

// Helper function
func contains(s, substr string) bool {
	return len(s) > 0 && len(substr) > 0 && (s == substr || len(s) >= len(substr) && s[:len(substr)] == substr || findSubstring(s, substr))
}

func findSubstring(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
